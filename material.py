from __future__ import annotations

from typing import Container, Self, TYPE_CHECKING

import chess.base
import chess.geometry

if TYPE_CHECKING:
	import chess.game


class Piece:

	specs: set[chess.geometry.Difference] = set()  # possible special moves
	moves: set[chess.geometry.Difference] = set()  # possible moves
	capts: set[chess.geometry.Difference] = set()  # possible captures


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(chess.base.moves for chess.base in cls.__bases__))
		cls.capts = cls.capts.union(*(chess.base.capts for chess.base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: bool = False

	def __init__(self, color: chess.base.Color,
		board: chess.game.Board | None = None,
		square: chess.geometry.Square | None = None,
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


	def add(self,
		board: chess.game.Board | None = None,
		square: chess.geometry.Square | None = None,
	) -> None:
		self.board = board
		self.square = square

	def discard(self) -> None:
		self.__init__(self.color)


class Pawn(Piece):

	specs = {
		chess.geometry.Difference.S2,
	}
	moves = specs | {
		chess.geometry.Difference.S,
	}
	capts = {
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
	}


class Ghost:

	...


class Melee(Piece):

	def squares(self) -> chess.geometry.Squares:
		squares = chess.geometry.Squares()

		if self.square is not None:
			for move in self.moves:
				try:
					squares.squares.add(self.square + move)

				except ValueError:
					continue

			for capt in self.capts:
				try:
					squares.targets.add(self.square + capt)

				except ValueError:
					continue

			if not self.moved:
				for spec in self.specs:
					try:
						squares.squares.add(self.square + spec)

					except ValueError:
						continue

		return squares


class Ranged(Piece):

	...


class Rook(Ranged, Piece):

	moves = {
		chess.geometry.Difference.N,
		chess.geometry.Difference.E,
		chess.geometry.Difference.S,
		chess.geometry.Difference.W,
	}
	capts = moves


class Bishop(Ranged, Piece):

	moves = {
		chess.geometry.Difference.NE,
		chess.geometry.Difference.SE,
		chess.geometry.Difference.SW,
		chess.geometry.Difference.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		chess.geometry.Difference.N2E,
		chess.geometry.Difference.NE2,
		chess.geometry.Difference.SE2,
		chess.geometry.Difference.S2E,
		chess.geometry.Difference.S2W,
		chess.geometry.Difference.SW2,
		chess.geometry.Difference.NW2,
		chess.geometry.Difference.N2W,
	}
	capts = moves


class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs = {
		chess.geometry.Difference.E2,
		chess.geometry.Difference.W2,
	}
	moves = specs
