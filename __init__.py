from __future__ import annotations


from typing import Iterable, Hashable, Self


class collection[T: Hashable](set):

	def __init__(self, *items: T):
		super().__init__(items)

	def  __or__(self, other: Self, /) -> Self: return self.               union(other)
	def __and__(self, other: Self, /) -> Self: return self.        intersection(other)
	def __sub__(self, other: Self, /) -> Self: return self.          difference(other)
	def __xor__(self, other: Self, /) -> Self: return self.symmetric_difference(other)

	def  __ror__(self, other: Self, /) -> Self: return self | other
	def __rand__(self, other: Self, /) -> Self: return self & other
	def __rsub__(self, other: Self, /) -> Self: return self - other
	def __rxor__(self, other: Self, /) -> Self: return self ^ other

	def  __ior__(self, other: Self, /) -> Self: self.                     update(other); return self
	def __iand__(self, other: Self, /) -> Self: self.        intersection_update(other); return self
	def __isub__(self, other: Self, /) -> Self: self.          difference_update(other); return self
	def __ixor__(self, other: Self, /) -> Self: self.symmetric_difference_update(other); return self

	def                union(self, *others: Self) -> Self: return self.__class__(*super().               union(*others))
	def         intersection(self, *others: Self) -> Self: return self.__class__(*super().        intersection(*others))
	def           difference(self, *others: Self) -> Self: return self.__class__(*super().          difference(*others))
	def symmetric_difference(self,  other : Self) -> Self: return self.__class__(*super().symmetric_difference( other ))


	@classmethod
	def any(cls, others: Iterable[Self]) -> Self:
		return cls().union(*others)

	@classmethod
	def all(cls, others: Iterable[Self]) -> Self:
		return cls().intersection(*others)


	def copy(self) -> Self:
		return self.__class__(*self)

	def filter(self, by: type[T]) -> Self:
		return self.__class__(*(item for item in self if isinstance(item, by)))


class array[T: (int, float)](tuple[T, ...]):

	dimension: int

	def __init_subclass__(cls, *args,
		dimension: int,
	**kwargs):
		cls.dimension = dimension

		return super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *components) -> Self:
		return super().__new__(cls, components[:cls.dimension])

	def __bool__(self,) -> bool:
		return bool(sum(self))

	def __add__(self, other: Self) -> Self: return self.__class__(*(left + right for left, right in zip(self, other)))
	def __sub__(self, other: Self) -> Self: return self.__class__(*(left - right for left, right in zip(self, other)))

	def __mul__(self, times: T) -> Self:
		return self.__class__(*(left * times for left in self))

	def __floordiv__(self, times: T) -> Self:
		return self.__class__(*(left // times for left in self))

	def __pos__(self) -> Self: return self.__class__(*(+left for left in self))
	def __neg__(self) -> Self: return self.__class__(*(-left for left in self))
