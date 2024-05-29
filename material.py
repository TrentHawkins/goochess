from __future__ import annotations

from typing import Container, Self, TYPE_CHECKING

import chess.base
import chess.geometry

if TYPE_CHECKING:
	import chess.game


class Piece:

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set()


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(chess.base.moves for chess.base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: bool = False

	def __init__(self, color: chess.base.Color,
		board: chess.game.Board | None = None,
		square: chess.geometry.Square | None = None,
	) -> None:
		self.__pre_init__()

		self.color = color
		self.board = board
		self.square = square

		self.__post_init__()

	def __post_init__(self) -> None:
		...


	def add(self,
		board: chess.game.Board | None = None,
		square: chess.geometry.Square | None = None,
	) -> None:
		self.__init__(self.color,
			board = board,
			square = square,
		)

	def discard(self) -> None:
		self.__init__(self.color)


class Pawn(Piece):

	moves = chess.base.Set(
		squares = {
			chess.geometry.Difference.S,
			chess.geometry.Difference.S2,
		},
		targets = {
			chess.geometry.Difference.SE,
			chess.geometry.Difference.SW,
		},
		special = {
			chess.geometry.Difference.S2,
		},
	)


class Ghost:

	...


class Melee(Piece):

	def squares(self) -> tuple[
		set[chess.geometry.Square],
		set[chess.geometry.Square],
		set[chess.geometry.Square],
	]:
		squares = set()
		targets = set()
		special = set()

		if self.square is not None:
			for move in self.moves.squares:
				try:
					squares.add(self.square + move)

				except ValueError:
					continue

			for capt in self.moves.targets:
				try:
					targets.add(self.square + capt)

				except ValueError:
					continue

			if not self.moved:
				for spec in self.moves.special:
					try:
						special.add(self.square + spec)

					except ValueError:
						continue

		return (
			squares,
			targets,
			special,
		)


class Ranged(Piece):

	...


class Rook(Ranged, Piece):

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set(
		squares = {
			chess.geometry.Difference.N,
			chess.geometry.Difference.E,
			chess.geometry.Difference.S,
			chess.geometry.Difference.W,
		}
	)


class Bishop(Ranged, Piece):

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set(
		squares = {
			chess.geometry.Difference.NE,
			chess.geometry.Difference.SE,
			chess.geometry.Difference.SW,
			chess.geometry.Difference.NW,
		}
	)


class Knight(Melee, Piece):

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set(
		squares = {
			chess.geometry.Difference.N2E,
			chess.geometry.Difference.NE2,
			chess.geometry.Difference.SE2,
			chess.geometry.Difference.S2E,
			chess.geometry.Difference.S2W,
			chess.geometry.Difference.SW2,
			chess.geometry.Difference.NW2,
			chess.geometry.Difference.N2W,
		}
	)


class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set(
		special = {
			chess.geometry.Difference.E2,
			chess.geometry.Difference.W2,
		}
	)
