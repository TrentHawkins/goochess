from __future__ import annotations


import typing

import chess.utils
import chess.theme
import chess.algebra
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece:

	value: int = 0

	black: str = " "
	white: str = " "

	steps: chess.utils.Set[chess.algebra.Difference] = chess.utils.Set()


	def __init__(self,side: chess.engine.Side, square: chess.algebra.Square | None = None):
		self.side = side
		self.square = square
		self.color = self.side.color

		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = chess.theme.DEFAULT.pieces.black if self.color else chess.theme.DEFAULT.pieces.white

		return color.bg(self.black)


	@property
	def game(self) -> chess.engine.Game:
		return self.side.game

	@property
	def squares(self) -> chess.utils.Set[chess.algebra.Square]:
		return chess.utils.Set()


class Officer(Piece):

	...


class Melee(Piece):

	@property
	def squares(self) -> chess.utils.Set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.steps.moves:
				square = self.square + move

				if chess.rules.Move(self, square): squares      .add(square); continue
				if chess.rules.Capt(self, square): squares.capts.add(square); continue

		return squares


class Ranged(Piece):

	@property
	def squares(self) -> chess.utils.Set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.steps.moves:
				square = self.square

				while True:
					try:
						square += move

						if chess.rules.Move(self, square): squares      .add(square); continue
						if chess.rules.Capt(self, square): squares.capts.add(square); continue

						break

					except ValueError:
						break

		return squares


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	setps = chess.utils.Set(
		moves = {
			chess.algebra.Difference.S,
		},
		capts = {
			chess.algebra.Difference.SE,
			chess.algebra.Difference.SW,
		},
	)

	@property
	def squares(self) -> chess.utils.Set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.steps.moves:
				square = self.square

				try:
					if chess.rules.Move(self, square := square + move * self.color)                   : squares.moves.add(square)
					if chess.rules.Move(self, square := square + move * self.color) and not self.moved: squares.moves.add(square)

				except ValueError:
					continue

			for capt in self.steps.capts:
				try:
					if chess.rules.Capt(self, square := self.square + capt * self.color): squares.capts.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged, Officer):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	steps = chess.utils.Set(
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

	steps = chess.utils.Set(
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

	steps: chess.utils.Set[chess.algebra.Difference] = Rook.steps + Bishop.steps
#	steps = chess.utils.Set(
#		moves = {
#			chess.algebra.Difference.N2E,
#			chess.algebra.Difference.NE2,
#			chess.algebra.Difference.SE2,
#			chess.algebra.Difference.S2E,
#			chess.algebra.Difference.S2W,
#			chess.algebra.Difference.SW2,
#			chess.algebra.Difference.NW2,
#			chess.algebra.Difference.N2W,
#		}
#	)


class Star(Piece):

	steps = Rook.steps | Bishop.steps
#	steps = chess.utils.Set(
#		moves = {
#			chess.algebra.Difference.N, chess.algebra.Difference.NE,
#			chess.algebra.Difference.E, chess.algebra.Difference.SE,
#			chess.algebra.Difference.S, chess.algebra.Difference.SW,
#			chess.algebra.Difference.W, chess.algebra.Difference.NW,
#		}
#	)


class Queen(Ranged, Officer, Star):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Star):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	@property
	def squares(self) -> chess.utils.Set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			if chess.rules.CastleShort(self.side): squares.add(self.square + chess.algebra.Difference.E2)
			if chess.rules.CastleLong (self.side): squares.add(self.square + chess.algebra.Difference.W2)

		return squares


	def safe(self,
		square: chess.algebra.Square | None = None
	) -> bool:
		if square is None:
			square = self.square

		return True
