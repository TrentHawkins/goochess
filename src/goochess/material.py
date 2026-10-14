from __future__ import annotations


from .geometry import Color, Index
from .engine import Board


class Piece:

	def __init__(self,
		color: Color              ,
		index: Index | None = None,
		board: Board | None = None,
	) -> None:
		self.color = color
		self.index = index
		self.board = board


class Pawn(Piece):

	...


class Melee(Piece):

	...


class Ranged(Piece):

	...


class Officer(Piece):

	...


class Rook(Melee, Officer):

	...


class Bishop(Melee, Officer):

	...


class Knight(Melee, Officer):

	...


class Queen(Ranged, Officer):

	...


class King(Melee):

	...
