from __future__ import annotations


from typing import TYPE_CHECKING

from chess.geometry import Difference, Square

if TYPE_CHECKING:
	from chess.material import Piece, Officer, Pawn, Rook, King
	from chess.engine import Game


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = square

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)


	def valid(self, game: Game) -> bool:
		return game[self.target] is None


class Capt(Move):

	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")


	def valid(self, game: Game) -> bool:
		return (other := game[self.target]) is not None and self.piece.color != other.color


class Promote(Move):

	def __init__(self, pawn: Pawn, square: Square, rank: type[Officer]):
		super().__init__(pawn, square)

		self.officer = rank(self.piece.color)

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.officer)


	def valid(self, game: Game) -> bool:
		return self.target.rank.final(self.piece.color) and super().valid(game)


class Castle(Move):

	def __init__(self, king: King, square: Square, rook: Rook):
		super().__init__(king, square)

		self.rook = rook


class CastleL(Move):

	def __init__(self, king: King):
		assert king.square is not None

		super().__init__(king, king.square + Difference.W2)


	def __repr__(self) -> str:
		return "O-O-O"


class CastleS(Castle):

	def __repr__(self) -> str:
		return "O-O"
