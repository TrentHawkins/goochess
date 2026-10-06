from __future__ import annotations


import math
import operator

from typing import Callable, Self, SupportsIndex, overload


def exp(x: float, /) -> float:
	try:
		return math.exp(x)

	except OverflowError:
		return math.inf


def log(x: float, /) -> float:
	try:
		return math.log(x)

	except ValueError:
		if x:
			return math.nan

		return -math.inf


def inv(x: float, /) -> float:
	try:
		return 1 / x

	except ZeroDivisionError:
		return math.copysign(math.inf, x)


type number = int | float
type array = tuple[int, ...]


class vector(tuple[int, ...]):

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

	def __add__(self, other: int | array, /) -> Self: return self.operator(other, operator = operator.add, identity = 0)
	def __sub__(self, other: int | array, /) -> Self: return self.operator(other, operator = operator.sub, identity = 0)
	def __mul__(self, other: int | array, /) -> Self: return self.operator(other, operator = operator.mul, identity = 1)

	def __matmul__(self, other: int | array, /) -> int:
		return sum(self * other)

	def __radd__(self, other: int | array, /) -> Self: return  self + other
	def __rmul__(self, other: int | array, /) -> Self: return  self * other
	def __rsub__(self, other: int | array, /) -> Self: return -self + other

	def __rmatmul__(self, other: int | array, /) -> int:
		return self @ other

	def __pos__(self) -> Self: return self
	def __neg__(self) -> Self: return self * -1

	def __abs__(self) -> int:
		return self @ self


	def operator(self, other: int | array, /, *,
		operator: Callable[[int, int], int],
		identity: int,
	) -> Self:
		cls = type(self)

		if isinstance(other, int):
			if other == identity:
				return self

			other = (other,) * len(self)

		return cls(*(operator(left, right) for left, right in zip(self, other, strict = True)))


class index(int):

	base: int


	def __init_subclass__(cls, *, base: int, **kwargs) -> None:
		super().__init_subclass__(**kwargs)

		cls.base = base


	@classmethod
	def from_vector(cls, vector: vector) -> Self:
		return cls(sum(component * cls.base ** power for power, component in enumerate(vector)))

	@property
	def vector(self) -> vector:
		components = []
		remaining = int(self)

		while remaining:
			remaining, component = divmod(remaining, self.base)
			components.append(component)

		return vector(*components)


class average(float):

	encode: Callable[[float], float] = staticmethod(float)
	decode: Callable[[float], float] = staticmethod(float)


	def __new__(cls, x: float, _: int | None = None, /) -> Self:
		return super().__new__(cls, x)

	def __init__(self, x: float, count: int | None = None, /) -> None:
		super().__init__()

		if count is None:
			count = x.count if isinstance(x, average) else 1

		if count < 0:
			raise ValueError

		self.count = count

	def __add__(self, other: float | average, /) -> Self: return self.operator(other, operator = operator.add)
	def __sub__(self, other: float | average, /) -> Self: return self.operator(other, operator = operator.sub)

	def __radd__(self, other: float | average, /) -> float | Self:
		if not isinstance(other, average) and other == 0:
			return self

		return super().__radd__(other)


	def operator(self, other: float | average, /, *,
		operator: Callable[[number, number], number],
	) -> Self:
		cls = type(self)

		other = cls(other)
		count = int(operator(self.count, other.count))

		left  = self. count * cls.encode(self ) if self .count else 0
		right = other.count * cls.encode(other) if other.count else 0

		return cls(cls.decode(operator(left, right) / count if count else 0), count)


class geometric(average):

	encode = staticmethod(log)
	decode = staticmethod(exp)


class harmonic(average):

	encode = staticmethod(inv)
	decode = staticmethod(inv)
