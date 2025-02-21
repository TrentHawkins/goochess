from __future__ import annotations


from typing import TYPE_CHECKING
from weakref import ref as weakref

from chess.geometry import Square

if TYPE_CHECKING:
	from chess.material import Piece, Officer, Pawn, Rook, King


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = square

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return (other := board[self.target]) is     None

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)


class Capt(Move):

	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return (other := board[self.target]) is not None and self.piece.color != other.color


class Dependent(Move):

	def __init__(self, piece: Piece, square: Square, dependant: Piece):
		super().__init__(piece, square)

		self.dependant = dependant


class Promote(Dependent):

	def __init__(self, pawn: Pawn, square: Square, officer: Officer):
		super().__init__(pawn, square, officer)

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.dependant)

	def __bool__(self) -> bool:
		assert (board := self.piece.game()) is not None
		return self.dependant.square is None and super().__bool__()


class Castle(Dependent):

	def __init__(self, king: King, square: Square, rook: Rook):
		super().__init__(king, square, rook)


class CastleL(Castle):

	def __repr__(self) -> str:
		return "O-O-O"


class CastleS(Castle):

	def __repr__(self) -> str:
		return "O-O"
