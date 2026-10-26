from __future__ import annotations


import contextlib
import functools
import itertools
import typing

from . import structs
from . import mathematics
from . import geometry
from . import material
if typing.TYPE_CHECKING: from . import engine


class Move(mathematics.index[2, 8]):

	action: str = ""


	def __new__(cls, x: int, /, piece: material.Piece) -> typing.Self:
		return super().__new__(cls, x)

	def __init__(self, x: int, piece: material.Piece) -> None:
		assert (source := piece.index) is not None

		super().__init__()

		self.piece = piece
		self.other = self.position[self.target]

		self.source = source

	def __repr__(self) -> str:
		piece = self.piece.white.replace("P", "") or (self.source.file if self.action else "")

		return piece + self.action + str(self.target)

	def __bool__(self) -> bool:
		return self.position[self.target] is None

	def __call__(self) -> typing.Self:
		assert self.piece.index == self.source and self.position[self.target] is self.other

		self.piece(self.target)

		return self

	@property
	@contextlib.contextmanager
	def simulated(self) -> typing.Generator[typing.Self]:
		assert self.piece.index == self.source and self.position[self.target] is self.other

		moved = self.piece.moved
		self.piece(self.target)

		try: yield self
		finally: self.piece(self.source,
			kept = self.other,
			moved = moved,
		)

	@property
	def target(self) -> geometry.Index:
		return geometry.Index(int(self))

	@property
	def position(self) -> engine.Position:
		return self.piece.position


class Capt(Move):

	action: str = "x"


	def __bool__(self) -> bool:
		return (other := self.position[self.target]) is not None and other.color != self.piece.color


class Spec(Move):

	...


class Rush(Spec):

	piece: material.Pawn


	def __bool__(self) -> bool:
		return super().__bool__() and not self.piece.moved and self.position[self.middle] is None

	def __call__(self) -> typing.Self:
		super().__call__()

		self.position[self.middle] = material.Ghost(self.piece)

		return self

	@property
	@contextlib.contextmanager
	def simulated(self) -> typing.Generator[typing.Self]:
		with super().simulated:
			self.position[self.middle] = material.Ghost(self.piece)

			try: yield self
			finally: del self.position[self.middle]

	@property
	def middle(self) -> geometry.Index:
		return self.source.middle(self.target)


class Promotion(Spec):

	def __class_getitem__(cls, item: type[Move], /) -> type[Promotion]:
		if item is Move: return PromotionMove
		if item is Capt: return PromotionCapt

		raise TypeError(f"{cls.__name__} expects Move or Capt")

	def __init__(self, x: int, piece: material.Pawn) -> None:
		assert isinstance(piece, material.Pawn)
		super().__init__(x, piece)

		self.to = next(self.officers)

	def __repr__(self) -> str:
		return super().__repr__() + "=" + self.to.name

	def __bool__(self) -> bool:
		return super().__bool__() and self.source.rank == (2 if self.piece.color else 7)


	@functools.cached_property
	def officers(self) -> itertools.cycle[material.Officer]:
		return itertools.cycle(material.Officer)


class PromotionMove(Promotion, Move): ...
class PromotionCapt(Promotion, Capt): ...


class EnPassant(Capt):

	other: material.Ghost


	def __init__(self, x: int, piece: material.Pawn) -> None:
		super().__init__(x, piece)

		assert isinstance(self.piece, material.Pawn )
		assert isinstance(self.other, material.Ghost)

	def __call__(self) -> typing.Self:
		assert self.position[self.middle] is self.other.rusher

		super().__call__()

		del self.position[self.middle]

		return self

	@property
	@contextlib.contextmanager
	def simulated(self) -> typing.Generator[typing.Self]:
		assert self.position[self.middle] is self.other.rusher

		with super().simulated:
			del self.position[self.middle]

			try: yield self
			finally: self.position[self.middle] = self.other.rusher

	def __bool__(self) -> bool:
		return super().__bool__() and self.position[self.middle] is self.other.rusher and \
			self.source.rank == (4 if self.piece.color else 5) and \
			self.target.rank == (3 if self.piece.color else 6)


	@property
	def middle(self) -> geometry.Index:
		return geometry.Index.from_sequence((self.target[0], self.source[1]))  # pylint: disable = no-member


class Check(Move):

	def __repr__(self) -> str:
		return super().__repr__() + "+"


class Checkmate(Check):

	def __repr__(self) -> str:
		return super().__repr__().replace("+", "#")


class Moves(structs.collection[Move]): ...
