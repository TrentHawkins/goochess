from __future__ import annotations


import typing

import chess.geometry

if typing.TYPE_CHECKING: import chess.material
if typing.TYPE_CHECKING: import chess.engine


class Move:

	def __init__(self, piece: chess.material.Piece, square: chess.geometry.Square):
		self.piece = piece

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = square

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)


	def valid(self, game: chess.engine.Game) -> bool:
		return game[self.target] is None


class Capt(Move):

	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")


	def valid(self, game: chess.engine.Game) -> bool:
		return (other := game[self.target]) is not None and self.piece.color != other.color


class Promote(Move):

	def __init__(self, pawn: chess.material.Pawn, square: chess.geometry.Square, rank: type[chess.material.Officer]):
		super().__init__(pawn, square)

		self.officer = rank(self.piece.color)

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.officer)


	def valid(self, game: chess.engine.Game) -> bool:
		return self.target.rank.final(self.piece.color) and super().valid(game)


class Castle(Move):

	def __init__(self, king: chess.material.King, square: chess.geometry.Square, rook: chess.material.Rook):
		super().__init__(king, square)

		self.rook = rook


class CastleL(Move):

	def __init__(self, king: chess.material.King):
		assert king.square is not None

		super().__init__(king, king.square + chess.geometry.Difference.W2)


	def __repr__(self) -> str:
		return "O-O-O"


class CastleS(Castle):

	def __repr__(self) -> str:
		return "O-O"
