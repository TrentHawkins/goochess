from __future__ import annotations


from itertools import product

from chess.theme import DEFAULT
from chess.geometry import Color, Square, Difference, Difference
from chess.rules import Move, Capt, Castle


class Piece:

	range: int = 0
	value: int = 0

	black: str = " "
	white: str = " "

	moves: set[Difference] = set()
	capts: set[Difference] = set()
	specs: set[Difference] = set()


	def __init_subclass__(cls, *args, **kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.moves for base in cls.__bases__)) if not cls.capts else cls.moves
		cls.specs = cls.specs.union(*(base.moves for base in cls.__bases__))

	#	cls.value += sum(base.value for base in cls.__bases__)


	def __init__(self, color: Color,
		square: Square | None = None,
	):
		self.color = color
		self.square = square

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = DEFAULT.pieces.black if self.color else DEFAULT.pieces.white

		return color.bg(self.black)


	@property
	def squares(self) -> set[Square]:
		return set()


class Officer(Piece):

	@property
	def squares(self) -> set[Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.moves | self.capts:
				square = self.square

				for _ in range(self.range):
					try:
						square += move

						if not Move(self, square):
							break

						squares.add(square)

						if not Capt(self, square):
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
		Difference.S ,
	}
	capts = {
		Difference.SE,
		Difference.SW,
	}


	@property
	def squares(self) -> set[Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.moves:
				try:
					if Move(self, square := self.square + move * self.color):
						squares.add(square)

					if not self.moved:
						if Move(self, square := square + move * self.color):
							squares.add(square)

				except ValueError:
					continue

			for move in self.capts:
				try:
					if Capt(self, square := self.square + move * self.color):
						squares.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	moves: set[Difference] = {
		Difference.N,
		Difference.E,
		Difference.S,
		Difference.W,
	}


class Bishop(Ranged):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	moves: set[Difference] = {
		Difference.NE,
		Difference.SE,
		Difference.SW,
		Difference.NW,
	}

class Knight(Melee):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

	moves: set[Difference] = {straight + diagonal for straight, diagonal in product(Rook.moves, Bishop.moves)} - Rook.moves
#	moves: set[Difference] = {
#		Difference.N2E,
#		Difference.NE2,
#		Difference.SE2,
#		Difference.S2E,
#		Difference.S2W,
#		Difference.SW2,
#		Difference.NW2,
#		Difference.N2W,
#	}


class Queen(Rook, Bishop):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Queen):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"

	specs: set[Difference] = {
		Difference.E2,
		Difference.W2,
	}


	def safe(self,
		square: Square | None = None
	) -> bool:
		if square is None:
			square = self.square

		return True
