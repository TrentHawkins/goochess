from __future__ import annotations

import typing

from .geometry import index, Index

if typing.TYPE_CHECKING: from .engine import Board
if typing.TYPE_CHECKING: from .material import Piece


class Move(index[2, 8]):

	def __new__(cls, x: int, /, piece: Piece) -> typing.Self:
		return super().__new__(cls, x)

	def __init__(self, x: int, piece: Piece) -> None:
		if (source := piece.index) is None:
			raise ValueError("a piece must have a valid index before creating a move")

		super().__init__()

		self.piece = piece
		self.source = source

	def __repr__(self) -> str:
		raise NotImplementedError("algebraic representation will go here")

	def __bool__(self) -> bool:
		raise NotImplementedError("probably validate move here")

	def __hash__(self) -> int:
		return hash(
			(type(self.piece),
				self.source,
				self.target,
			)
		)

	def __eq__(self, other: object) -> bool:
		raise NotImplementedError("sync with hash or the other way around")

	def __ne__(self, other: object) -> bool:
		return not self == other


	@property
	def target(self) -> Index:
		return Index(int(self))

	@property
	def board(self) -> Board:
		return self.piece.board
