from __future__ import annotations


import abc
import typing

import chess.algebra

if typing.TYPE_CHECKING: import chess.material
if typing.TYPE_CHECKING: import chess.engine


class Rule(abc.ABC):

	def __init__(self,side: chess.engine.Side):
		self.side = side

	@abc.abstractmethod
	def __repr__(self) -> str:
		...

	@abc.abstractmethod
	def __bool__(self) -> bool:
		...


	@property
	def game(self) -> chess.engine.Game:
		return self.side.game



class Move(Rule):

	def __init__(self, piece: chess.material.Piece, square: chess.algebra.Square):
		self.piece = piece
		self.target = square


	@property
	def side(self) -> chess.engine.Side:
		return self.piece.side

	@property
	def source(self) -> chess.algebra.Square:
		assert self.piece.square is not None
		return self.piece.square


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


	def __init__(self, rank: type[chess.material.Officer]):
		self.rank = rank


	def __repr__(self) -> str:
		return super().__repr__() + repr(self.rank)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


class Castle(Rule, abc.ABC):

	steps: set[chess.algebra.Difference] = {chess.algebra.Difference.O}
	rook_file: chess.algebra.File


	@property
	def king(self) -> chess.material.King:
		return self.side.king

	@property
	def rook(self) -> chess.material.Rook:
		assert (square := self.king.square) is not None
		assert (rook := self.game[square.rank + self.rook_file]) is not None

		return typing.cast(chess.material.Rook, rook)


	def __bool__(self) -> bool:
		assert self.king.square is not None
		return \
		not self.king.moved and \
		not self.rook.moved and not {self.king.square + step for step in self.steps} & self.side.other.squares.capts


class CastleLong(Castle):

	steps: set[chess.algebra.Difference] = Castle.steps | {chess.algebra.Difference.W, chess.algebra.Difference.W2}
	rook_file: chess.algebra.File = chess.algebra.File.A_


	def __repr__(self) -> str:
		return "O-O-O"


class CastleShort(Castle):

	steps: set[chess.algebra.Difference] = Castle.steps | {chess.algebra.Difference.E, chess.algebra.Difference.E2}
	rook_file: chess.algebra.File = chess.algebra.File.H_


	def __repr__(self) -> str:
		return "O-O"
