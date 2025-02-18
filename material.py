from __future__ import annotations


from chess import DEFAULT
from chess import Color
from chess import Square, Difference


class Piece:

	value: int = 0

	symbol: str = " "
	white: str = " "

	moves: set[Difference] = set()
	capts: set[Difference] = set()
	specs: set[Difference] = set()


	def __init_subclass__(cls, *args,
		value = 0,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.moves for base in cls.__bases__)) if cls.capts else cls.moves
		cls.specs = cls.specs.union(*(base.moves for base in cls.__bases__))

		cls.value += value


	def __init__(self, color: Color,
		square: Square | None = None,
	):
		self.color = color
		self.square = square

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		color = DEFAULT.pieces.black if self.color else DEFAULT.pieces.white

		return repr(self.square).replace(" ", color.bg(self.symbol))


class Officer(Piece):

	...


class Melee(Officer):

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


class Ranged(Officer):

	@property
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


class Pawn(Piece):

	symbol: str = "♟"

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

	def promote(self, rank: type):
		if not issubclass(rank, Officer):
			raise ValueError


class Ghost(Pawn):

	...


class Rook(Ranged):

	symbol: str = "♜"

	moves: set[Difference] = {
		Difference.N,
		Difference.E,
		Difference.S,
		Difference.W,
	}


class Bishop(Ranged):

	symbol: str = "♝"

	moves: set[Difference] = {
		Difference.NE,
		Difference.SE,
		Difference.SW,
		Difference.NW,
	}

class Knight(Melee):

	symbol: str = "♞"

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

	symbol: str = "♛"


class King(Melee, Queen):

	symbol: str = "♚"

	specs: set[Difference] = {
		Difference.E2,
		Difference.W2,
	}


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece
		self.source = self.piece.square
		self.target = square
