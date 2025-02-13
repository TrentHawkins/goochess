from __future__ import annotations


from chess import Color
from chess import Square, Difference


class Piece:

	value: int

	moves: set[Difference] = set()
	capts: set[Difference] = set()
	specs: set[Difference] = set()


	def __init_subclass__(cls):
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))

	def __init__(self, color: Color,
		square: Square | None = None,
	):
		self.color = color
		self.square = square

		self.turn: int = 0
		self.moved: bool = False

	def __hash__(self) -> int:
		return hash((self.__class__, self.color, self.square))


	def append(self, squares: set[Square], move: Difference):
		if self.square is not None:
			try:
				squares.add(self.square + move)

			except ValueError:
				...


class Pawn(Piece):

	moves = {
		Difference.S ,
	}
	capts = {
		Difference.SE,
		Difference.SW,
	}
	specs = {
		Difference.S2,
	}


class Ghost(Piece):

	...


class Melee(Piece):

	@property
	def squares(self) -> set[Square]:
		squares = set()

		if self.square is not None:
			for move in self.moves | self.capts:
				try:
					square = self.square + move
					squares.add(square)

				except ValueError:
					continue

			if not self.moved:
				for spec in self.specs:
					try:
						square = self.square + spec
						squares.add(square)

					except ValueError:
						continue

		return squares


class Ranged(Piece):

	def squares(self) -> set[Square]:
		squares = set()

		if self.square is not None:
			for move in self.moves | self.capts:
				while True:
					try:
						square = self.square + move
						squares.add(square)

					except ValueError:
						continue

			if not self.moved:
				for spec in self.specs:
					while True:
						try:
							square = self.square + spec
							squares.add(square)

						except ValueError:
							continue

		return squares



class Rook(Ranged, Piece):

	moves: set[Difference] = {
		Difference.N,
		Difference.E,
		Difference.S,
		Difference.W,
	}


class Bishop(Ranged, Piece):

	moves: set[Difference] = {
		Difference.NE,
		Difference.SE,
		Difference.SW,
		Difference.NW,
	}

class Knight(Melee, Piece):

	moves: set[Difference] = {
		Difference.N2E,
		Difference.NE2,
		Difference.SE2,
		Difference.S2E,
		Difference.S2W,
		Difference.SW2,
		Difference.NW2,
		Difference.N2W,
	}


class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs: set[Difference] = {
		Difference.E2,
		Difference.W2,
	}
