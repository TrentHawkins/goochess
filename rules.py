from __future__ import annotations


import abc
import typing

import chess.algebra

if typing.TYPE_CHECKING: import chess.material
if typing.TYPE_CHECKING: import chess.engine


class Base(abc.ABC):

	def __init__(self,side: chess.engine.Side):
		self.side = side

	@abc.abstractmethod
	def __repr__(self) -> str:
		...

	@abc.abstractmethod
	def __call__(self, *args, **kwargs):
		...

	@abc.abstractmethod
	def __bool__(self) -> bool:
		...


	@property
	def game(self) -> chess.engine.Game:
		return self.side.game

	@property
	def king(self) -> chess.material.King:
		return self.side.king


class Move(Base):

	def __init__(self, piece: chess.material.Piece, square: chess.algebra.Square):
		self.piece = piece
		self.target = square

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)

	def __call__(self,
		target: chess.algebra.Square | None = None,
	):
		self.piece.move(target if target is not None else self.target)

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is None or isinstance(other, chess.material.Ghost)


	@property
	def side(self) -> chess.engine.Side:
		return self.piece.side

	@property
	def source(self) -> chess.algebra.Square:
		assert self.piece.square is not None
		return self.piece.square

	@property
	def step(self) -> chess.algebra.Vector2:
		return self.target - self.source

	@property
	def with_safe_king(self) -> bool:
		with self.piece.test(self.target):
			return bool(self) and self.king.safe


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


class Castle(Base, abc.ABC):

	steps: set[chess.algebra.Vector] = {
		chess.algebra.Vector.O,
	}


	def __bool__(self) -> bool:
		assert self.king.square is not None
		return \
			not self.king.moved and \
			not self.rook.moved and all(self.king.square + step not in self.side.other.targets.capts for step in self.steps)


	@property
	@abc.abstractmethod
	def rook(self) -> chess.material.Rook:
		...


class CastleWest(Castle):

	steps = Castle.steps | {
		chess.algebra.Vector.W ,
		chess.algebra.Vector.W2,
	}


	def __repr__(self) -> str:
		return "O-O-O"

	def __call__(self):
		assert self.king.square is not None; self.king.move(self.king.square + chess.algebra.Vector.W2)
		assert self.rook.square is not None; self.rook.move(self.rook.square + chess.algebra.Vector.E2)

	def __bool__(self) -> bool:
		return super().__bool__() and self.rook.square is not None and \
			bool(Move(self.rook, self.rook.square + chess.algebra.Vector.E))


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.west_rook


class CastleEast(Castle):

	steps = Castle.steps | {
		chess.algebra.Vector.E ,
		chess.algebra.Vector.E2,
	}


	def __repr__(self) -> str:
		return "O-O"

	def __call__(self):
		assert self.king.square is not None; self.king.move(self.king.square + chess.algebra.Vector.E2)
		assert self.rook.square is not None; self.rook.move(self.rook.square + chess.algebra.Vector.W2)

	def __bool__(self) -> bool:
		return super().__bool__() and self.rook.square is not None


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.east_rook
