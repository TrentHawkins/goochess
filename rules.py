from __future__ import annotations


from weakref import ref as weakref

from chess import Square
from chess import Piece
from chess import Board


class Move(int):

	__slots__ = ("piece", "square")


	def __new__(cls, piece: Piece, square: Square):
		assert piece.square is not None

		move = super().__new__(cls, square - piece.square)

		move.piece = piece
		move.square = square

		return move


	def __bool__(self) -> bool:
		assert (board := self.piece.board()) is not None
		return (other := board[self.square]) is     None


class Capture(Move):

	def __bool__(self) -> bool:
		assert (board := self.piece.board()) is not None
		return (other := board[self.square]) is not None and self.piece.color != other.color


class Rush(Move):

	...


class EnPassant(Capture):

	...


class Promotion(Move):

	...


class Castle(Move):

	...
