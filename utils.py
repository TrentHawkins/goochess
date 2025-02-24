from __future__ import annotations


import itertools
import typing


class SummableHashable(typing.Hashable, typing.Protocol):

	def __add__(self, other: typing.Self) -> typing.Self:
		...


class Set[T: SummableHashable]:

	def __init__(self, *,
		moves: set[T] = set(),
		capts: set[T] = set(),
	):
		self.moves = moves if moves else capts.copy()
		self.capts = capts if capts else moves.copy()

	def  __or__ (self, other: Set[T], /) -> Set[T]: return self.               union(other)
	def  __and__(self, other: Set[T], /) -> Set[T]: return self.        intersection(other)
	def  __sub__(self, other: Set[T], /) -> Set[T]: return self.          difference(other)
	def  __xor__(self, other: Set[T], /) -> Set[T]: return self.symmetric_difference(other)

	def __ior__ (self, other: Set[T], /) -> Set[T]: self.                     update(other); return self
	def __iand__(self, other: Set[T], /) -> Set[T]: self.        intersection_update(other); return self
	def __isub__(self, other: Set[T], /) -> Set[T]: self.          difference_update(other); return self
	def __ixor__(self, other: Set[T], /) -> Set[T]: self.symmetric_difference_update(other); return self

	def __add__(self, other: Set[T], /) -> Set[T]:
		return Set(
			moves = {one + two for one, two in itertools.product(self.moves, other.moves)},
			capts = {one + two for one, two in itertools.product(self.moves, other.moves)},
		)

	def union(self, *others: Set[T]) -> Set[T]:
		return Set(
			moves = self.moves.union(*(other.moves for other in others)),
			capts = self.capts.union(*(other.capts for other in others)),
		)

	def intersection(self, *others: Set[T]) -> Set[T]:
		return Set(
			moves = self.moves.intersection(*(other.moves for other in others)),
			capts = self.capts.intersection(*(other.capts for other in others)),
		)

	def difference(self, *others: Set[T]) -> Set[T]:
		return Set(
			moves = self.moves.difference(*(other.moves for other in others)),
			capts = self.capts.difference(*(other.capts for other in others)),
		)

	def symmetric_difference(self, *others: Set[T]) -> Set[T]:
		return Set(
			moves = self.moves.symmetric_difference(*(other.moves for other in others)),
			capts = self.capts.symmetric_difference(*(other.capts for other in others)),
		)

	def update(self, *others: Set[T]):
		self.moves.update(*(other.moves for other in others))
		self.capts.update(*(other.capts for other in others))

	def intersection_update(self, *others: Set[T]):
		self.moves.intersection_update(*(other.moves for other in others))
		self.capts.intersection_update(*(other.capts for other in others))

	def difference_update(self, *others: Set[T]):
		self.moves.difference_update(*(other.moves for other in others))
		self.capts.difference_update(*(other.capts for other in others))

	def symmetric_difference_update(self, *others: Set[T]):
		self.moves.symmetric_difference_update(*(other.moves for other in others))
		self.capts.symmetric_difference_update(*(other.capts for other in others))

	def add(self, other: T):
		self.moves.add(other)
		self.capts.add(other)

	def remove(self, other: T):
		self.moves.remove(other)
		self.capts.remove(other)

	def discard(self, other: T):
		self.moves.discard(other)
		self.capts.discard(other)

	def sum(self, *others: Set[T]) -> Set[T]:
		return Set(
			moves = {sum(twos, start = one) for one, *twos in itertools.product(self.moves, *(other.moves for other in others))},
			capts = {sum(twos, start = one) for one, *twos in itertools.product(self.capts, *(other.capts for other in others))},
		)
