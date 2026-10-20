from __future__ import annotations


from . import notation
from . import mathematics
from . import geometry
from . import material


class Board(list[material.Piece | None]):

	def __init__(self, forsyth_edwards: str, /):
		super().__init__([material.Piece.from_symbol(piece) if piece != "-" else None for piece in notation.board(forsyth_edwards)])

	def __repr__(self) -> str:
		return str(notation.serial("".join(map(self.piece, geometry.Square))))

	def __setitem__(self, key: geometry.Square, value: material.Piece | None):
		if value is not None:
			value.square = key

		super().__setitem__(key, value)

	def __delitem__(self, key: geometry.Square):
		if (piece := self[key]) is not None:
			piece.square = None

		super().__setitem__(key, None)


	def piece(self, square: geometry.Square, /) -> str:
		if (piece := self[square]) is None:
			return "-"

		return repr(piece)


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
				piece.side.add(piece)
