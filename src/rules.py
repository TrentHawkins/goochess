from __future__ import annotations


from abc import ABC, abstractmethod
from itertools import cycle
from functools import cached_property
from typing import TYPE_CHECKING, Self, cast

import pygame

import src.theme
import src.algebra

if TYPE_CHECKING: import src.material
if TYPE_CHECKING: import src.engine


class Base(ABC):

	def __init__(self,side: src.engine.Side):
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
	def game(self) -> src.engine.Game:
		return self.side.game

	@property
	def king(self) -> src.material.King | None:
		return self.side.king


class Move(Base, src.algebra.square):

	highlight_color = src.theme.GREEN
	symbol = "∘"


	def __init__(self, square: src.algebra.Square, piece: src.material.Piece):
		super(Base, self).__init__(square)

		self.source = piece.square
		self.target = src.algebra.Square(square)

		self.piece = piece
		self.other = self.game[self.target]

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + self.symbol + repr(self.target)

	def __call__(self) -> Self:
		self.piece(self.target)

		return self

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is None or isinstance(other, src.material.Ghost)

	def __enter__(self) -> Self:
		with self.game.dry_run:
			self.piece(self.target)

		return self

	def __exit__(self,
		exc_type: type[Base] | None,
		exc_value: Base | None,
		traceback: Base | None,
	):
		assert self.source is not None

		with self.game.dry_run:
			self.piece(self.source,
				kept = self.other,
			)

		self.other = None


	@property
	def side(self) -> src.engine.Side:
		return self.piece.side

#	@property
#	def source(self) -> src.algebra.Square:
#		return self.piece.square

#	@property
#	def target(self) -> src.algebra.Square:
#		return src.algebra.Square(self)


class Capt(Move):

	highlight_color = src.theme.RED
	symbol = "×"


	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is not None and self.piece.color != other.color


	def highlight(self, screen: pygame.Surface, **kwargs):
		assert self.other is not None
		return super().highlight(screen,
			width = self.other.width,
			thick = 8,
		)


class Spec(Move):

	highlight_color = src.theme.BLUE


class Mod(Move):

    def __new__(cls, move: Move):
        modded_cls = type(cls.__name__, (cls, move.__class__), {})

        return super().__new__(cast(type[Self], modded_cls), move.target, move.piece)

    def __init__(self, move: Move):
        super().__init__(move.target, move.piece)


class Rush(Spec):

	def __init__(self, square: src.algebra.Square, piece: src.material.Piece):
		super().__init__(square, piece)

		assert self.source is not None; self.middle = self.source + src.algebra.Vector.S * self.side.color

	def __call__(self) -> Self:
		self.side.ghost = self.game[self.middle] = src.material.Ghost(self.game, self.side.color)

		return super().__call__()

	def __bool__(self) -> bool:
		return not self.piece.moved and super().__bool__()


class EnPassant(Mod, Capt):

	def __init__(self, move: Move):
		super().__init__(move)

		assert self.source is not None; self.middle = self.target + src.algebra.Vector.S * self.side.other.color

	def __call__(self) -> Self:
		del self.game[self.middle]

		return super().__call__()

	def __bool__(self) -> bool:
		return self.other is not None and isinstance(self.other, src.material.Ghost) and super().__bool__()


	def highlight(self, screen: pygame.Surface, **kwargs):
		super().highlight(screen, **kwargs)

		if self.other is not None:
			self.other.ghost = 1

		#	if (piece := self.game[self.middle]) is not None:
		#		piece.ghost = 2


class Promotion(Mod):

	def __init__(self, move: Move):
		super().__init__(move)

		self.officer = next(self.officers)

	def __call__(self) -> Self:
		super().__call__()

		if isinstance(self.piece, src.material.Pawn):
			self.piece.promote(self.officer)

		return self

	def __repr__(self) -> str:
		return super().__repr__() + repr(self.officer.value.forsyth_edwards)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


	@cached_property
	def officers(self) -> cycle[src.material.Officer]:
		assert isinstance(self.piece, src.material.Pawn)
		return cycle(src.material.Officer)


class Cast(Spec, ABC):

	capts: src.algebra.Vectors
	moves: src.algebra.Vectors


	def __bool__(self) -> bool:
		return self.king is not None and not self.king.moved and not self.rook.moved and self.king.safe \
		and all(self.game[self.king.square + move]    is None                    for move in self.moves) \
		and all(          self.king.square + capt not in self.side.other.targets for capt in self.capts)


	@property
	@abstractmethod
	def rook(self) -> src.material.Rook:
		...


class CastWest(Cast):

	capts = src.algebra.Vectors(
		src.algebra.Vector.W ,
		src.algebra.Vector.W2,
	)
	moves = capts | src.algebra.Vectors(
		src.algebra.Vector.W3,
	)


	def __repr__(self) -> str:
		return "O-O-O"


	@property
	def rook(self) -> src.material.Rook | None:
		return self.side.arook


class CastEast(Cast):

	capts = src.algebra.Vectors(
		src.algebra.Vector.E ,
		src.algebra.Vector.E2,
	)
	moves = capts


	def __repr__(self) -> str:
		return "O-O"


	@property
	def rook(self) -> src.material.Rook | None:
		return self.side.hrook


def specialize(move: Move, *mods: type[Mod]) -> Move:
	for mod in mods:
		if modded := mod(move):
			move = modded

	return move
