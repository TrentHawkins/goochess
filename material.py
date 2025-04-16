from __future__ import annotations


from copy import copy
from enum import Enum
from typing import TYPE_CHECKING, Self

import pygame

import chess.theme
import chess.algebra
import chess.rules

if TYPE_CHECKING:
	import chess.engine


class Piece(chess.theme.Highlightable):

	square: chess.algebra.Square

	value: int = 0
	width: int = 0
	ghost: int = 0

	black: str = " "
	white: str = " "

	moves: chess.algebra.Vectors
	capts: chess.algebra.Vectors
	specs: chess.algebra.Vectors
	stock: chess.algebra.Squares


	def __init__(self, game: chess.engine.Game, color: chess.algebra.Color):
		super().__init__()

		self.color = color
		self.game = game

		self._moved: bool = False


	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __call__(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		self._moved = self._moved or move
		self.game[source], self.game[target] = kept, self.game[source]

		return self


	@property
	def moved(self) -> bool:
		return self._moved or self.square not in self.stock * self.color


	@classmethod
	def fromside(cls, side: chess.engine.Side) -> Self:
		return cls(side.game, side.color)


	@property
	def decal(self) -> str:
		color = "b" if self.color else "w"

		return color + super().decal

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + chess.theme.PIECE_OFFSET,
		)

	@property
	def side(self) -> chess.engine.Side:
		return self.game.black if self.color else self.game.white

	@property
	def king(self) -> King | None:
		return self.side.king

	@property
	def targets(self) -> chess.algebra.Squares:
		return chess.algebra.Squares()

	@property
	def squares(self) -> chess.algebra.Squares:
		squares = self.targets.copy()

		for step in self.targets:
			with step:
				if self.king is not None and not self.king.safe:
					squares.discard(step)

		return squares


	def clicked(self, event: pygame.event.Event) -> bool:
		if clicked := self.square.clicked(event):
			self.game.selected = self

		return clicked

	def draw(self, screen: pygame.Surface):
		if self.ghost:
			surf = copy(self.surf)
			surf.fill((*chess.theme.HIGH, 85 * (3 - self.ghost)),
				special_flags = pygame.BLEND_RGBA_MULT,
			)

		else:
			surf = self.surf

		screen.blit(surf, self.rect)


class Melee(Piece):

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		for move in self.moves:
			try:
				if step := chess.rules.Move(self.square + move, self): targets.add(step)
				if step := chess.rules.Capt(self.square + move, self): targets.add(step)

			except ValueError:
				continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		for move in self.moves:
			target = self.square

			try:
				while step := chess.rules.Move(target := target + move, self):
					targets.add(step)

			except ValueError:
				continue

			if step := chess.rules.Capt(target, self):
				targets.add(step)

		return targets


class Rook(Ranged):

	value: int = 5
	width: int = 5

	black: str = "r"  # "\u265c"
	white: str = "R"  # "\u2656"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.N,
		chess.algebra.Vector.E,
		chess.algebra.Vector.S,
		chess.algebra.Vector.W,
	)
	stock = chess.algebra.Squares(
		chess.algebra.Square.A8,
		chess.algebra.Square.H8,
	)


class Assymetric(Piece):

	@property
	def decal(self) -> str:
		flipped = "r" if self.color else ""

		return super().decal + flipped


class Bishop(Ranged, Assymetric):

	value: int = 3
	width: int = 6

	black: str = "b"  # "\u265d"
	white: str = "B"  # "\u2657"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.NE,
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
		chess.algebra.Vector.NW,
	)
	stock = chess.algebra.Squares(
		chess.algebra.Square.C8,
		chess.algebra.Square.F8,
	)


class Knight(Melee, Assymetric):

	value: int = 3
	width: int = 5

	black: str = "n"  # "\u265e"
	white: str = "N"  # "\u2658"

	moves = Rook.moves * Bishop.moves - Rook.moves
#	moves = chess.algebra.Vectors(
#		chess.algebra.Vector.N2E,
#		chess.algebra.Vector.NE2,
#		chess.algebra.Vector.SE2,
#		chess.algebra.Vector.S2E,
#		chess.algebra.Vector.S2W,
#		chess.algebra.Vector.SW2,
#		chess.algebra.Vector.NW2,
#		chess.algebra.Vector.N2W,
#	)
	stock = chess.algebra.Squares(
		chess.algebra.Square.B8,
		chess.algebra.Square.G8,
	)


class Star(Piece):

	width: int = 8

#	moves = chess.algebra.Vectors(
#			chess.algebra.Vector.N, chess.algebra.Vector.NE,
#			chess.algebra.Vector.E, chess.algebra.Vector.SE,
#			chess.algebra.Vector.S, chess.algebra.Vector.SW,
#			chess.algebra.Vector.W, chess.algebra.Vector.NW,
#	)
	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star):

	value: int = 9

	black: str = "q"  # "\u265b"
	white: str = "Q"  # "\u2655"

	stock = chess.algebra.Squares(
		chess.algebra.Square.D8,
	)


class King(Melee, Star):

	black: str = "k"  # "\u265a"
	white: str = "K"  # "\u2654"

	specs = chess.algebra.Vectors(
		chess.algebra.Vector.W2,
		chess.algebra.Vector.E2,
	)
	stock = chess.algebra.Squares(
		chess.algebra.Square.E8,
	)


	def __call__(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		if not self.moved and move:
			if self.side.arook is not None and target == source + chess.algebra.Vector.E2:
				self.side.arook(target + chess.algebra.Vector.W, move, kept)
			if self.side.hrook is not None and target == source + chess.algebra.Vector.W2:
				self.side.hrook(target + chess.algebra.Vector.E, move, kept)

		return super().__call__(target, move, kept)


	@property
	def squares(self) -> chess.algebra.Squares:
		squares = super().squares

		if not self.moved:
			if step := chess.rules.CastWest(self.square + chess.algebra.Vector.W2, self): squares.add(step)
			if step := chess.rules.CastEast(self.square + chess.algebra.Vector.E2, self): squares.add(step)

		return squares

	@property
	def safe(self) -> bool:
		return self.square not in self.side.other.targets.capts


class Officer(Enum):

	Q = Queen
	R = Rook
	N = Knight
	B = Bishop


	def surf(self, color: chess.algebra.Color) -> pygame.Surface:
		mod = "B" if color else "W"

		match self.name:
			case "Q": surf = chess.theme.Main[mod + "QUEEN" ].value.copy()
			case "R": surf = chess.theme.Main[mod + "ROOK"  ].value.copy()
			case "B": surf = chess.theme.Main[mod + "BISHOP"].value.copy()
			case "N": surf = chess.theme.Main[mod + "KNIGHT"].value.copy()
			case  _ : surf = chess.theme.Main[mod + "PAWN"  ].value.copy()

		surf.fill((*chess.theme.HIGH, 170), special_flags = pygame.BLEND_RGBA_MULT)

		return surf


class Pawn(Piece):

	value: int = 1
	width: int = 2

	black: str = "\u265f"
	white: str = "\u2659"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.S,
	)
	capts = chess.algebra.Vectors(
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
	)
	stock = chess.algebra.Squares(
		chess.algebra.Square.A7,
		chess.algebra.Square.B7,
		chess.algebra.Square.C7,
		chess.algebra.Square.D7,
		chess.algebra.Square.E7,
		chess.algebra.Square.F7,
		chess.algebra.Square.G7,
		chess.algebra.Square.H7,
	)


#	def __call__(self, target: chess.algebra.Square,
#		move: bool = True,
#		kept: Piece | None = None,
#	) -> Self:
#		assert (source := self.square) is not None
#
#		if move and not self.moved and target == source + chess.algebra.Vector.S2 * self.color:
#			self.side.ghost = self.game[source + chess.algebra.Vector.S  * self.color] = Ghost(self.side)
#
#		if move and isinstance(self.game[target], Ghost):
#			self.game[target + chess.algebra.Vector.N * self.color] = kept
#
#		return super().__call__(target, move, kept)


	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		for move in self.moves * self.color:
			try:
				if step := chess.rules.Move(target := self.square + move, self):
					targets.add(
						chess.rules.specialize(step,
							chess.rules.Promotion,
						)
					)

					if step := chess.rules.Rush(target := target + move, self):
						targets.add(step)

			except ValueError:
				continue

		for capt in self.capts * self.color:
			try:
				if step := chess.rules.Capt(self.square + capt, self):
					targets.add(
						chess.rules.specialize(step,
							chess.rules.EnPassant,
							chess.rules.Promotion,
						)
					)

			except ValueError:
				continue

		return targets

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				chess.theme.PIECE_OFFSET.x * 49 // 25,
				chess.theme.PIECE_OFFSET.y * 25 // 24,
			),
		)


	def promote(self, to: Officer):
		self.__class__ = to.value  # type: ignore


class Ghost(Piece):

	width = 2
	ghost = 3


	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				chess.theme.PIECE_OFFSET.x * 49 // 25,
				chess.theme.PIECE_OFFSET.y * 25 // 24,
			),
		)


class Pieces(chess.collection):

	def __init__(self, *pieces: Piece):
		self.king: King | None = None
		self.ghost: Ghost | None = None

		self.queens: set[Queen] = set()
		self.rooks: set[Rook] = set()
		self.knights: set[Knight] = set()
		self.bishops: set[Bishop] = set()
		self.pawns: set[Pawn] = set()

		for piece in pieces:
			match piece:
				case King  (): self.king  = piece
				case Ghost (): self.ghost = piece

				case Queen (): self.queens .add(piece)
				case Rook  (): self.rooks  .add(piece)
				case Knight(): self.knights.add(piece)
				case Bishop(): self.bishops.add(piece)
				case Pawn  (): self.pawns  .add(piece)

				case _      : ...
