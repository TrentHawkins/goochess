from __future__ import annotations


import functools
import itertools
import typing

from . import mathematics
from . import geometry
from . import material


class Move(mathematics.index[2, 8]):

	action: str = ""


	def __new__(cls, x: int, /, piece: material.Piece) -> typing.Self:
		return super().__new__(cls, x)

	def __init__(self, x: int, piece: material.Piece) -> None:
		assert (source := piece.index) is not None

		super().__init__()

		self.piece = piece
		self.other = self.piece.position[self.target]

		self.source = source

	def __repr__(self) -> str:
		piece = self.piece.white.replace("P", "") or (self.source.file if self.action else "")

		return piece + self.action + str(self.target)

	def __bool__(self) -> bool:
		return self.piece.position[self.target] is None

	def __call__(self) -> typing.Self:
		self.piece(self.target)
		self.piece.moved = True

		return self

	def __enter__(self) -> typing.Self:
		assert self.piece.index == self.source and self.piece.position[self.target] is self.other
		self.piece(self.target)

		return self

	def __exit__(self, *_) -> None:
		self.piece(self.source, self.other)


	@property
	def target(self) -> geometry.Index:
		return geometry.Index(int(self))


class Capt(Move):

	action: str = "x"


	def __bool__(self) -> bool:
		return (other := self.piece.position[self.target]) is not None and other.color != self.piece.color


class Spec(Move):

	...


class Rush(Spec):

	def __bool__(self) -> bool:
		return super().__bool__() and not self.piece.moved and self.piece.position[self.middle] is None


	@property
	def middle(self) -> geometry.Index:
		return self.source.middle(self.target)


class Promotion(Spec):

	def __class_getitem__(cls, item: type[Move], /) -> type[Promotion]:
		if item is Move: return PromotionMove
		if item is Capt: return PromotionCapt

		raise TypeError(f"{cls.__name__} expects Move or Capt")

	def __init__(self, x: int, piece: material.Piece) -> None:
		super().__init__(x, piece)

		self.to = next(self.officers)

	def __repr__(self) -> str:
		return super().__repr__() + "=" + self.to.name

	def __bool__(self) -> bool:
		return super().__bool__() and \
			isinstance(self.piece, material.Pawn ) and self.source.rank == (2 if self.piece.color else 7)


	@functools.cached_property
	def officers(self) -> itertools.cycle[material.Officer]:
		return itertools.cycle(material.Officer)


class PromotionMove(Promotion, Move): ...
class PromotionCapt(Promotion, Capt): ...


class EnPassant(Capt):

	def __init__(self, x: int, piece: material.Piece) -> None:
		super().__init__(x, piece)

		self.victim = self.piece.position[self.middle]

	def __call__(self) -> typing.Self:
		super().__call__()
		del self.piece.position[self.middle]

		return self

	def __bool__(self) -> bool:
		other = self.piece.position[self.target]
		victim = self.piece.position[self.middle]

		return super().__bool__() and \
			isinstance(self.piece, material.Pawn ) and \
			isinstance(     other, material.Ghost) and \
			isinstance(    victim, material.Pawn ) and victim.color != self.piece.color and \
			self.source.rank == (4 if self.piece.color else 5) and \
			self.target.rank == (3 if self.piece.color else 6) and abs(self.target[0] - self.source[0]) == 1

	def __enter__(self) -> typing.Self:
		assert self.piece.position[self.middle] is self.victim
		super().__enter__()
		del self.piece.position[self.middle]

		return self

	def __exit__(self, *args) -> None:
		super().__exit__(*args)
		self.piece.position[self.middle] = self.victim


	@property
	def middle(self) -> geometry.Index:
		return geometry.Index.from_sequence((self.target[0], self.source[1]))  # pylint: disable = no-member


class Check(Move):

	def __repr__(self) -> str:
		return super().__repr__() + "+"


class Checkmate(Check):

	def __repr__(self) -> str:
		return super().__repr__().replace("+", "#")
