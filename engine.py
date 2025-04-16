from __future__ import annotations


from collections import defaultdict
from datetime import datetime
from typing import Generator, Iterable, SupportsIndex, Self, cast

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

		self.selected: chess.material.Piece | None = None

	def __repr__(self) -> str:
		return self.forsyth_edwards

	def __setitem__(self, key: chess.algebra.square | slice,
		value: chess.material.Piece | None | Iterable[chess.material.Piece | None],
	):
		if isinstance(key, chess.algebra.square): key = slice(int(key), int(key) + 1, +1)
		if isinstance(value, chess.material.Piece | None): value = [value]

		for index, piece in zip(range(*key.indices(len(self))), value):
			self.update(chess.algebra.Square(index), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.algebra.square | slice):
		if isinstance(key, chess.algebra.square): key = slice(int(key), int(key) + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


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


	def add(self, piece: chess.material.Piece | None):
		if piece is None or piece.color != self.color:
			return

		self.last_type = type(piece)
		self[piece.__class__].append(piece)
		self.game[piece.square] = piece

		match piece:
			case chess.material.King(): self.king = piece
			case chess.material.Rook():
				match piece.square * self.color:
					case chess.algebra.Square.A8: self.arook = piece
					case chess.algebra.Square.H8: self.hrook = piece
			case chess.material.Ghost(): self.ghost = piece

	def pop(self,
		piece_type: type[chess.material.Piece] | None = None,
	) -> chess.material.Piece | None:
		if piece_type is None:
			piece_type = self.last_type

		try:
			return self[piece_type].pop()

		except IndexError:
			return


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

	def __init__(self,
		pieces: list[Piece] | None = None,
	):
		super().__init__(pieces)

		self.black = Side(self, chess.algebra.Color.BLACK)
		self.white = Side(self, chess.algebra.Color.WHITE)

		for piece in self:
			self.black.add(piece)
			self.white.add(piece)

		self.history = History()
		self.promoted: chess.rules.Promotion | None = None

	def __next__(self) -> Side:
		return self.current

	def __repr__(self) -> str:
		...  # TODO: FEN (full)

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())

	def __iadd__(self, rule: chess.rules.Move) -> Self:
		self.history.append(rule())

		if (ghost := self.current.ghost) is not None:
			del self[ghost.square]

		return self


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
