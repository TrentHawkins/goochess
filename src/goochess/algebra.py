from __future__ import annotations

import typing

from . import mathematics
from . import geometry
from . import material


class Move(mathematics.index[2, 8]):

	action: str = ""


	def __new__(cls, x: int, /, piece: material.Piece) -> typing.Self:
		return super().__new__(cls, x)

	def __init__(self, x: int, piece: material.Piece) -> None:
		if (source := piece.square) is None:
			raise ValueError("a piece must have a valid index before creating a move")

		super().__init__()

		self.piece = piece
		self.other = self.piece.game[self.target]

		self.source = source

	def __repr__(self) -> str:
		piece = self.piece.white.replace("P", "") or (self.source.file if self.action else "")

		return piece + self.action + str(self.target)

	def __bool__(self) -> bool:
		return self.piece.game[self.target] is None


	@property
	def target(self) -> geometry.Square:
		return geometry.Square(int(self))


class Capt(Move):

	action: str = "x"


	def __bool__(self) -> bool:
		return (other := self.piece.game[self.target]) is not None and other.color != self.piece.color


class Spec(Move):

	...


class Rush(Spec):

	def __bool__(self) -> bool:
		return super().__bool__() and not self.piece.moved and self.piece.game[self.middle] is None


	@property
	def middle(self) -> geometry.Square:
		return self.source.middle(self.target)


class Promotion(Spec):

	to: material.Officer = material.Officer.Q


	def __repr__(self) -> str:
		return super().__repr__() + "=" + self.to.name

	def __bool__(self) -> bool:
		return isinstance(self.piece, material.Pawn) and super().__bool__() and self.source.rank == (7 if self.piece.color else 2)


class EnPassant(Capt):

	def __bool__(self) -> bool:
		other = self.piece.game[self.target]

		return isinstance(self.piece, material.Pawn) and \
			isinstance(other, material.Ghost) and super().__bool__() and self.source.rank == (5 if self.piece.color else 4)


class Check(Move):

	def __repr__(self) -> str:
		return super().__repr__() + "+"


class Checkmate(Check):

	def __repr__(self) -> str:
		return super().__repr__().replace("+", "#")
