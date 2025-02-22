from __future__ import annotations


import itertools
import typing

import chess.theme
import chess.geometry
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece:

	range: int = 0
	value: int = 0

	black: str = " "
	white: str = " "

	moves: set[chess.geometry.Difference] = set()
	capts: set[chess.geometry.Difference] = set()
	specs: set[chess.geometry.Difference] = set()


	def __init_subclass__(cls, *args, **kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.moves for base in cls.__bases__)) if not cls.capts else cls.moves
		cls.specs = cls.specs.union(*(base.moves for base in cls.__bases__))

	#	cls.value += sum(base.value for base in cls.__bases__)


	def __init__(self, color: chess.geometry.Color,
		square: chess.geometry.Square | None = None,
	):
		self.color = color
		self.square = square

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = chess.theme.DEFAULT.pieces.black if self.color else chess.theme.DEFAULT.pieces.white

		return color.bg(self.black)


	def squares(self, game: chess.engine.Game) -> set[chess.geometry.Square]:
		return set()


class Officer(Piece):

	def squares(self, game: chess.engine.Game) -> set[chess.geometry.Square]:
		squares = super().squares(game)

		if self.square is not None:
			for move in self.moves | self.capts:
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


class Melee(Officer):

	range: int = 1


class Ranged(Officer):

	range: int = 8


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	moves = {
		chess.geometry.Difference.S ,
	}
	capts = {
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
	}


	def squares(self, game: chess.engine.Game) -> set[chess.geometry.Square]:
		squares = super().squares(game)

		if self.square is not None:
			for move in self.moves:
				try:
					if chess.rules.Move(self, square := self.square + move * self.color):
						squares.add(square)

					if not self.moved:
						if chess.rules.Move(self, square := square + move * self.color):
							squares.add(square)

				except ValueError:
					continue

			for move in self.capts:
				try:
					if chess.rules.Capt(self, square := self.square + move * self.color):
						squares.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	moves: set[chess.geometry.Difference] = {
		chess.geometry.Difference.N,
		chess.geometry.Difference.E,
		chess.geometry.Difference.S,
		chess.geometry.Difference.W,
	}


class Bishop(Ranged):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	moves: set[chess.geometry.Difference] = {
		chess.geometry.Difference.NE,
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
		chess.geometry.Difference.NW,
	}

class Knight(Melee):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

	moves: set[chess.geometry.Difference] = {
		straight + diagonal for straight, diagonal in itertools.product(Rook.moves, Bishop.moves)
	} - Rook.moves
#	moves: set[chess.geometry.Difference] = {
#		chess.geometry.Difference.N2E,
#		chess.geometry.Difference.NE2,
#		chess.geometry.Difference.SE2,
#		chess.geometry.Difference.S2E,
#		chess.geometry.Difference.S2W,
#		chess.geometry.Difference.SW2,
#		chess.geometry.Difference.NW2,
#		chess.geometry.Difference.N2W,
#	}


class Queen(Rook, Bishop):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Queen):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"

	specs: set[chess.geometry.Difference] = {
		chess.geometry.Difference.E2,
		chess.geometry.Difference.W2,
	}


	def safe(self,
		square: chess.geometry.Square | None = None
	) -> bool:
		if square is None:
			square = self.square

		return True
