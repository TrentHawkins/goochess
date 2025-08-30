from __future__ import annotations


from typing import Iterable, Hashable, Self, overload


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


class array(tuple[int, ...]):

	dimension: int

	def __init_subclass__(cls, *args,
		dimension: int | None = None,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		if dimension is not None:
			cls.dimension = dimension
			cls.zero = cls(*(0 for _ in range(cls.dimension)))

	def __new__(cls, *components: int) -> Self:
		assert cls.dimension == len(components)
		return super().__new__(cls, components)

	def __len__(self) -> int:
		return self.dimension

	def __pos__(self) -> Self: return self
	def __neg__(self) -> Self: return self.zero - self

	def __add__(self, other: array, /) -> Self: return self.__class__(*(left + right for left, right in zip(self, other)))
	def __sub__(self, other: array, /) -> Self: return self.__class__(*(left - right for left, right in zip(self, other)))
	def __mul__(self, times: int  , /) -> Self: return self.__class__(*(left * times for left        in     self        ))

	def __radd__(self, other: array, /) -> Self: return  self + other
	def __rsub__(self, other: array, /) -> Self: return -self + other
	def __rmul__(self, times: int  , /) -> Self: return  self * times

	def __matmul__(self, other: array, /) -> int:
		return sum((right * left for left, right in zip(self, other)))

	def __rmatmul__(self, other: array, /) -> int:
		return self @ other

	def __abs__(self) -> int:
		return self @ self


class zerosumarray(array):

	def __new__(cls, *components: int) -> Self:
		projection = sum(components)
		normalizer = cls.dimension if projection else 1

		return super().__new__(cls, *(normalizer * component - projection for component in components))

	def __len__(self) -> int:
		return super().__len__() - 1


class arrays(collection[array]):

	@overload
	def __mul__(self, other: set[array], /) -> Self:
		...

	@overload
	def __mul__(self, other: set[array], /) -> Self:
		...

	def __mul__(self, other: set[array] | int, /) -> Self:
		match other:
			case set(): return self.__class__(*(left + right for left in self for right in other))
			case int(): return self.__class__(*(left * other for left in self))
			case     _: return NotImplemented
