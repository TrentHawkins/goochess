from __future__ import annotations

from functools import total_ordering
from typing import Container, TYPE_CHECKING

import chess.base
import chess.geometry

if TYPE_CHECKING:
	import chess.game


@total_ordering
class Life(int):

	def __eq__(self, other: int | None) -> bool:
		return other is None or self == other

	def __le__(self, other: int | None) -> bool:
		return other is None or self <= other


class Piece:

	turns: int = 2 ** 32  # lifespan

	specs: set[chess.geometry.Move] = set()  # possible special moves
	moves: set[chess.geometry.Move] = set()  # possible moves
	capts: set[chess.geometry.Move] = set()  # possible captures


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(chess.base.moves for chess.base in cls.__bases__))
		cls.capts = cls.capts.union(*(chess.base.capts for chess.base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: int = 0

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

	def alive(self) -> bool:
		return self.turn < self.turns


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
		chess.geometry.Move.S2,
	}
	moves = specs | {
		chess.geometry.Move.S,
	}
	capts = {
		chess.geometry.Move.SE,
		chess.geometry.Move.SW,
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

	def squares(self, ) -> Container[chess.geometry.Square]:
		squares: set[chess.geometry.Square] = set()

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
		chess.geometry.Move.N,
		chess.geometry.Move.E,
		chess.geometry.Move.S,
		chess.geometry.Move.W,
	}
	capts = moves

class Bishop(Ranged, Piece):

	moves = {
		chess.geometry.Move.NE,
		chess.geometry.Move.SE,
		chess.geometry.Move.SW,
		chess.geometry.Move.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		chess.geometry.Move.N2E,
		chess.geometry.Move.NE2,
		chess.geometry.Move.SE2,
		chess.geometry.Move.S2E,
		chess.geometry.Move.S2W,
		chess.geometry.Move.SW2,
		chess.geometry.Move.NW2,
		chess.geometry.Move.N2W,
	}
	capts = moves



class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	specs = {
		chess.geometry.Move.E2,
		chess.geometry.Move.W2,
	}
	moves = specs
