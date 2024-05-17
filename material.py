from typing import Callable, Container

from chess import Color, Move, Square


class Piece:

	turns: int = 2 ** 32  # lifespan

	specs: set[Move] = set()  # possible special moves
	moves: set[Move] = set()  # possible moves
	capts: set[Move] = set()  # possible captures


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.capts for base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: int = 0

	def __init__(self, color: Color,
		board = None,
		square: Square | None = None,
	) -> None:
		self.__pre_init__()

		self.color = color
		self.board = board
		self.square = square

		self.__post_init__()

	def __post_init__(self) -> None:
		...

	def alive(self) -> bool:
		return self.turn < self.turns


	def kill(self) -> None:
		self.__init__(self.color)



class Pawn(Piece):

	specs = {
		Move.S2,
	}
	moves = specs | {
		Move.S,
	}
	capts = {
		Move.SE,
		Move.SW,
	}

	def __post_init__(self) -> None:
		super().__post_init__()

		self.moves = {move * self.color for move in self.moves}
		self.capts = {capt * self.color for capt in self.capts}
		self.specs = {spec * self.color for spec in self.specs}

	#	Pawns start with the option to leap forward:
		self.moves.update(self.specs)


class Ghost(Pawn):

	turns: int = 1


class Melee(Piece):

	def squares(self, condition: Callable[[Square], bool]) -> Container[Square]:
		squares: set[Square] = set()

		if self.square is not None:
			for move in self.moves:
				try:
					squares.add(self.square + move)

				except ValueError:
					continue

			for capt in self.capts:
				try:
					squares.add(self.square + capt)

				except ValueError:
					continue

			if not self.moved:
				for spec in self.specs:
					try:
						squares.add(self.square + spec)

					except ValueError:
						continue

		return squares


class Ranged(Piece):

	...


class Rook(Ranged, Piece):

	moves = {
		Move.N,
		Move.E,
		Move.S,
		Move.W,
	}
	capts = moves

class Bishop(Ranged, Piece):

	moves = {
		Move.NE,
		Move.SE,
		Move.SW,
		Move.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		Move.N2E,
		Move.NE2,
		Move.SE2,
		Move.S2E,
		Move.S2W,
		Move.SW2,
		Move.NW2,
		Move.N2W,
	}
	capts = moves



class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs = {
		Move.E2,
		Move.W2,
	}
	moves = specs
