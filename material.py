from typing import Container

import base
import geometry
import game


class Piece:

	turns: int = 2 ** 32  # lifespan

	specs: set[geometry.Move] = set()  # possible special moves
	moves: set[geometry.Move] = set()  # possible moves
	capts: set[geometry.Move] = set()  # possible captures


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.capts for base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: int = 0

	def __init__(self, color: base.Color,
		board: game.Board | None = None,
		square: geometry.Square | None = None,
	) -> None:
		self.__pre_init__()

		self.color = color
		self.add(
			board = board,
			square = square,
		)

		self.__post_init__()

	def __post_init__(self) -> None:
		...

	def alive(self) -> bool:
		return self.turn < self.turns


	def add(self,
		board: game.Board | None = None,
		square: geometry.Square | None = None,
	) -> None:
		self.board = board
		self.square = square


	def discard(self) -> None:
		self.__init__(self.color)


class Pawn(Piece):

	specs = {
		geometry.Move.S2,
	}
	moves = specs | {
		geometry.Move.S,
	}
	capts = {
		geometry.Move.SE,
		geometry.Move.SW,
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

	def squares(self, ) -> Container[geometry.Square]:
		squares: set[geometry.Square] = set()

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
		geometry.Move.N,
		geometry.Move.E,
		geometry.Move.S,
		geometry.Move.W,
	}
	capts = moves

class Bishop(Ranged, Piece):

	moves = {
		geometry.Move.NE,
		geometry.Move.SE,
		geometry.Move.SW,
		geometry.Move.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		geometry.Move.N2E,
		geometry.Move.NE2,
		geometry.Move.SE2,
		geometry.Move.S2E,
		geometry.Move.S2W,
		geometry.Move.SW2,
		geometry.Move.NW2,
		geometry.Move.N2W,
	}
	capts = moves



class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs = {
		geometry.Move.E2,
		geometry.Move.W2,
	}
	moves = specs
