from __future__ import annotations


from typing import TYPE_CHECKING
from weakref import ref as weakref

from chess.geometry import Square

if TYPE_CHECKING:
	from chess.material import Piece, Pawn, Officer


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = square

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return (other := board[self.target]) is     None


class Capt(Move):

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return (other := board[self.target]) is not None and self.piece.color != other.color


class Promote(Move):

	def __init__(self, pawn: Pawn, square: Square, officer: Officer):
		super().__init__(pawn, square)

		self.officer = officer

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return self.officer.square is None and super().__bool__()


class Castle(Move):

	...
