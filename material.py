from __future__ import annotations

from typing import Self, TYPE_CHECKING

import chess.base
import chess.geometry

if TYPE_CHECKING:
	import chess.game


class Piece:

	moves: set[chess.geometry.Difference] = set()
	capts: set[chess.geometry.Difference] = set()
	specs: set[chess.geometry.Difference] = set()


	def __init_subclass__(cls):
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))

	def __init__(self, color: chess.base.Color,
		square: chess.geometry.Square | None = None,
	):
		self.color = color
		self.square = square

		self.turn: int = 0
		self.moved: bool = False


	def append(self, squares: set[chess.geometry.Square], move: chess.geometry.Difference):
		if self.square is not None:
			try:
				squares.add(self.square + move)

			except ValueError:
				...


class Pawn(Piece):

	moves = {
		chess.geometry.Difference.S ,
	}
	capts = {
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
	}
	specs = {
		chess.geometry.Difference.S2,
	}


class Ghost(Piece):

	...


class Melee(Piece):

	@property
	def squares(self) -> set[chess.geometry.Square]:
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

	def squares(self) -> set[chess.geometry.Square]:
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

	moves: set[chess.geometry.Difference] = {
		chess.geometry.Difference.N,
		chess.geometry.Difference.E,
		chess.geometry.Difference.S,
		chess.geometry.Difference.W,
	}


class Bishop(Ranged, Piece):

	moves: set[chess.geometry.Difference] = {
		chess.geometry.Difference.NE,
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
		chess.geometry.Difference.NW,
	}

class Knight(Melee, Piece):

	moves: set[chess.geometry.Difference] = {
		chess.geometry.Difference.N2E,
		chess.geometry.Difference.NE2,
		chess.geometry.Difference.SE2,
		chess.geometry.Difference.S2E,
		chess.geometry.Difference.S2W,
		chess.geometry.Difference.SW2,
		chess.geometry.Difference.NW2,
		chess.geometry.Difference.N2W,
	}


class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs: set[chess.geometry.Difference] = {
		chess.geometry.Difference.E2,
		chess.geometry.Difference.W2,
	}
