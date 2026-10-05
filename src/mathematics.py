from __future__ import annotations


from typing import Self, SupportsIndex, overload


array = tuple[int, ...]


class Vector(array):

	def __getnewargs__(self) -> array:
		return tuple(self)

	def __new__(cls, *components: int) -> Self:
		return super().__new__(cls, components)

	def __repr__(self) -> str:
		cls = type(self)

		return cls.__name__ + super().__repr__()

	def __bool__(self) -> bool:
		return any(self)

	@overload
	def __getitem__(self, key: SupportsIndex, /) -> int:
		...

	@overload
	def __getitem__(self, key: slice, /) -> Self:
		...

	def __getitem__(self, key: SupportsIndex | slice, /) -> int | Self:
		cls = type(self)

		if isinstance(key, slice):
			return cls(*super().__getitem__(key))

		return super().__getitem__(key)

	def __add__(self, other: int | array) -> Self:
		cls = type(self)

		if isinstance(other, int):
			if other == 0:
				return self

			other = (other,) * len(self)

		return cls(*(left + right for left, right in zip(self, other)))

	def __sub__(self, other: int | array) -> Self:
		return -(other - self)

	def __mul__(self, other: int | array) -> Self:
		cls = type(self)

		if isinstance(other, int):
			if other == 1:
				return self

			other = (other,) * len(self)

		return cls(*(left * right for left, right in zip(self, other)))

	def __matmul__(self, other: int | array) -> int:
		if isinstance(other, int):
			other = (other,) * len(self)

		return sum(left * right for left, right in zip(self, other))

	def __radd__(self, other: int | array) -> Self: return  self + other
	def __rmul__(self, other: int | array) -> Self: return  self * other
	def __rsub__(self, other: int | array) -> Self: return -self + other

	def __rmatmul__(self, other: int | array) -> int:
		return self @ other

	def __pos__(self) -> Self:
		return self

	def __neg__(self) -> Self:
		cls = type(self)

		return cls(*(-left for left in self))

	def __abs__(self) -> int:
		return self @ self
