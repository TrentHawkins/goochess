from __future__ import annotations


from itertools import product
from typing import TYPE_CHECKING
from weakref import ref as weakref

from chess import DEFAULT
from chess import Color, Square, Difference

if TYPE_CHECKING:
	from chess import Board


class Piece:

	range: int = 0
	value: int = 0

	black: str = " "
	white: str = " "

	moves: set[Difference] = set()
	capts: set[Difference] = set()
#	specs: set[Difference] = set()


	def __init_subclass__(cls, *args, **kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.moves for base in cls.__bases__))
	#	cls.specs = cls.specs.union(*(base.moves for base in cls.__bases__))

	#	cls.value += sum(base.value for base in cls.__bases__)


	def __init__(self, color: Color, board: Board,
		square: Square | None = None,
	):
		self.color = color
		self.square = square
		self.board = weakref(board)

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = DEFAULT.pieces.black if self.color else DEFAULT.pieces.white

		return color.bg(self.black)

	def __eq__(self, other: Piece | None) -> bool:
		return other is not None and self.color == other.color

	def __ne__(self, other: Piece | None) -> bool:
		return other is not None and self.color != other.color


	@property
	def squares(self) -> set[Square]:
		return set()


	def move(self, square: Square):
		assert (board := self.board()) is not None

		if square not in self.squares or self.square is None:
			raise ValueError(f"invalid move of {repr(self)} from {repr(self.square)} to {repr(square)}")

		board[self.square], board[square] = None, self
		self.moved = True


class Officer(Piece):

	@property
	def squares(self) -> set[Square]:
		assert (board := self.board()) is not None

		squares = super().squares

		if self.square is not None:
			for move in self.moves | self.capts:
				square = self.square

				for _ in range(self.range):
					try:
						square += move

						if (other := board[square]) is not None and self.color == other.color:
							break

						squares.add(square)

						if (other := board[square]) is not None and self.color != other.color:
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
#	specs = {
#		Difference.S2,
#	}


	@property
	def squares(self) -> set[Square]:
		assert (board := self.board()) is not None

		squares = super().squares

		if self.square is not None:
			for move in self.moves:
				try:
					if board[square := self.square + (move := move * self.color)] is None:
						squares.add(square)

					if not self.moved:
						squares.add(square + move)  # HACK

				except ValueError:
					continue

			for move in self.capts:
				try:
					if (other := board[square := self.square + move * self.color]) is not None and self.color != other.color:
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

#	specs: set[Difference] = {
#		Difference.E2,
#		Difference.W2,
#	}
