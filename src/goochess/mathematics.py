from __future__ import annotations


import collections.abc
import math
import numbers
import operator
import typing


type pair[T] = tuple[T, T]
type array[T] = tuple[T, ...]
type operation[T] = typing.Callable[[T, T], T]
type comparison[T] = typing.Callable[[T, T], bool]
type mutation[*T] = typing.Callable[[str, *T], None]


class vector(tuple[int, ...]):

	def __new__(cls, *components: int) -> typing.Self:
		return super().__new__(cls, components)

	def __getnewargs__(self) -> array[int]:
		return tuple(self)

	def __bool__(self) -> bool:
		return any(self)

	@typing.overload
	def __getitem__(self, key: typing.SupportsIndex, /) -> int:
		...

	@typing.overload
	def __getitem__(self, key: slice, /) -> typing.Self:
		...

	def __getitem__(self, key: typing.SupportsIndex | slice, /) -> int | typing.Self:
		cls = type(self)

		match key:
			case typing.SupportsIndex(): return      super().__getitem__(key)
			case                slice(): return cls(*super().__getitem__(key))
			case _                     :
				return NotImplemented


	def __add__(self, other: int | array[int], /) -> typing.Self: return self.operate(other, operator = operator.add, identity = 0)
	def __sub__(self, other: int | array[int], /) -> typing.Self: return self.operate(other, operator = operator.sub, identity = 0)
	def __mul__(self, other: int | array[int], /) -> typing.Self: return self.operate(other, operator = operator.mul, identity = 1)

	def __matmul__(self, other: int | array[int], /) -> int:
		return sum(self * other)

	def __radd__(self, other: int | array[int], /) -> typing.Self: return  self + other
	def __rsub__(self, other: int | array[int], /) -> typing.Self: return -self + other
	def __rmul__(self, other: int | array[int], /) -> typing.Self: return  self * other

	def __rmatmul__(self, other: int | array[int], /) -> int:
		return self @ other

	def __pos__(self) -> typing.Self: return self
	def __neg__(self) -> typing.Self: return self * -1

	def __abs__(self) -> int:
		return self @ self


	def operate(self, other: int | array[int], /, *,
		operator: operation[int],
		identity: int,
	) -> typing.Self:
		cls = type(self)

		if isinstance(other, int):
			if isinstance(other, index):
				return NotImplemented

			if other == identity:
				return self

			other = (other,) * len(self)

		return cls(*(operator(left, right) for left, right in zip(self, other, strict = True)))


class index(int):

	registry: dict[tuple[type[index], pair[int]], type[index]] = {}

	dim : int
	base: int

	@typing.overload
	def __new__(cls, x: int) -> typing.Self:
		...

	@typing.overload
	def __new__(cls, x: array[int]) -> typing.Self:
		...

	def __new__(cls, x: int | array[int]) -> typing.Self:
		if isinstance(x, int):
			if not 0 <= x < cls.base ** cls.dim:
				raise ValueError

			return super().__new__(cls, x)

		return cls.from_vector(x)

	def __class_getitem__(cls, item: pair[int], /) -> type[index]:
		dim, base = item

		if (key := (cls, item)) in cls.registry:
			return cls.registry[key]

		class concrete(cls, dim = dim, base = base): ...

		qualifier = f"{dim}_{base}"

		concrete.__name__ = f"{cls.__name__}_{qualifier}"
		concrete.__qualname__ = f"{cls.__qualname__}_{qualifier}"
		concrete.__module__ = cls.__module__

		return cls.registry.setdefault(key, concrete)

	def __reduce__(self) -> str | tuple:
		cls: type[index] = type(self)
		items: list[pair[int]] = []

		while specialization := next((key for key, value in cls.registry.items() if value is cls), None):
			cls, item = specialization
			items.append(item)

		if not items:
			return super().__reduce__()

		return cls.restore, (tuple(reversed(items)), int(self)), super().__getstate__()

	def __init_subclass__(cls, *args,
		dim : int | None = None,
		base: int | None = None,
	**kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)

		if dim  is not None: cls.dim  = dim
		if base is not None: cls.base = base

	@typing.overload
	def __getitem__(self, key: typing.SupportsIndex, /) -> int:
		...

	@typing.overload
	def __getitem__(self, key: slice, /) -> index:
		...

	def __getitem__(self, key: typing.SupportsIndex | slice, /) -> int | index:
		components = self.vector[key]

		match components:
			case vector(): cls = index[len(components), self.base]; return cls(components)
			case    int():                                          return     components
			case _       :
				return NotImplemented

	def __add__(self, other: array[int], /) -> typing.Self:
		cls = type(self)

		return cls.from_vector(self.vector + other)

	def __radd__(self, other: array[int], /) -> typing.Self:
		return self + other

	def __sub__(self, other: int | array[int], /) -> vector | typing.Self:
		cls = type(self)

		if isinstance(other, int):
			return self.vector - cls(other).vector

		return cls.from_vector(self.vector - other)


	@classmethod
	def restore(cls, items: array[pair[int]], value: int, /) -> typing.Self:
		for item in items:
			cls = cls[item]

		return cls(value)

	@classmethod
	def from_vector(cls, components: array[int], /) -> typing.Self:

		if len(components) != cls.dim or any(not 0 <= component < cls.base for component in components):
			raise ValueError

		return cls(sum(component * cls.base ** power for power, component in enumerate(components)))


	@property
	def vector(self) -> vector:
		components = []
		remaining = int(self)

		for _ in range(self.dim):
			remaining, component = divmod(remaining, self.base)
			components.append(component)

		return vector(*components)


class fraction(numbers.Number):

	__slots__ = (
		"numerator",
		"denominator",
	)

	def __setattr__(self, name: str, value: object, /) -> None: self.mutate(name, value, mutator = super().__setattr__)
	def __delattr__(self, name: str,                /) -> None: self.mutate(name,        mutator = super().__delattr__)

	def __init__(self, numerator: int | fraction = 0, denominator: int = 1, /) -> None:
		if isinstance(numerator, fraction):
			self.numerator   = numerator.numerator
			self.denominator = numerator.denominator

			return

		common = math.gcd(numerator, denominator)

		if denominator < 0:
			common = -common

		self.numerator   = numerator   // common if common else numerator
		self.denominator = denominator // common if common else denominator

	def __getstate__(self) -> object:
		return super().__getstate__()

	def __repr__(self) -> str:
		return f"{self.numerator:+}/{self.denominator}"

	def __hash__(self) -> int:
		if self.denominator == 0:
			if self.numerator == 0:
				return hash(math.nan)

			return hash(math.copysign(math.inf, self.numerator))

		if self.denominator == 1:
			return hash(self.numerator)

		return hash((self.numerator, self.denominator))

	def __bool__(self) -> bool:
		return self.numerator != 0 or self.denominator == 0

	def __add__(self, other: int | fraction, /) -> typing.Self: return self.operate(other, operator = operator.add)
	def __sub__(self, other: int | fraction, /) -> typing.Self: return self.operate(other, operator = operator.sub)
	def __mul__(self, other: int | fraction, /) -> typing.Self:
		cls = type(self)
		other = cls(other)

		return cls(self.numerator * other.numerator, self.denominator * other.denominator)

	def __truediv__(self, other: int | fraction, /) -> typing.Self:
		cls = type(self)

		return self * ~cls(other)

	def __radd__(self, other: int | fraction, /) -> typing.Self: return  self + other
	def __rsub__(self, other: int | fraction, /) -> typing.Self: return -self + other
	def __rmul__(self, other: int | fraction, /) -> typing.Self: return  self * other

	def __rtruediv__(self, other: int | fraction, /) -> typing.Self:
		return ~self * other

	def __pow__(self, value: int, /) -> typing.Self:
		numerator, denominator = self.numerator, self.denominator

		if value < 0:
			numerator, denominator = denominator, numerator
			value = -value

		cls = type(self)

		return cls(numerator ** value, denominator ** value)

	def __pos__(self, /) -> typing.Self: cls = type(self); return cls(    self                             )
	def __neg__(self, /) -> typing.Self: cls = type(self); return cls(   -self.numerator , self.denominator)
	def __abs__(self, /) -> typing.Self: cls = type(self); return cls(abs(self.numerator), self.denominator)

	def __invert__(self, /) -> typing.Self:
		cls = type(self)

		return cls(self.denominator, self.numerator)

	def __eq__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.eq)
	def __ne__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.ne)
	def __lt__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.lt)
	def __le__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.le)
	def __gt__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.gt)
	def __ge__(self, other: object, /) -> bool: return self.compare(other, comparator = operator.ge)

	@property
	def as_integer_ratio(self, /) -> pair[int]:
		return self.numerator, self.denominator


	def operate(self, other: int | fraction, /, *,
		operator: operation[int],
	) -> typing.Self:
		cls = type(self)
		other = cls(other)

		if self.denominator == other.denominator == 0 and self.numerator and other.numerator:
			return cls(operator(self.numerator, other.numerator), 0)

		return cls(
			operator(
				self.numerator * other.denominator,
				self.denominator * other.numerator,
			),
			self.denominator * other.denominator,
		)

	def compare(self, other: object, /, *,
		comparator: comparison[int],
	) -> bool:
		if not isinstance(other, int | fraction):
			return NotImplemented

		cls = type(self)
		other = cls(other)

		if self.as_integer_ratio == (0, 0) or other.as_integer_ratio == (0, 0):
			return comparator is operator.ne

		if self.denominator == other.denominator == 0:
			return comparator(self.numerator, other.numerator)

		return comparator(
			self.numerator * other.denominator,
			self.denominator * other.numerator,
		)

	def mutate[*T](self, name: str, *args: *T,
		mutator: mutation[*T],
	) -> None:
		if name in fraction.__slots__ and hasattr(self, name):
			raise AttributeError(f"'{fraction.__name__}' object attribute '{name}' is read-only")

		mutator(name, *args)


class collection[T: typing.Hashable](set[T]):

	def __init__(self, *items: T) -> None:
		super().__init__(items)

	def __reduce__(self) -> tuple:
		cls = type(self)

		return cls, tuple(self), self.__getstate__()

	def  __or__(self, other: typing.Iterable[T], /) -> typing.Self: return self.               union(other)
	def __and__(self, other: typing.Iterable[T], /) -> typing.Self: return self.        intersection(other)
	def __sub__(self, other: typing.Iterable[T], /) -> typing.Self: return self.          difference(other)
	def __xor__(self, other: typing.Iterable[T], /) -> typing.Self: return self.symmetric_difference(other)

	def  __ror__(self, other: typing.Iterable[T], /) -> typing.Self: return self | other
	def __rand__(self, other: typing.Iterable[T], /) -> typing.Self: return self & other
	def __rxor__(self, other: typing.Iterable[T], /) -> typing.Self: return self ^ other

	def        union(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().       union(*others))
	def intersection(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().intersection(*others))
	def   difference(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().  difference(*others))

	def copy(self) -> typing.Self:
		cls = type(self)

		return cls(*self)

	def symmetric_difference(self, other : typing.Iterable[T]) -> typing.Self:
		cls = type(self)

		return cls(*super().symmetric_difference(other))


class vectors(collection[vector]):

	def __add__(self, other: typing.Iterable[int | array[int]], /) -> typing.Self:
		cls = type(self)

		return cls(*(left + right for left in self for right in other))

	def __mul__(self, other: int, /) -> typing.Self:
		cls = type(self)

		return cls(*(left * other for left in self))

	def __radd__(self, other: typing.Iterable[int | array[int]], /) -> typing.Self: return self + other
	def __rmul__(self, other:                 int              , /) -> typing.Self: return self * other
