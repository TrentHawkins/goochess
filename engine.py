from __future__ import annotations


from datetime import datetime
from itertools import cycle
from pathlib import Path
from typing import SupportsIndex, Iterable, Self, cast

import pygame

import chess.rules
import chess.theme
import chess.algebra
import chess.material


Piece = chess.material.Piece | None


class Board(list[Piece], chess.theme.Drawable):

	def __init__(self):
		super().__init__(None for _ in chess.algebra.Square)

		self.selected: chess.material.Piece | None = None

		self.surf = pygame.transform.smoothscale(pygame.image.load(self.decal).convert(), chess.theme.WINDOW)
		self.rect = self.surf.get_rect(
		#	center = pygame.Vector2(
		#		chess.theme.RESOLUTION // 2,
		#		chess.theme.RESOLUTION // 2,
		#	)
		)

	def __repr__(self) -> str:
		...  # TODO: FEN (part)

	def __setitem__(self, key: chess.algebra.square | slice, value: Piece | Iterable[Piece]):
		if isinstance(key, chess.algebra.square): key = slice(int(key), int(key) + 1, +1)
		if isinstance(value, Piece): value = [value]

		for index, piece in zip(range(*key.indices(len(self))), value):
			self.update(chess.algebra.Square(index), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.algebra.square | slice):
		if isinstance(key, chess.algebra.square): key = slice(int(key), int(key) + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	@property
	def decal(self) -> Path:
		return Path("chess/graphics/board/stone1.jpg")


	def update(self, square: chess.algebra.Square,
		piece: Piece = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None

	def move(self,
		source: chess.algebra.Square,
		target: chess.algebra.Square,
	):
		if target != source and (piece := self[source]) is not None:
			piece(target)


class Side(list[chess.material.Piece]):

	def __init__(self, game: Game, color: chess.algebra.Color):
		self.game = game
		self.color = color

		super().__init__(
			[
				chess.material.Rook  (self),
				chess.material.Knight(self),
				chess.material.Bishop(self),
				chess.material.Queen (self) if self.color else
				chess.material.King  (self),
				chess.material.King  (self) if self.color else
				chess.material.Queen (self),
				chess.material.Bishop(self),
				chess.material.Knight(self),
				chess.material.Rook  (self),

				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
			]
		)

		self.ghost: chess.material.Ghost | None = None

	def __bool__(self) -> bool:
		return self is self.game.current


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)

	@property
	def targets(self) -> chess.algebra.Squares:
		return chess.algebra.Squares.union(*(piece.targets for piece in self))

	@property
	def other(self) -> Side:
		return self.game.white if self.color else self.game.black

	@property
	def history(self) -> list[chess.rules.Base]:
		return self.game.history[bool(self.color)::2]

	@property
	def king(self) -> chess.material.King:
		return cast(chess.material.King,
			self[
				chess.algebra.Square.E8 if self.color else
				chess.algebra.Square.D8
			]
		)

	@property
	def west_rook(self) -> chess.material.Rook:
		return cast(chess.material.Rook,
			self[
				chess.algebra.Square.A8 if self.color else
				chess.algebra.Square.H8
			]
		)

	@property
	def east_rook(self) -> chess.material.Rook:
		return cast(chess.material.Rook,
			self[
				chess.algebra.Square.H8 if self.color else
				chess.algebra.Square.A8
			]
		)


class History(list[chess.rules.Base]):

	@property
	def last(self) -> chess.rules.Base | None:
		return self.get(-1)


	def get(self, index: SupportsIndex,
		default: chess.rules.Base | None = None,
	) -> chess.rules.Base | None:
		try: return self[index]
		except IndexError: return default


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(self, chess.algebra.Color.BLACK)
		self.white = Side(self, chess.algebra.Color.WHITE)

		self[+chess.algebra.Square.A8:+chess.algebra.Square.A6:chess.algebra.Color.BLACK] = self.black
		self[-chess.algebra.Square.A8:-chess.algebra.Square.A6:chess.algebra.Color.WHITE] = self.white

		self.history = History()
		self.promoting: chess.rules.Promote | None = None

	def __next__(self) -> Side:
		return self.current

	def __repr__(self) -> str:
		...  # TODO: FEN (full)

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())

	def __iadd__(self, rule: chess.rules.Base) -> Self:
		self.history.append(rule())

		if (ghost := self.current.ghost) is not None and ghost.square is not None:
			del self[ghost.square]

		return self


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
				piece.draw(screen)

				if piece is self.selected:
					piece.highlight(screen)

				piece.ghost = piece.__class__.ghost  # HACK

	def clicked(self, event: pygame.event.Event) -> bool:
		for square in chess.algebra.Square:
			if square.clicked(event):
				if self.promoting is not None:
					officers = cycle(chess.material.Pawn.officers)

					if square == self.promoting.target:
						self += self.promoting  # confirm promotion

						self.promoting = self.selected = None

					elif square == self.promoting.source:
						pawn = cast(chess.material.Pawn, self.promoting.piece)
						self.promoting.officer = next(officers)  # promote to next
						pawn.promote(self.promoting.officer)  # promote to current  # type: ignore

					else:
						self.promoting = None
						self.selected = None

					return True

				if self.selected is not None and self.selected.square is not None:
					if self.selected.side and (rule := self.selected.squares.get(square)) is not None:
						if isinstance(rule, chess.rules.Promote):
							self.promoting = rule
							pawn = cast(chess.material.Pawn, self[self.selected.square])
							pawn.promote(self.promoting.officer)  # type: ignore

						else:
							self += rule
							self.selected = None

					else:
						self.selected = None

				else:
					piece = self[square]
					self.selected = piece if piece is not None and piece.side else None

				return True

		return False
