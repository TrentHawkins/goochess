from __future__ import annotations


from copy import copy
from enum import Enum
from typing import TYPE_CHECKING, Self

import pygame

import src.theme
import src.algebra
import src.rules

if TYPE_CHECKING:
	import src.engine


class Piece(src.theme.Highlightable):

	square: src.algebra.Square

	value: int = 0
	width: int = 0
	ghost: int = 0

	black: str = " "
	white: str = " "

	moves: src.algebra.Vectors
	capts: src.algebra.Vectors
	specs: src.algebra.Vectors
	stock: src.algebra.Squares


	def __init__(self, game: src.engine.Game, color: src.algebra.Color):
		super().__init__()

		self.color = color
		self.game = game

		self._moved: bool = False


	def __repr__(self) -> str:
		return self.forsyth_edwards

	def __call__(self, target: src.algebra.Square,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		self.game[source], self.game[target] = kept, self.game[source]

		return self


	@classmethod
	def from_forsyth_edwards(cls, game: src.engine.Game, symbol: str) -> Piece | None:
		match symbol:
			case "♟": return Pawn  (game, src.algebra.Color.BLACK)
			case "♙": return Pawn  (game, src.algebra.Color.WHITE)
			case "♜": return Rook  (game, src.algebra.Color.BLACK)
			case "♖": return Rook  (game, src.algebra.Color.WHITE)
			case "♞": return Knight(game, src.algebra.Color.BLACK)
			case "♘": return Knight(game, src.algebra.Color.WHITE)
			case "♝": return Bishop(game, src.algebra.Color.BLACK)
			case "♗": return Bishop(game, src.algebra.Color.WHITE)
			case "♛": return Queen (game, src.algebra.Color.BLACK)
			case "♕": return Queen (game, src.algebra.Color.WHITE)
			case "♚": return King  (game, src.algebra.Color.BLACK)
			case "♔": return King  (game, src.algebra.Color.WHITE)

	@classmethod
	def fromside(cls, side: src.engine.Side) -> Self:
		return cls(side.game, side.color)


	@property
	def forsyth_edwards(self) -> str:
		return self.black if self.color else self.white

	@property
	def moved(self) -> bool:
		return self._moved or self.square not in self.stock * self.color

	@property
	def decal(self) -> str:
		color = "b" if self.color else "w"

		return color + super().decal

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + src.theme.PIECE_OFFSET,
		)

	@property
	def side(self) -> src.engine.Side:
		return self.game.black if self.color else self.game.white

	@property
	def king(self) -> King | None:
		return self.side.king

	@property
	def targets(self) -> src.algebra.Squares:
		return src.algebra.Squares()

	@property
	def squares(self) -> src.algebra.Squares:
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
			surf.fill((*src.theme.HIGH, 85 * (3 - self.ghost)),
				special_flags = pygame.BLEND_RGBA_MULT,
			)

		else:
			surf = self.surf

		screen.blit(surf, self.rect)


class Melee(Piece):

	@property
	def targets(self) -> src.algebra.Squares:
		targets = super().targets

		for move in self.moves:
			try:
				if step := src.rules.Move(self.square + move, self): targets.add(step)
				if step := src.rules.Capt(self.square + move, self): targets.add(step)

			except ValueError:
				continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> src.algebra.Squares:
		targets = super().targets

		for move in self.moves:
			target = self.square

			try:
				while step := src.rules.Move(target := target + move, self):
					targets.add(step)

			except ValueError:
				continue

			if step := src.rules.Capt(target, self):
				targets.add(step)

		return targets


class Rook(Ranged):

	value: int = 5
	width: int = 5

	black: str = "♜"
	white: str = "♖"

	moves = src.algebra.Vectors(
		src.algebra.Vector.N,
		src.algebra.Vector.E,
		src.algebra.Vector.S,
		src.algebra.Vector.W,
	)
	stock = src.algebra.Squares(
		src.algebra.Square.A8,
		src.algebra.Square.H8,
	)


class Assymetric(Piece):

	@property
	def decal(self) -> str:
		flipped = "r" if self.color else ""

		return super().decal + flipped


class Bishop(Ranged, Assymetric):

	value: int = 3
	width: int = 6

	black: str = "♝"
	white: str = "♗"

	moves = src.algebra.Vectors(
		src.algebra.Vector.NE,
		src.algebra.Vector.SE,
		src.algebra.Vector.SW,
		src.algebra.Vector.NW,
	)
	stock = src.algebra.Squares(
		src.algebra.Square.C8,
		src.algebra.Square.F8,
	)


class Knight(Melee, Assymetric):

	value: int = 3
	width: int = 5

	black: str = "♞"
	white: str = "♘"

	moves = Rook.moves * Bishop.moves - Rook.moves
#	moves = src.algebra.Vectors(
#		src.algebra.Vector.N2E,
#		src.algebra.Vector.NE2,
#		src.algebra.Vector.SE2,
#		src.algebra.Vector.S2E,
#		src.algebra.Vector.S2W,
#		src.algebra.Vector.SW2,
#		src.algebra.Vector.NW2,
#		src.algebra.Vector.N2W,
#	)
	stock = src.algebra.Squares(
		src.algebra.Square.B8,
		src.algebra.Square.G8,
	)


class Star(Piece):

	width: int = 8

#	moves = src.algebra.Vectors(
#			src.algebra.Vector.N, src.algebra.Vector.NE,
#			src.algebra.Vector.E, src.algebra.Vector.SE,
#			src.algebra.Vector.S, src.algebra.Vector.SW,
#			src.algebra.Vector.W, src.algebra.Vector.NW,
#	)
	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star):

	value: int = 9

	black: str = "♛"
	white: str = "♕"

	stock = src.algebra.Squares(
		src.algebra.Square.D8,
	)


class King(Melee, Star):

	black: str = "♚"
	white: str = "♔"

	specs = src.algebra.Vectors(
		src.algebra.Vector.W2,
		src.algebra.Vector.E2,
	)
	stock = src.algebra.Squares(
		src.algebra.Square.E8,
	)


	def __call__(self, target: src.algebra.Square,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		if not self.moved:
			if self.side.arook is not None and target == source + src.algebra.Vector.E2:
				self.side.arook(target + src.algebra.Vector.W, kept)
			if self.side.hrook is not None and target == source + src.algebra.Vector.W2:
				self.side.hrook(target + src.algebra.Vector.E, kept)

		return super().__call__(target, kept)


	@property
	def squares(self) -> src.algebra.Squares:
		squares = super().squares

		if not self.moved:
			if step := src.rules.CastWest(self.square + src.algebra.Vector.W2, self): squares.add(step)
			if step := src.rules.CastEast(self.square + src.algebra.Vector.E2, self): squares.add(step)

		return squares

	@property
	def safe(self) -> bool:
		return self.square not in self.side.other.targets.capts


class Officer(Enum):

	Q = Queen
	R = Rook
	N = Knight
	B = Bishop


	def surf(self, color: src.algebra.Color) -> pygame.Surface:
		mod = "B" if color else "W"

		match self.name:
			case "Q": surf = src.theme.Main[mod + "QUEEN" ].value.copy()
			case "R": surf = src.theme.Main[mod + "ROOK"  ].value.copy()
			case "B": surf = src.theme.Main[mod + "BISHOP"].value.copy()
			case "N": surf = src.theme.Main[mod + "KNIGHT"].value.copy()
			case  _ : surf = src.theme.Main[mod + "PAWN"  ].value.copy()

		surf.fill((*src.theme.HIGH, 170), special_flags = pygame.BLEND_RGBA_MULT)

		return surf


class Pawn(Piece):

	value: int = 1
	width: int = 2

	black: str = "♟"
	white: str = "♙"

	moves = src.algebra.Vectors(
		src.algebra.Vector.S,
	)
	capts = src.algebra.Vectors(
		src.algebra.Vector.SE,
		src.algebra.Vector.SW,
	)
	stock = src.algebra.Squares(
		src.algebra.Square.A7,
		src.algebra.Square.B7,
		src.algebra.Square.C7,
		src.algebra.Square.D7,
		src.algebra.Square.E7,
		src.algebra.Square.F7,
		src.algebra.Square.G7,
		src.algebra.Square.H7,
	)


	@property
	def targets(self) -> src.algebra.Squares:
		targets = super().targets

		for move in self.moves * self.color:
			try:
				if step := src.rules.Move(target := self.square + move, self):
					targets.add(
						src.rules.specialize(step,
							src.rules.Promotion,
						)
					)

					if step := src.rules.Rush(target := target + move, self):
						targets.add(step)

			except ValueError:
				continue

		for capt in self.capts * self.color:
			try:
				if step := src.rules.Capt(self.square + capt, self):
					targets.add(
						src.rules.specialize(step,
							src.rules.EnPassant,
							src.rules.Promotion,
						)
					)

			except ValueError:
				continue

		return targets

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				src.theme.PIECE_OFFSET.x * 49 // 25,
				src.theme.PIECE_OFFSET.y * 25 // 24,
			),
		)


	def promote(self, to: Officer):
		self.game[self.square] = to.value.fromside(self.side)

class Ghost(Piece):

	width = 2
	ghost = 3


	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				src.theme.PIECE_OFFSET.x * 49 // 25,
				src.theme.PIECE_OFFSET.y * 25 // 24,
			),
		)
