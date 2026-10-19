from __future__ import annotations


from .mathematics import collection
from .geometry import Square, Color
from .material import Piece


class Board(list[Piece | None]):

	def __init__(self, forsyth_edwards: str, /):
		...

	def __repr__(self) -> str:
		...

	def __setitem__(self, key: Square, value: Piece | None):
		if value is not None:
			value.square = key

		super().__setitem__(key, value)

	def __delitem__(self, key: Square):
		if (piece := self[key]) is not None:
			piece.square = None

		super().__setitem__(key, None)


class Side(collection[Piece]):

	def __init__(self, *pieces: Piece,
		game: Game,
	):
		super().__init__(*pieces)

		self.game = game


	@property
	def color(self) -> Color:
		return Color.WHITE if self is self.game.white else Color.BLACK

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
