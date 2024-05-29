from __future__ import annotations

from typing import TYPE_CHECKING

import chess.base
import chess.geometry

if TYPE_CHECKING:
	import chess.game


class Piece:

	moves: chess.base.Set[chess.geometry.Difference] = chess.base.Set()


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))

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


	def append(self, squares: set[chess.geometry.Square], move: chess.geometry.Difference):
		if self.square is not None:
			try:
				squares.add(self.square + move)

			except ValueError:
				...


class Pawn(Piece):

	def __post_init__(self) -> None:
		self.moves = chess.base.Set(
			squares = {
				chess.geometry.Difference(self.color * chess.geometry.Difference.S ),
				chess.geometry.Difference(self.color * chess.geometry.Difference.S2),
			},
			targets = {
				chess.geometry.Difference(self.color * chess.geometry.Difference.SE),
				chess.geometry.Difference(self.color * chess.geometry.Difference.SW),
			},
			special = {
				chess.geometry.Difference(self.color * chess.geometry.Difference.S2),
			},
	)


class Ghost:

	...


class Melee(Piece):

	def squares(self) -> chess.base.Set[chess.geometry.Square]:
		squares = chess.base.Set()

		for move in self.moves.squares:
			self.append(squares.squares, move)

		for capt in self.moves.targets:
			self.append(squares.targets, capt)

		if not self.moved:
			for spec in self.moves.special:
				self.append(squares.special, spec)

		return squares


class Ranged(Piece):

	def squares(self) -> chess.base.Set[chess.geometry.Square]:
		squares = chess.base.Set()

		for move in self.moves.squares:
			self.append(squares.squares, move)

		for capt in self.moves.targets:
			self.append(squares.targets, capt)

		if not self.moved:
			for spec in self.moves.special:
				self.append(squares.special, spec)

		return squares


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
