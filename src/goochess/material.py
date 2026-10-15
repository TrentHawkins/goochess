from __future__ import annotations


import typing

from .geometry import Color, Index
if typing.TYPE_CHECKING: from .engine import Board

class Piece:

	def __init__(self,
		board: Board,
		color: Color,
		index: Index | None = None,
	) -> None:
		self.board = board
		self.color = color
		self.index = index


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
