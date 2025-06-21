from __future__ import annotations


from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from os import linesep
from typing import Generator, SupportsIndex, Self

import pygame

import src.rules
import src.theme
import src.algebra
import src.material


Piece = src.material.Piece | None


class Board(list[Piece], src.theme.Drawable):

	default = "♜♞♝♛♚♝♞♜/♟♟♟♟♟♟♟♟/8/8/8/8/♙♙♙♙♙♙♙♙/♖♘♗♕♔♗♘♖"


	def __init__(self,
		pieces: list[Piece] | None = None,
	):
		if pieces is None:
			pieces = [None for _ in src.algebra.Square]

		super().__init__(pieces)

		for index, piece in enumerate(pieces):
			square = src.algebra.Square(index)

			self[square] = piece

		self.selected: src.material.Piece | None = None

	def __repr__(self) -> str:
		return self.forsyth_edwards

	def __setitem__(self, key: src.algebra.Square, value: src.material.Piece | None):
		if value is not None:
			value.square = key

		super().__setitem__(key, value)

	def __delitem__(self, key: src.algebra.Square):
		super().__setitem__(key, None)


	@classmethod
	def from_forsyth_edwards(cls,
		notation: str | None = None,
	) -> Self:
		if notation is None:
			notation = cls.default

		board = cls()

		index = 0

		for row in notation.split("/"):
			for char in row:
				if piece_found := not char.isdigit():
					square = src.algebra.Square(index)
					board[square] = src.material.Piece.from_forsyth_edwards(board, char)  # type: ignore  # HACK

				index += 1 if piece_found else int(char)

		return board


	@property
	def forsyth_edwards(self) -> str:
		notation = ""

		for index, piece in enumerate(self):
			empty = 0
			square = src.algebra.Square(index)

			if piece is None:
				empty += 1
				continue

			if empty > 0:
				notation += str(empty)
				empty = 0

			if square % 8 == 0:
				notation += "/"

			notation += repr(piece)

		return notation

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
		#	center = pygame.Vector2(
		#		src.theme.RESOLUTION // 2,
		#		src.theme.RESOLUTION // 2,
		#	)
		)


	def update(self, square: src.algebra.Square,
		piece: src.material.Piece | None = None,
	):
	#	other = self[square]

		if piece is not None: piece.square = square
	#	if other is not None: other.square = None

	def move(self,
		source: src.algebra.Square,
		target: src.algebra.Square,
	):
		if target != source and (piece := self[source]) is not None:
			piece(target)

	def draw(self, screen: pygame.Surface):
		for file in src.algebra.File:
			file.draw(screen)
			file.ward(screen)

		for rank in src.algebra.Rank:
			rank.draw(screen)
			rank.ward(screen)

		for square in src.algebra.Square:
			square.draw(screen)

	#	surf = src.theme.Main.CORNER.value

	#	rect = src.theme.BOARD_OFFSET
	#	size = src.theme.BOARD + rect

	#	screen.blit(surf, surf.get_rect(bottom = rect.y, right = rect.x))
	#	screen.blit(surf, surf.get_rect(   top = size.y, right = rect.x))
	#	screen.blit(surf, surf.get_rect(   top = size.y,  left = size.x))
	#	screen.blit(surf, surf.get_rect(bottom = rect.y,  left = size.x))

		super().draw(screen,
			special_flags = pygame.BLEND_RGBA_MULT,
		)


class Side(
	defaultdict[
		type[src.material.Piece],
		set [src.material.Piece],
	]
):

	last_type: type[src.material.Piece]


	def __init__(self, game: Game, color: src.algebra.Color):
		super().__init__(set)

		self.game = game
		self.color = color

	#	self[src.material.King  ] = []
	#	self[src.material.Queen ] = []
	#	self[src.material.Pawn  ] = []
	#	self[src.material.Rook  ] = []
	#	self[src.material.Bishop] = []
	#	self[src.material.Knight] = []

		self. king: src.material.King  | None = None
		self.arook: src.material.Rook  | None = None
		self.hrook: src.material.Rook  | None = None

		self.ghost: src.material.Ghost | None = None

	def __iter__(self) -> Generator[src.material.Piece]:
		for pieces in self.values():
			for piece in pieces:
				yield piece

	def __bool__(self) -> bool:
		return self is self.game.current


	@classmethod
	def from_forsyth_edwards(cls, game: Game, color: src.algebra.Color, castling: str) -> Self:
		side = cls(game, color)

		if color:
			if "k" in castling: side.arook = game[src.algebra.Square.H8]  # type: ignore
			if "q" in castling: side.hrook = game[src.algebra.Square.A8]  # type: ignore

		else:
			if "K" in castling: side.arook = game[src.algebra.Square.H1]  # type: ignore
			if "Q" in castling: side.hrook = game[src.algebra.Square.A1]  # type: ignore

		return side


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self)

	@property
	def targets(self) -> src.algebra.Squares:
		return src.algebra.Squares.union(*(piece.targets for piece in self))

	@property
	def other(self) -> Side:
		return self.game.white if self.color else self.game.black

	@property
	def history(self) -> History:
		return History(self.game.history[bool(self.color)::2])

	@property
	def forsyth_edwards(self) -> str:
		notation = ""

		if self.king is not None and not self.king.moved:
			if self.arook is not None and not self.arook.moved: notation += "k" if self.color else "K"
			if self.hrook is not None and not self.hrook.moved: notation += "q" if self.color else "Q"

		return notation


	def sync(self, piece: src.material.Piece):
		match piece:
			case src.material.King(): self.king = piece
			case src.material.Rook():
				match piece.square * self.color:
					case src.algebra.Square.A8: self.arook = piece
					case src.algebra.Square.H8: self.hrook = piece

			case src.material.Ghost():
				self.ghost = piece

	def add(self, piece: src.material.Piece | None):
		if piece is None or piece.color != self.color:
			return

		self.last_type = type(piece)
		self[piece.__class__].add(piece)

		self.sync(piece)

	def discard(self, piece: src.material.Piece | None):
		if piece is None or piece.color != self.color:
			return

		self[piece.__class__].discard(piece)


class History(list[src.rules.Move | None]):

	def __repr__(self) -> str:
		return self.window()


	@classmethod
	def from_forsyth_edwards(cls, full_clock: str, turn: str) -> Self:
		total_moves = 2 * (int(full_clock) - 1) + (1 if turn == "b" else 0)

		return cls([None] * total_moves)


	@property
	def last(self) -> src.rules.Move | None:
		return self.get(-1)

	@property
	def half_clock(self) -> int:
		for index, rule in enumerate(reversed(self)):
			if rule is not None and (isinstance(rule, src.rules.Capt) or isinstance(rule.piece, src.material.Pawn)):
				return index

		return len(self)

	@property
	def full_clock(self) -> int:
		return len(self) // 2 + 1

	@property
	def forsyth_edwards(self) -> str:
		return f"{self.half_clock} {self.full_clock}"


	def get(self, index: SupportsIndex,
		default: src.rules.Move | None = None,
	) -> src.rules.Move | None:
		try: return self[index]
		except IndexError: return default

	def window(self,
		size: int | None = None,
	) -> str:
		notation = ""

		if size == None:
			size = len(self)

		for index, rule in enumerate(self[-size:],
			start = len(self) - size,
		):
			if rule is None: notation += f"{index}         "
			else:            notation += f"{index} {rule}"

			notation += linesep

		return notation


class Game(Board):

	testing = bool()
	default = f"{Board.default} w KQkq - 0 1"


	def __init__(self,
		pieces: list[Piece] | None = None,
	):
		self.black = Side(self, src.algebra.Color.BLACK)
		self.white = Side(self, src.algebra.Color.WHITE)

		super().__init__(pieces)

		self.history = History()
		self.promoted: src.rules.Promotion | None = None

	def __next__(self) -> Side:
		return self.current

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())

	def __setitem__(self, key: src.algebra.Square, value: src.material.Piece | None):
		super().__setitem__(key, value)

		if not self.testing:
			self.black.add(value)
			self.white.add(value)

	def __delitem__(self, key: src.algebra.Square):
		value = self[key]

		if not self.testing:
			self.black.discard(value)
			self.white.discard(value)

		super().__delitem__(key)


	def __iadd__(self, rule: src.rules.Move) -> Self:
		self.history.append(rule())

		if (ghost := self.current.ghost) is not None:
			if self[ghost.square] is ghost:
				del self[ghost.square]

		return self


	@classmethod
	def from_forsyth_edwards(cls,
		notation: str | None = None,
	) -> Self:
		if notation is None:
			notation = cls.default

		board, turn, castling, enpassant, _, full = notation.split()

		game = cls()

		game.white = Side.from_forsyth_edwards(game, src.algebra.Color.WHITE, castling)
		game.black = Side.from_forsyth_edwards(game, src.algebra.Color.BLACK, castling)

		if turn == "b":
			game.history.append(None)

		index = 0

		for row in board.split("/"):
			for char in row:
				if piece_found := not char.isdigit():
					square = src.algebra.Square(index)
					game[square] = src.material.Piece.from_forsyth_edwards(game, char)

				index += 1 if piece_found else int(char)

		if enpassant != "-":
			square = src.algebra.Square.from_algebraic(enpassant)
			color = game.current.other.color
			game.current.other.ghost = game[square] = src.material.Ghost(game, color)

		game.history = History.from_forsyth_edwards(full, turn)

		return game


	@property
	def forsyth_edwards(self) -> str:
		notation = super().forsyth_edwards

		current = "b" if self.current.color else "w"
		enpassant = repr(self.current.ghost.square) if self.current.ghost is not None else "-"

		return " ".join([notation, current, enpassant, self.castling, self.history.forsyth_edwards])

	@property
	def castling(self) -> str:
		castling  = self.white.forsyth_edwards + self.black.forsyth_edwards

		return castling if castling else "-"

	@property
	def current(self) -> Side:
		return self.black if len(self.history) & 1 else self.white

	@property
	@contextmanager
	def dry_run(self) -> Generator[Self]:
		original, self.testing = self.testing, True; yield self
		self.testing = original


	def draw(self, screen: pygame.Surface):
		super().draw(screen)

		if self.selected is not None:
			if self.promoted is not None and self.selected is self.promoted.piece:
				self.promoted.highlight(screen)

			else:
				for square in self.selected.squares:
					square.highlight(screen)

		for piece in self:
			if piece is not None:
				if piece is self.selected:
					if self.promoted is not None and piece is self.promoted.piece:
						screen.blit(self.promoted.officer.surf(self.promoted.piece.color), self.promoted.piece.rect)

					else:
						piece.highlight(screen)

				else:
					piece.draw(screen)

				piece.ghost = piece.__class__.ghost  # HACK

	def clicked(self, event: pygame.event.Event) -> bool:
		for square in src.algebra.Square:
			if not square.clicked(event):
				continue

			if self.promoted is not None:
				if square == self.promoted.source:
					self.promoted.officer = next(self.promoted.officers)

				else:
					if square == self.promoted.target:
						self += self.promoted

					self.selected = None
					self.promoted = None

				return True

			if self.selected:
				if (rule := self.selected.squares.get(square)) is not None:
					if isinstance(rule, src.rules.Promotion):
						self.promoted = rule

					else:
						self += rule
						self.selected = None

				else:
					self.selected = None

				return True

			if (piece := self[square]) is not None and piece.side:
				self.selected = piece

			return True

		return False
