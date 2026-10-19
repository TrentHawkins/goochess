from __future__ import annotations

import typing

from .geometry import index, Index
if typing.TYPE_CHECKING: from .engine import Game, Side
if typing.TYPE_CHECKING: from .material import Piece


class Move(index[2, 8]):

	action: str = ""


	def __new__(cls, x: int, /, piece: Piece) -> typing.Self:
		return super().__new__(cls, x)

	def __init__(self, x: int, piece: Piece) -> None:
		if (source := piece.square) is None:
			raise ValueError("a piece must have a valid index before creating a move")

		super().__init__()

		self.piece = piece
		self.other = self.piece.game[self.target]

		self.source = source

	def __repr__(self) -> str:
		piece = str(self.piece).upper().replace("P", "") or (self.source.file if self.action else "")

		return piece + self.action + str(self.target)

	def __bool__(self) -> bool:
		return self.piece.game[self.target] is None


	@property
	def target(self) -> Index:
		return Index(int(self))


class Capt(Move):

	action: str = "x"


	def __bool__(self) -> bool:
		return (other := self.piece.game[self.target]) is not None and other.color != self.piece.color


class Spec(Move):

	...


class Rush(Spec):

	def __bool__(self) -> bool:
		return super().__bool__() and not self.piece.moved and self.piece.game[self.middle] is None


	@property
	def middle(self) -> Index:
		return self.source.middle(self.target)
