from __future__ import annotations


from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, SupportsIndex, Self

import pygame

import chess.rules
import chess.theme
import chess.algebra
import chess.material


Piece = chess.material.Piece | None


class Board(list[Piece], chess.theme.Drawable):

	def __init__(self,
		pieces: list[Piece] | None = None,
	):
		if pieces is None:
			pieces = [None for _ in chess.algebra.Square]

		super().__init__(pieces)

		for index, piece in enumerate(pieces):
			square = chess.algebra.Square(index)

			self[square] = piece

		self.selected: chess.material.Piece | None = None

	def __repr__(self) -> str:
		return self.forsyth_edwards

	def __setitem__(self, key: chess.algebra.Square, value: chess.material.Piece | None):
		if value is not None:
			value.square = key

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.algebra.Square):
		self[key] = None


	@property
	def forsyth_edwards(self) -> str:
		notation = ""

		for index, piece in enumerate(self):
			empty = 0
			square = chess.algebra.Square(index)

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
		#		chess.theme.RESOLUTION // 2,
		#		chess.theme.RESOLUTION // 2,
		#	)
		)

	@property
	@contextmanager
	def dry_run(self):
		original, self.testing = self.testing, True; yield
		self.testing = original


	def update(self, square: chess.algebra.Square,
		piece: chess.material.Piece | None = None,
	):
	#	other = self[square]

		if piece is not None: piece.square = square
	#	if other is not None: other.square = None

	def move(self,
		source: chess.algebra.Square,
		target: chess.algebra.Square,
	):
		if target != source and (piece := self[source]) is not None:
			piece(target)


class Side(
	defaultdict[
		type[chess.material.Piece],
		list[chess.material.Piece],
	]
):

	last_type: type[chess.material.Piece]


	def __init__(self, game: Game, color: chess.algebra.Color):
		super().__init__(list)

		self.game = game
		self.color = color

	#	self[chess.material.King  ] = []
	#	self[chess.material.Queen ] = []
	#	self[chess.material.Pawn  ] = []
	#	self[chess.material.Rook  ] = []
	#	self[chess.material.Bishop] = []
	#	self[chess.material.Knight] = []

		self. king: chess.material.King  | None = None
		self.arook: chess.material.Rook  | None = None
		self.hrook: chess.material.Rook  | None = None

		self.ghost: chess.material.Ghost | None = None

	def __iter__(self) -> Generator[chess.material.Piece]:
		for piece_type, pieces in self.items():
			for piece in pieces:
				yield piece

	def __bool__(self) -> bool:
		return self is self.game.current


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self)

	@property
	def targets(self) -> chess.algebra.Squares:
		return chess.algebra.Squares.union(*(piece.targets for piece in self))

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


	def sync(self,
		piece: chess.material.Piece | None = None,
	):
		match piece:
			case chess.material.King(): self.king = piece
			case chess.material.Rook():
				match piece.square * self.color:
					case chess.algebra.Square.A8: self.arook = piece
					case chess.algebra.Square.H8: self.hrook = piece

			case chess.material.Ghost():
				self.ghost = piece

	def append(self, piece: chess.material.Piece | None):
		if piece is None or piece.color != self.color:
			return

		self.last_type = type(piece)
		self[piece.__class__].append(piece)

		self.sync(piece)

	def remove(self, piece: chess.material.Piece | None):
		if piece is None or piece.color != self.color:
			return

		try:
			self[piece.__class__].remove(piece)

		except ValueError:
			return

		self.sync()


class History(list[chess.rules.Move]):

	@property
	def last(self) -> chess.rules.Move | None:
		return self.get(-1)

	@property
	def half_clock(self) -> int:
		for index, rule in enumerate(reversed(self)):
			if isinstance(rule, chess.rules.Capt) or isinstance(rule.piece, chess.material.Pawn):
				return index

		return len(self)

	@property
	def full_clock(self) -> int:
		return len(self) // 2 + 1


	def get(self, index: SupportsIndex,
		default: chess.rules.Move | None = None,
	) -> chess.rules.Move | None:
		try: return self[index]
		except IndexError: return default


class Game(Board):

	testing = bool()


	def __init__(self,
		pieces: list[Piece] | None = None,
	):
		self.black = Side(self, chess.algebra.Color.BLACK)
		self.white = Side(self, chess.algebra.Color.WHITE)

		super().__init__(pieces)

		self.history = History()
		self.promoted: chess.rules.Promotion | None = None

	def __next__(self) -> Side:
		return self.current

	def __repr__(self) -> str:
		...  # TODO: FEN (full)

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())

	def __setitem__(self, key: chess.algebra.Square, value: chess.material.Piece | None):
		super().__setitem__(key, value)

		if not self.testing:
			self.black.append(value)
			self.white.append(value)

	def __delitem__(self, key: chess.algebra.Square):
		value = self[key]

		super().__delitem__(key)

		if not self.testing:
			self.black.remove(value)
			self.white.remove(value)

	def __iadd__(self, rule: chess.rules.Move) -> Self:
		self.history.append(rule())

		if (ghost := self.current.ghost) is not None:
			del self[ghost.square]

		return self


	@classmethod
	def from_forsyth_edwards(cls,
		notation: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
	) -> Self:
		game = cls()
		board, turn, castling, enpassant, half, full = notation.split()

		index = 0

		for row in board.split("/"):
			for char in row:
				if char.isdigit():
					index += int(char)

				else:
					square = chess.algebra.Square(index)
					color = chess.algebra.Color.BLACK if char.islower() else chess.algebra.Color.WHITE
					piece_types = {
						"p": chess.material.Pawn,
						"r": chess.material.Rook,
						"n": chess.material.Knight,
						"b": chess.material.Bishop,
						"q": chess.material.Queen,
						"k": chess.material.King,
					}
					piece_type = piece_types[char.lower()]
					piece = piece_type(game, color)
					game[square] = piece

					index += 1

		if turn == "b":
			game.history.append(None)  # type: ignore

		for symbol in castling:
			match symbol:
				case "K": game.white.arook = game[chess.algebra.Square.H1]  # type: ignore
				case "Q": game.white.hrook = game[chess.algebra.Square.A1]  # type: ignore
				case "k": game.black.arook = game[chess.algebra.Square.H8]  # type: ignore
				case "q": game.black.hrook = game[chess.algebra.Square.A8]  # type: ignore

		if enpassant != "-":
			square = chess.algebra.Square.fromnotation(enpassant)
			color = game.current.color
			game.current.ghost = game[square] = chess.material.Ghost(game, color)

		return game


	@property
	def forsyth_edwards(self) -> str:
		notation = super().forsyth_edwards

		current = "b" if self.current.color else "w"
		enpassant = repr(self.current.ghost.square) if self.current.ghost is not None else "-"

		return " ".join(
			[notation, current, enpassant, self.castling,
				str(self.history.half_clock),
				str(self.history.full_clock),
			]
		)


	@property
	def castling(self) -> str:
		castling  = self.white.forsyth_edwards + self.black.forsyth_edwards

		return castling if castling else "-"


	@property
	def current(self) -> Side:
		return self.black if len(self.history) & 1 else self.white


	def draw(self, screen: pygame.Surface):
		for square in chess.algebra.Square:
			square.draw(screen)

		super().draw(screen,
			special_flags = pygame.BLEND_RGBA_MULT,
		)

		if self.selected is not None:
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
		for square in chess.algebra.Square:
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
					if isinstance(rule, chess.rules.Promotion):
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
