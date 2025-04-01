from __future__ import annotations


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

import chess.algebra

if TYPE_CHECKING: import chess.material
if TYPE_CHECKING: import chess.engine


class Base(ABC):

	def __init__(self,side: chess.engine.Side):
		self.side = side

	@abstractmethod
	def __repr__(self) -> str:
		...

	@abstractmethod
	def __call__(self):
		...

	@abstractmethod
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

		self.kept: chess.material.Piece | None = None

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)

	def __call__(self,
		move: bool = True,
		kept: chess.material.Piece | None = None,
	):
		self.kept = kept
		self.moved = self.moved or move
		self.game[self.source], self.game[self.target] = self.kept, self.game[self.source]

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is None or isinstance(other, chess.material.Ghost)

	def __enter__(self) -> Self:
		self.kept = self.game[self.target]
		self(
			move = False,
			kept = self.kept,
		)

		return self

	def __exit__(self, *args):
		self(
			move = False,
			kept = self.kept,
		)


	@property
	def side(self) -> chess.engine.Side:
		return self.piece.side

	@property
	def source(self) -> chess.algebra.Square:
		assert self.piece.square is not None
		return self.piece.square

	@property
	def step(self) -> chess.algebra.Vector:
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

	def __init__(self, piece: chess.material.Piece, square: chess.algebra.Square):
		super().__init__(piece, square)

	def __call__(self):
		self.piece.move(self.target)
		self.game[self.middle] = chess.material.Piece(self.side)

	def __bool__(self) -> bool:
		self.middle = self.source + (self.target - self.source) // 2

		return self.source != self.middle \
			and bool(Move(self.piece, self.middle)) \
			and bool(Move(self.piece, self.target))


class Promote(Move):

	def __init__(self, rank: type[chess.material.Officer]):
		self.rank = rank

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.rank)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


class Castle(Base, ABC):

	steps = chess.algebra.Vectors(
		capts = {
			chess.algebra.Vector.O
		},
	)


	def __bool__(self) -> bool:
		assert self.king.square is not None
		return self.rook.square is not None and not self.rook.moved \
			and all(self.game[self.king.square + move]    is None                    for move in self.steps.moves) \
			and all(          self.king.square + capt not in self.side.other.targets for capt in self.steps.capts)


	@property
	@abstractmethod
	def rook(self) -> chess.material.Rook:
		...


class CastleWest(Castle):

	steps = Castle.steps | chess.algebra.Vectors(
		moves = {
			chess.algebra.Vector.W ,
			chess.algebra.Vector.W2,
		},
	) | chess.algebra.Vectors(
		capts = {
			chess.algebra.Vector.W3,
		},
	)


	def __repr__(self) -> str:
		return "O-O-O"

	def __call__(self):
		assert self.king.square is not None; self.king.move(self.king.square + chess.algebra.Vector.W2)
		assert self.rook.square is not None; self.rook.move(self.rook.square + chess.algebra.Vector.E2)


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.west_rook


class CastleEast(Castle):

	steps = Castle.steps | chess.algebra.Vectors(
		moves = {
			chess.algebra.Vector.E ,
			chess.algebra.Vector.E2,
		},
	)


	def __repr__(self) -> str:
		return "O-O"

	def __call__(self):
		assert self.king.square is not None; self.king.move(self.king.square + chess.algebra.Vector.E2)
		assert self.rook.square is not None; self.rook.move(self.rook.square + chess.algebra.Vector.W2)


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.east_rook
