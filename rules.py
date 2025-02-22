from __future__ import annotations


import typing

import chess.geometry

if typing.TYPE_CHECKING: import chess.material
if typing.TYPE_CHECKING: import chess.engine


class Rule:

	def __init__(self,
		game: chess.engine.Game,
		side: chess.engine.Side,
	):
		self.game = game
		self.side = side


class Move(Rule):

	def __init__(self,
		piece: chess.material.Piece,
		square: chess.geometry.Square,
	):
		self.piece = piece

		self.game = self.piece.game
		self.side = self.piece.side

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = square

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)

	def __bool__(self) -> bool:
		return self.game[self.target] is None


class Capt(Move):

	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is not None and self.piece.color != other.color


class Rush(Move):

	def __bool__(self) -> bool:
		return not self.piece.moved and super().__bool__()


class Promote(Move):

	rank: type[chess.material.Officer]


	def __repr__(self) -> str:
		return super().__repr__() + repr(self.rank)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


class Castle(Rule):

	steps: set[chess.geometry.Difference]


	def __bool__(self) -> bool:
		assert self.side.king.square is not None
		return not self.side.king.moved and not {self.side.king.square + step for step in self.steps} <= self.side.opponent.squares


class CastleLong(Castle):

	steps: set[chess.geometry.Difference] = {
		chess.geometry.Difference.O,
		chess.geometry.Difference.W, chess.geometry.Difference.W2,
	}

	def __init__(self, *args):
		super().__init__(*args)

		assert self.side.king.square is not None
		self.rook = self.game[chess.geometry.Square(self.side.king.square.rank + chess.geometry.File.A_)]

	def __repr__(self) -> str:
		return "O-O-O"

	def __bool__(self) -> bool:
		return not self.side.left_rook.moved and super().__bool__()


class CastleShort(Castle):

	steps: set[chess.geometry.Difference] = {
		chess.geometry.Difference.O,
		chess.geometry.Difference.E, chess.geometry.Difference.E2,
	}

	def __repr__(self) -> str:
		return "O-O"

	def __bool__(self) -> bool:
		return not self.side.right_rook.moved and super().__bool__()
