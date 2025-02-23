from __future__ import annotations


import typing

from chess.theme import Theme, DEFAULT
from chess.algebra import Color, Rank, File, Difference, Square, Difference
from chess.material import Piece, Pawn, Rook, Bishop, Knight, Queen, King
from chess.rules import Move, Capt, CastleLong, CastleShort
from chess.engine import Game, Side, Game


class Set[T: typing.Hashable]:

	def __init__(self,
		moves: set[T] = set(),
		capts: set[T] = set(),
		specs: set[T] = set(),
	):
		self.moves = moves
		self.capts = capts if capts else self.moves
		self.specs = specs

	def __or__ (self, other: Set[T], /) -> Set[T]: return self.               union(other)
	def __and__(self, other: Set[T], /) -> Set[T]: return self.        intersection(other)
	def __sub__(self, other: Set[T], /) -> Set[T]: return self.          difference(other)
	def __xor__(self, other: Set[T], /) -> Set[T]: return self.symmetric_difference(other)

	def __ior__ (self, other: Set[T], /): self.                     update(other); return self
	def __iand__(self, other: Set[T], /): self.        intersection_update(other); return self
	def __isub__(self, other: Set[T], /): self.          difference_update(other); return self
	def __ixor__(self, other: Set[T], /): self.symmetric_difference_update(other); return self


	def union(self, *others: Set[T]) -> Set[T]:
		return Set[T](
			self.moves.union(*(other.moves for other in others)),
			self.capts.union(*(other.capts for other in others)),
			self.specs.union(*(other.specs for other in others)),
		)

	def intersection(self, *others: Set[T]) -> Set[T]:
		return Set[T](
			self.moves.intersection(*(other.moves for other in others)),
			self.capts.intersection(*(other.capts for other in others)),
			self.specs.intersection(*(other.specs for other in others)),
		)

	def difference(self, *others: Set[T]) -> Set[T]:
		return Set[T](
			self.moves.difference(*(other.moves for other in others)),
			self.capts.difference(*(other.capts for other in others)),
			self.specs.difference(*(other.specs for other in others)),
		)

	def symmetric_difference(self, *others: Set[T]) -> Set[T]:
		return Set[T](
			self.moves.symmetric_difference(*(other.moves for other in others)),
			self.capts.symmetric_difference(*(other.capts for other in others)),
			self.specs.symmetric_difference(*(other.specs for other in others)),
		)

	def update(self, *others: Set[T]):
		self.moves.update(*(other.moves for other in others))
		self.capts.update(*(other.capts for other in others))
		self.specs.update(*(other.specs for other in others))

	def intersection_update(self, *others: Set[T]):
		self.moves.intersection_update(*(other.moves for other in others))
		self.capts.intersection_update(*(other.capts for other in others))
		self.specs.intersection_update(*(other.specs for other in others))

	def difference_update(self, *others: Set[T]):
		self.moves.difference_update(*(other.moves for other in others))
		self.capts.difference_update(*(other.capts for other in others))
		self.specs.difference_update(*(other.specs for other in others))

	def symmetric_difference_update(self, *others: Set[T]):
		self.moves.symmetric_difference_update(*(other.moves for other in others))
		self.capts.symmetric_difference_update(*(other.capts for other in others))
		self.specs.symmetric_difference_update(*(other.specs for other in others))
