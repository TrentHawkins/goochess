from __future__ import annotations


import itertools
import typing

import chess.theme
import chess.algebra
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece:

	range: int = 0
	value: int = 0

	black: str = " "
	white: str = " "

	steps: chess.Set[chess.algebra.Difference] = chess.Set()


	def __init__(self,
		game: chess.engine.Game,
		side: chess.engine.Side, square: chess.algebra.Square | None = None,
	):
		self.game = game
		self.side = side

		self.square = square
		self.color = self.side.color

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = chess.theme.DEFAULT.pieces.black if self.color else chess.theme.DEFAULT.pieces.white

		return color.bg(self.black)


	@property
	def squares(self) -> set[chess.algebra.Square]:
		return set()


class Officer(Piece):

	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.steps.moves | self.steps.capts:
				square = self.square

				for _ in range(self.range):
					try:
						square += move

						if not chess.rules.Move(self, square):
							break

						squares.add(square)

						if not chess.rules.Capt(self, square):
							break

					except ValueError:
						break

		return squares


class Melee(Piece):

	range: int = 1


class Ranged(Piece):

	range: int = 7


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	setps = chess.Set(
		moves = {
			chess.algebra.Difference.S,
		},
		capts = {
			chess.algebra.Difference.SE,
			chess.algebra.Difference.SW,
		},
	)

	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.steps.moves:
				try:
					if chess.rules.Move(self, square := self.square + move * self.color):
						squares.add(square)

					if not self.moved:
						if chess.rules.Move(self, square := square + move * self.color):
							squares.add(square)

				except ValueError:
					continue

			for move in self.steps.capts:
				try:
					if chess.rules.Capt(self, square := self.square + move * self.color):
						squares.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged, Officer):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	steps = chess.Set(
		moves = {
			chess.algebra.Difference.N,
			chess.algebra.Difference.E,
			chess.algebra.Difference.S,
			chess.algebra.Difference.W,
		}
	)


class Bishop(Ranged, Officer):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	steps = chess.Set(
		moves = {
			chess.algebra.Difference.NE,
			chess.algebra.Difference.SE,
			chess.algebra.Difference.SW,
			chess.algebra.Difference.NW,
		}
	)

class Knight(Melee, Officer):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

#	moves: set[chess.algebra.Difference] = {
#		straight + diagonal for straight, diagonal in itertools.product(Rook.steps, Bishop.steps)
#	} - Rook.steps
	steps = chess.Set(
		moves = {
			chess.algebra.Difference.N2E,
			chess.algebra.Difference.NE2,
			chess.algebra.Difference.SE2,
			chess.algebra.Difference.S2E,
			chess.algebra.Difference.S2W,
			chess.algebra.Difference.SW2,
			chess.algebra.Difference.NW2,
			chess.algebra.Difference.N2W,
		}
	)


class Star(Piece):

	steps = Rook.steps | Bishop.steps


class Queen(Star, Ranged, Officer):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Star, Melee):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			if chess.rules.CastleShort(self.game, self.side): squares.add(self.square + chess.algebra.Difference.E2)
			if chess.rules.CastleLong (self.game, self.side): squares.add(self.square + chess.algebra.Difference.W2)

		return squares


	def safe(self,
		square: chess.algebra.Square | None = None
	) -> bool:
		if square is None:
			square = self.square

		return True
