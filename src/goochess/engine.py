from __future__ import annotations


from . import notation
from . import mathematics
from . import geometry
from . import material


class Board(list[material.Piece | None]):

	def __init__(self, forsyth_edwards: str, /):
		self.white = Side(); self.white.board = self
		self.black = Side(); self.black.board = self

		super().__init__([None] * len(geometry.Index))

		for item in enumerate(notation.serial(forsyth_edwards)):
			self.set(*item)

		for piece in self:
			if isinstance(piece, material.King):
				piece.side.king = piece

	def __repr__(self) -> str:
		return str(notation.serial("".join(map(self.get, geometry.Index))))

	def __setitem__(self, key: int, value: material.Piece | None):
		key = geometry.Index(key)

		if (piece := self[key]) is not None:
			piece.side.discard(piece)
			piece.index = None

		if value is not None:
			value.index = key
			value.side.add(value)

		super().__setitem__(key, value)

	def __delitem__(self, key: int):
		self[key] = None


	def get(self, key: int, /) -> str:
		if (piece := self[geometry.Index(key)]) is None:
			return "-"

		return repr(piece)

	def set(self, key: int, value: str, /):
		self[geometry.Index(key)] = material.Piece.fromnotation(value, self) if value != "-" else None

	def empty(self, key: int, /) -> bool:
		return (piece := self[geometry.Index(key)]) is None or isinstance(piece, material.Ghost)


class Side(set[material.Piece]):

	board: Board
	king: material.King


	def __init__(self, *pieces: material.Piece):
		super().__init__(pieces)


	def __bool__(self) -> bool:
		return self is self.board.white

	@property
	def other(self) -> Side:
		return self.board.black if self else self.board.white

	@property
	def forward(self) -> mathematics.array:
		return geometry.Compass.north if self else geometry.Compass.south


class Game(Board):

	...
