from __future__ import annotations


import typing

from .geometry import Color, Index
if typing.TYPE_CHECKING: from .engine import Board

class Piece:

	white: str
	black: str


	def __init__(self,
		board: Board,
		color: Color,
		index: Index | None = None,
	) -> None:
		self.board = board
		self.color = color
		self.index = index

	def __repr__(self) -> str:
		return self.white if self.color else self.black


class Pawn(Piece):

	white: str = ""  # "♙"
	black: str = ""  # "♟"


class Melee(Piece):

	...


class Ranged(Piece):

	...


class Officer(Piece):

	...


class Rook(Melee, Officer):

	white: str = "R"  # "♖"
	black: str = "r"  # "♜"


class Bishop(Melee, Officer):

	white: str = "B"  # "♗"
	black: str = "b"  # "♝"


class Knight(Melee, Officer):

	white: str = "N"  # "♘"
	black: str = "n"  # "♞"


class Queen(Ranged, Officer):

	white: str = "Q"  # "♕"
	black: str = "q"  # "♛"


class King(Melee):

	white: str = "K"  # "♔"
	black: str = "k"  # "♚"
