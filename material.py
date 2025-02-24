from __future__ import annotations


import itertools
import typing

import chess.theme
import chess.algebra
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece:

	value: int = 0

	black: str = " "
	white: str = " "

	capts: set[chess.algebra.Difference] = set()
	capts: set[chess.algebra.Difference] = set()


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
	def targets(self) -> set[chess.algebra.Square]:
		return set()

	@property
	def squares(self) -> set[chess.algebra.Square]:
		return self.targets


	def squares_moves_from(self, steps: set[chess.algebra.Difference]) -> set[chess.algebra.Square]:
		return {self.square + step for step in steps} if self.square is not None else set()

	def add(self, step: int) -> typing.Self:
		assert self.square is not None
		self.game[self.square], self.game[self.square + step] = None, self.game[self.square]

		return self

	def sub(self, step: int) -> typing.Self:
		assert self.square is not None
		self.game[self.square], self.game[self.square + step] = self.game[self.square + step], None

		return self


class Officer(Piece):

	...


class Melee(Piece):

	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for capt in self.capts:
				try:
					target = self.square + capt

					if   chess.rules.Move(self, target): targets.add(target)
					elif chess.rules.Capt(self, target): targets.add(target)
					else:
						continue

				except ValueError:
					continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for move in self.capts:
				target = self.square

				while True:
					try:
						target += move

						if   chess.rules.Move(self, target): targets.add(target); continue
						elif chess.rules.Capt(self, target): targets.add(target); break
						else:
							break

					except ValueError:
						break

		return targets


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	capts = {
		chess.algebra.Difference.SE,
		chess.algebra.Difference.SW,
	}
	moves = {
		chess.algebra.Difference.S,
	}


	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for capt in self.capts:
				try:
					if chess.rules.Capt(self, target := self.square + capt * self.color):
						targets.add(target)

				except ValueError:
					continue

		return targets

	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.moves:
				try:
					if chess.rules.Move(self, square := self.square + move * self.color)                   : squares.add(square)
					if chess.rules.Move(self, square :=      square + move * self.color) and not self.moved: squares.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged, Officer):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	capts = {
		chess.algebra.Difference.N,
		chess.algebra.Difference.E,
		chess.algebra.Difference.S,
		chess.algebra.Difference.W,
	}


class Bishop(Ranged, Officer):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	capts = {
		chess.algebra.Difference.NE,
		chess.algebra.Difference.SE,
		chess.algebra.Difference.SW,
		chess.algebra.Difference.NW,
	}


class Knight(Melee, Officer):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

	capts = {straight + diagonal for straight, diagonal in itertools.product(Rook.capts, Bishop.capts)}
#	capts = {
#		chess.algebra.Difference.N2E,
#		chess.algebra.Difference.NE2,
#		chess.algebra.Difference.SE2,
#		chess.algebra.Difference.S2E,
#		chess.algebra.Difference.S2W,
#		chess.algebra.Difference.SW2,
#		chess.algebra.Difference.NW2,
#		chess.algebra.Difference.N2W,
#	}


class Star(Piece):

	capts = Rook.capts | Bishop.capts
#	capts = {
#		chess.algebra.Difference.N, chess.algebra.Difference.NE,
#		chess.algebra.Difference.E, chess.algebra.Difference.SE,
#		chess.algebra.Difference.S, chess.algebra.Difference.SW,
#		chess.algebra.Difference.W, chess.algebra.Difference.NW,
#	}


class Queen(Ranged, Officer, Star):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Star):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		return squares
