from __future__ import annotations


from . import notation
from . import mathematics
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

		if (piece := self[key]) is not None:
			piece.index = None

		if value is not None:
			value.index = key
			value.board = self

		super().__setitem__(key, value)

	def __delitem__(self, key: int):
		self[key] = None


	def get(self, key: int, /) -> str:
		if (piece := self[key]) is None:
			return "-"

		return repr(piece)

	def set(self, key: int, value: str, /):
		self[key] = material.Piece.fromnotation(value) if value != "-" else None


class Side(mathematics.collection[material.Piece]):

	def __init__(self, *pieces: material.Piece,
		game: Game,
	):
		super().__init__(*pieces)

		self.game = game


	@property
	def color(self) -> geometry.Color:
		return geometry.Color.WHITE if self is self.game.white else geometry.Color.BLACK

	@property
	def other(self) -> Side:
		return self.game.black if self is self.game.white else self.game.white


class Game(Board):

	def __init__(self, forsyth_edwards: str, /):
		self.white = Side(game = self)
		self.black = Side(game = self)

		super().__init__(forsyth_edwards)

		for piece in self:
			if piece is not None:
				(self.white if piece.color else self.black).add(piece)
