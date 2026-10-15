from __future__ import annotations


from .geometry import index, Index
from .engine import Board
from .material import Piece


class Move(index):

	def __init__(self, _: index, piece: Piece):
		if (source := self.piece.index) is None:
			raise ValueError("a piece must have a valid index before creating a move")

		super().__init__()

		self.piece = piece
		self.source = source

	def __repr__(self) -> str:
		raise NotImplementedError("algebraic representation will go here")

	def __bool__(self) -> bool:
		raise NotImplementedError("probably validate move here")

	def __hash__(self) -> str:
		raise NotImplementedError("probably hash on algebraic representation")

	def __eq__(self, other: object) -> bool:
		raise NotImplementedError("sync with hash or the other way around")


	@property
	def target(self) -> Index:
		return Index(self)

	@property
	def board(self) -> Board:
		return self.piece.board
