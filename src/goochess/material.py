from __future__ import annotations


from .geometry import Square
from .engine import Board


class Piece:

	def __init__(self,
		square: Square | None = None,
		board: Board | None = None,
	) -> None:
		self.square = square
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
