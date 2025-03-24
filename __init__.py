from __future__ import annotations


from typing import Iterable, Self


class collection[T]:

	def __init__(self,
		moves: Iterable[T] = [],
		capts: Iterable[T] = [],
		specs: Iterable[T] = [],
	):
		self.moves = set(moves)
		self.capts = set(capts)
		self.specs = set(specs)

	def __len__(self) -> int:
		return len(self.moves) + len(self.capts) + len(self.specs)

	def __iter__(self):
		for move in self.moves: yield move
		for capt in self.capts: yield capt
		for spec in self.specs: yield spec

	def __contains__(self, item: T) -> bool:
		return \
			item in self.moves or \
			item in self.capts or \
			item in self.specs

	def  __or__(self, other: Self, /) -> Self: return self.               union(other)
	def __and__(self, other: Self, /) -> Self: return self.        intersection(other)
	def __sub__(self, other: Self, /) -> Self: return self.          difference(other)
	def __xor__(self, other: Self, /) -> Self: return self.symmetric_difference(other)

	def  __ror__(self, other: Self, /) -> Self: return self | other
	def __rand__(self, other: Self, /) -> Self: return self & other
	def __rsub__(self, other: Self, /) -> Self: return self - other
	def __rxor__(self, other: Self, /) -> Self: return self ^ other

	def  __ior__(self, other: Self, /): self.                     update(other); return self
	def __iand__(self, other: Self, /): self.        intersection_update(other); return self
	def __isub__(self, other: Self, /): self.          difference_update(other); return self
	def __ixor__(self, other: Self, /): self.symmetric_difference_update(other); return self

	def __le__(self, other: Self, /): return self.  issubset(other)
	def __ge__(self, other: Self, /): return self.issuperset(other)

	def __eq__(self, other: Self, /): return     self <= other \
											 and self >= other
	def __lt__(self, other: Self, /): return not self >= other
	def __gt__(self, other: Self, /): return not self <= other
	def __ne__(self, other: Self, /): return not self == other


	def copy(self):
		return self.__class__(
			self.moves,
			self.capts,
			self.specs,
		)

	def clear(self):
		self.moves.clear()
		self.capts.clear()
		self.specs.clear()


	def union(self, *others: Self) -> Self:
		return self.__class__(
			self.moves.union(*(other.moves for other in others)),
			self.capts.union(*(other.capts for other in others)),
			self.specs.union(*(other.specs for other in others)),
		)

	def intersection(self, *others: Self) -> Self:
		return self.__class__(
			self.moves.intersection(*(other.moves for other in others)),
			self.capts.intersection(*(other.capts for other in others)),
			self.specs.intersection(*(other.specs for other in others)),
		)

	def difference(self, *others: Self) -> Self:
		return self.__class__(
			self.moves.difference(*(other.moves for other in others)),
			self.capts.difference(*(other.capts for other in others)),
			self.specs.difference(*(other.specs for other in others)),
		)

	def symmetric_difference(self, other: Self, /) -> Self:
		return self.__class__(
			self.moves.symmetric_difference(other.moves),
			self.capts.symmetric_difference(other.capts),
			self.specs.symmetric_difference(other.specs),
		)


	def update(self, *others: Self):
		self.moves.update(*(other.moves for other in others))
		self.capts.update(*(other.capts for other in others))
		self.specs.update(*(other.specs for other in others))

	def intersection_update(self, *others: Self):
		self.moves.intersection_update(*(other.moves for other in others))
		self.capts.intersection_update(*(other.capts for other in others))
		self.specs.intersection_update(*(other.specs for other in others))

	def difference_update(self, *others: Self):
		self.moves.difference_update(*(other.moves for other in others))
		self.capts.difference_update(*(other.capts for other in others))
		self.specs.difference_update(*(other.specs for other in others))

	def symmetric_difference_update(self, other: Self, /):
		self.moves.symmetric_difference_update(other.moves)
		self.capts.symmetric_difference_update(other.capts)
		self.specs.symmetric_difference_update(other.specs)


	def isdisjoint(self, other: Self, /) -> bool:
		return \
			self.moves.isdisjoint(other.moves) and \
			self.capts.isdisjoint(other.capts) and \
			self.specs.isdisjoint(other.specs)

	def issubset(self, other: Self, /) -> bool:
		return \
			self.moves.issubset(other.moves) and \
			self.capts.issubset(other.capts) and \
			self.specs.issubset(other.specs)

	def issuperset(self, other: Self, /) -> bool:
		return \
			self.moves.issuperset(other.moves) and \
			self.capts.issuperset(other.capts) and \
			self.specs.issuperset(other.specs)

