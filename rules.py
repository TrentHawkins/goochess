from __future__ import annotations


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

import pygame

import chess.theme
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
	def __call__(self) -> Self:
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


class Move(Base, chess.algebra.square):

	highlight_color = chess.theme.GREEN


	def __init__(self, square: chess.algebra.Square, piece: chess.material.Piece):
		super(Base, self).__init__(square)

		self.source = piece.square
		self.target = chess.algebra.Square(square)

		self.piece = piece
		self.other = self.game[self.target]

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)

	def __call__(self):
		self.piece(self.target)

		return self

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is None or isinstance(other, chess.material.Ghost)

	def __enter__(self) -> Self:
		self.piece(self.target,
			move = False,
		)

		return self

	def __exit__(self,
		exc_type: type[Base] | None,
		exc_value: Base | None,
		traceback: Base | None,
	):
		assert self.source is not None

		self.piece(self.source,
			move = False,
			kept = self.other,
		)
		self.other = None


	@property
	def side(self) -> chess.engine.Side:
		return self.piece.side

#	@property
#	def source(self) -> chess.algebra.Square:
#		assert self.piece.square is not None
#		return self.piece.square

#	@property
#	def target(self) -> chess.algebra.Square:
#		return chess.algebra.Square(self)


	def highlight(self, screen: pygame.Surface,
		width: int = 1,
	):
		return super().highlight(screen, width)


class Capt(Move):

	highlight_color = chess.theme.RED


	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is not None and self.piece.color != other.color


	def highlight(self, screen: pygame.Surface,
		width: int = 1,
	):
		return super().highlight(screen, self.other.width if self.other is not None else width)


class Spec(Move):

	highlight_color = chess.theme.BLUE


class Rush(Spec):

	def __bool__(self) -> bool:
		return not self.piece.moved and super().__bool__()


class EnPassant(Capt):

	def __bool__(self) -> bool:
		return self.other is not None and isinstance(self.other, chess.material.Ghost) and super().__bool__()


class Promote(Spec):

	def __init__(self, officer: type[chess.material.Officer]):
		self.officer = officer

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.rank)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


class Cast(Spec, ABC):

	capts: chess.algebra.Vectors
	moves: chess.algebra.Vectors


	def __bool__(self) -> bool:
		return not self.king.moved and not self.rook.moved and self.king.safe \
		and all(self.game[self.king.square + move]    is None                    for move in self.moves) \
		and all(          self.king.square + capt not in self.side.other.targets for capt in self.capts)


	@property
	@abstractmethod
	def rook(self) -> chess.material.Rook:
		...


class CastWest(Cast):

	capts = chess.algebra.Vectors(
		chess.algebra.Vector.W ,
		chess.algebra.Vector.W2,
	)
	moves = capts | chess.algebra.Vectors(
		chess.algebra.Vector.W3,
	)


	def __repr__(self) -> str:
		return "O-O-O"


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.west_rook


class CastEast(Cast):

	capts = chess.algebra.Vectors(
		chess.algebra.Vector.E ,
		chess.algebra.Vector.E2,
	)
	moves = capts


	def __repr__(self) -> str:
		return "O-O"


	@property
	def rook(self) -> chess.material.Rook:
		return self.side.east_rook
