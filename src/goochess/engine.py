from __future__ import annotations


import contextlib
import typing

from . import structs
from . import mathematics
from . import notation
from . import geometry
from . import material


class Board(list[material.Piece | None]):

	def __init__(self, forsyth_edwards: str, /):
		super().__init__([None] * len(geometry.Index))

		for item in enumerate(notation.serial(forsyth_edwards)):
			self.set(*item)

	def __repr__(self) -> str:
		return str(notation.serial("".join(map(self.get, geometry.Index))))

	def __setitem__(self, key: int, value: material.Piece | None):
		key = geometry.Index(key)

		with self.binding(key, value):
			super().__setitem__(key, value)

	def __delitem__(self, key: int):
		self[key] = None


	@contextlib.contextmanager
	def binding(self, key: geometry.Index,
		value: material.Piece | None,
	) -> typing.Generator:
		if (piece := self[key]) is not None:
			piece.index = None

		yield

		if value is not None:
			value.index = key


	def get(self, key: int, /) -> str:
		if (piece := self[geometry.Index(key)]) is None:
			return "-"

		return repr(piece)

	def set(self, key: int, value: str, /):
		self[geometry.Index(key)] = material.Piece.fromnotation(value) if value != "-" else None


class Side(set[material.Piece]):

	position: Position
	king: material.King


	def __init__(self, position: Position, /, *pieces: material.Piece):
		self.position = position

		super().__init__(pieces)

	def __bool__(self) -> bool:
		return self is self.position.black


	@property
	def other(self) -> Side:
		return self.position.side[not self]

	@property
	def targets(self) -> mathematics.indices:
		return mathematics.indices().union(*(piece.targets for piece in self))


class Position(Board):

	def __init__(self, forsyth_edwards: str, /):
		self.side = structs.switch(
			Side(self),  # white
			Side(self),  # black
		)

		super().__init__(forsyth_edwards)

		for piece in self:
			if isinstance(piece, material.King):
				piece.side.king = piece


	@contextlib.contextmanager
	def binding(self, key: geometry.Index,
		value: material.Piece | None,
	) -> typing.Generator:
		if (piece := self[key]) is not None:
			piece.side.discard(piece)

		with super().binding(key, value):
			yield

		if value is not None:
			value.position = self
			value.side.add(value)

	@property
	def white(self) -> Side:
		return self.side[False]  # white

	@property
	def black(self) -> Side:
		return self.side[True]  # black
