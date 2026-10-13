from __future__ import annotations


import itertools
import math
import numbers
import operator
import typing


type pair[T] = tuple[T, T]
type sequence[T] = tuple[T, ...]
type operation[T] = typing.Callable[[T, T], T]
type comparison[T] = typing.Callable[[T, T], bool]
type mutation[*T] = typing.Callable[[str, *T], None]


class array(tuple[int, ...]):

	def __new__(cls, components: int | sequence[int] = (), /, *rest: int) -> typing.Self:
		if isinstance(components, int):
			components = (components, *rest)

		return super().__new__(cls, components)

	def __bool__(self) -> bool:
		return any(self)

	def __add__(self, other: int | sequence[int], /) -> typing.Self: return self.operate(other, operator.add, 0)
	def __sub__(self, other: int | sequence[int], /) -> typing.Self: return self.operate(other, operator.sub, 0)
	def __mul__(self, other: int | sequence[int], /) -> typing.Self: return self.operate(other, operator.mul, 1)

	def __matmul__(self, other: int | sequence[int], /) -> int:
		return sum(self * other)

	def __radd__(self, other: int | sequence[int], /) -> typing.Self: return  self + other
	def __rsub__(self, other: int | sequence[int], /) -> typing.Self: return -self + other
	def __rmul__(self, other: int | sequence[int], /) -> typing.Self: return  self * other

	def __rmatmul__(self, other: int | sequence[int], /) -> int:
		return self @ other

	def __iadd__(self, other: int | sequence[int], /) -> typing.Self: return self + other
	def __isub__(self, other: int | sequence[int], /) -> typing.Self: return self - other
	def __imul__(self, other: int | sequence[int], /) -> typing.Self: return self * other

	def __imatmul__(self, other: int | sequence[int], /) -> int:
		return self @ other

	def __pos__(self) -> typing.Self: cls = type(self); return cls(*self)
	def __neg__(self) -> typing.Self: cls = type(self); return cls(*(-left for left in self))

	def __abs__(self) -> int:
		return self @ self


	def operate(self, other: int | sequence[int], /,
		operator: operation[int],
		identity: int,
	) -> typing.Self:
		cls = type(self)

		if other == ():
			other = 0

		if isinstance(other, int):
			if isinstance(other, index):
				return NotImplemented

			if other == identity:
				return self

			other = (other,) * len(self)

		if not len(self):
			self = (0,) * len(other)

		return cls(*(operator(left, right) for left, right in zip(self, other, strict = True)))


class index(int):

	registry: dict[tuple[type[index], pair[int]], type[index]] = {}

	dimension: int
	base: int

	lower: int = 0
	upper: int


	def __new__(cls, x: int | sequence[int]) -> typing.Self:
		if isinstance(x, int):
			if not cls.lower <= x < cls.upper:
				raise ValueError(f"{cls.__name__} {x} out of bound [{cls.lower}, {cls.upper})")

			return super().__new__(cls, x)

		return cls.from_sequence(x)

	def __class_getitem__(cls, item: pair[int], /) -> type[index]:
		dimension, base = item

		if (key := (cls, item)) in cls.registry:
			return cls.registry[key]

		class _(cls, dimension = dimension, base = base): ...

		qualifier = f"{dimension}_{base}"
		_.__name__ = f"{cls.__name__}_{qualifier}"
		_.__qualname__ = f"{cls.__qualname__}_{qualifier}"
		_.__module__ = cls.__module__

		return cls.registry.setdefault(key, _)

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
		dimension : int | None = None,
		base: int | None = None,
	**kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)

		if dimension is not None: cls.dimension = dimension
		if base is not None: cls.base = base

		cls.upper = cls.base ** cls.dimension

	@typing.overload
	def __getitem__(self, key: typing.SupportsIndex, /) -> int:
		...

	@typing.overload
	def __getitem__(self, key: slice, /) -> index:
		...

	def __getitem__(self, key: typing.SupportsIndex | slice, /) -> int | index:
		components = self.array[key]

		if isinstance(components, tuple):
			cls = index[len(components), self.base]

			return cls(components)

		return components

	def __add__(self, other: sequence[int], /) -> typing.Self:
		cls = type(self)

		return cls.from_sequence(self.array + other)

	def __radd__(self, other: sequence[int], /) -> typing.Self: return self + other
	def __iadd__(self, other: sequence[int], /) -> typing.Self: return self + other

	@typing.overload
	def __sub__(self, other: int, /) -> array:
		...

	@typing.overload
	def __sub__(self, other: sequence[int], /) -> typing.Self:
		...

	def __sub__(self, other: int | sequence[int], /) -> array | typing.Self:
		cls = type(self)

		if isinstance(other, int):
			return self.array - cls(other).array

		return cls.from_sequence(self.array - other)

	@typing.overload
	def __isub__(self, other: int, /) -> array:
		...

	@typing.overload
	def __isub__(self, other: sequence[int], /) -> typing.Self:
		...

	def __isub__(self, other: int | sequence[int], /) -> array | typing.Self: return self.__sub__(other)

	@classmethod
	def restore(cls, items: sequence[pair[int]], value: int, /) -> typing.Self:
		for item in items:
			cls = cls[item]

		return cls(value)

	@classmethod
	def from_sequence(cls, components: sequence[int], /) -> typing.Self:

		if len(components) != cls.dimension:
			raise ValueError(f"components {components} do not match dimension {cls.dimension}")

		if any(not 0 <= component < cls.base for component in components):
			raise ValueError(f"components {components} out of bound for {cls.__name__} with base {cls.base}")

		return cls(sum(component * cls.base ** power for power, component in enumerate(components)))


	@property
	def array(self) -> array:
		components = []
		remaining = int(self)

		for _ in range(self.dimension):
			remaining, component = divmod(remaining, self.base)
			components.append(component)

		return array(*components)


	def range(self, step: array, stop: bool = False, /) -> typing.Generator[typing.Self]:
		if len(step) != self.dimension or not step:
			raise ValueError(f"step {step} does not match dimension {self.dimension}")

		while not stop:
			try: self += step
			except ValueError: break
			yield self


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

	def __add__(self, other: int | fraction, /) -> typing.Self: return self.operate(other, operator.add)
	def __sub__(self, other: int | fraction, /) -> typing.Self: return self.operate(other, operator.sub)
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

	def __iadd__(self, other: int | fraction, /) -> typing.Self: return self + other
	def __isub__(self, other: int | fraction, /) -> typing.Self: return self - other
	def __imul__(self, other: int | fraction, /) -> typing.Self: return self * other

	def __itruediv__(self, other: int | fraction, /) -> typing.Self:
		return self / other

	def __pow__(self, value: int, /) -> typing.Self:
		numerator, denominator = self.numerator, self.denominator

		if value < 0:
			numerator, denominator = denominator, numerator
			value = -value

		cls = type(self)

		return cls(numerator ** value, denominator ** value)

	def __ipow__(self, value: int, /) -> typing.Self: return self ** value

	def __pos__(self, /) -> typing.Self: cls = type(self); return cls(    self                             )
	def __neg__(self, /) -> typing.Self: cls = type(self); return cls(   -self.numerator , self.denominator)
	def __abs__(self, /) -> typing.Self: cls = type(self); return cls(abs(self.numerator), self.denominator)

	def __invert__(self, /) -> typing.Self:
		cls = type(self)

		return cls(self.denominator, self.numerator)

	def __eq__(self, other: object, /) -> bool: return self.compare(other, operator.eq)
	def __ne__(self, other: object, /) -> bool: return self.compare(other, operator.ne)
	def __lt__(self, other: object, /) -> bool: return self.compare(other, operator.lt)
	def __le__(self, other: object, /) -> bool: return self.compare(other, operator.le)
	def __gt__(self, other: object, /) -> bool: return self.compare(other, operator.gt)
	def __ge__(self, other: object, /) -> bool: return self.compare(other, operator.ge)

	@property
	def as_integer_ratio(self, /) -> pair[int]:
		return self.numerator, self.denominator


	def operate(self, other: int | fraction, /,
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

	def compare(self, other: object, /,
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

	def __or__ (self, other: typing.Iterable[T], /) -> typing.Self: return self.               union(other)
	def __and__(self, other: typing.Iterable[T], /) -> typing.Self: return self.        intersection(other)
	def __sub__(self, other: typing.Iterable[T], /) -> typing.Self: return self.          difference(other)
	def __xor__(self, other: typing.Iterable[T], /) -> typing.Self: return self.symmetric_difference(other)

	def __ror__ (self, other: typing.Iterable[T], /) -> typing.Self: return self | other
	def __rand__(self, other: typing.Iterable[T], /) -> typing.Self: return self & other
	def __rxor__(self, other: typing.Iterable[T], /) -> typing.Self: return self ^ other

	def __ior__ (self, other: typing.Iterable[T], /) -> typing.Self: self.                     update(other); return self
	def __iand__(self, other: typing.Iterable[T], /) -> typing.Self: self.        intersection_update(other); return self
	def __isub__(self, other: typing.Iterable[T], /) -> typing.Self: self.          difference_update(other); return self
	def __ixor__(self, other: typing.Iterable[T], /) -> typing.Self: self.symmetric_difference_update(other); return self


	def        union(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().       union(*others))
	def intersection(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().intersection(*others))
	def   difference(self, *others: typing.Iterable[T]) -> typing.Self: cls = type(self); return cls(*super().  difference(*others))

	def symmetric_difference(self, other : typing.Iterable[T]) -> typing.Self:
		cls = type(self)

		return cls(*super().symmetric_difference(other))

	def copy(self) -> typing.Self:
		cls = type(self)

		return cls(*self)


class arrays(collection[array]):

	def __mul__(self, other: int | typing.Iterable[int] | typing.Iterable[sequence[int]], /) -> typing.Self:
		cls = type(self)

		if isinstance(other, int):
			if other <  0: raise NotImplementedError
			if other == 0: return cls()
			if other == 1: return cls(*self)

			return cls(*(left * other for left in self))

		return cls(*(left + right for left, right in itertools.product(self, other)))

	def __rmul__(self, other: int | typing.Iterable[int] | typing.Iterable[sequence[int]], /) -> typing.Self: return self * other
	def __imul__(self, other: int | typing.Iterable[int] | typing.Iterable[sequence[int]], /) -> typing.Self: return self * other

	def __pow__(self, other: int, /) -> typing.Self:
		cls = type(self)

		if other <= 0: raise NotImplementedError
		if other == 1: return cls(*self)
		if other == 2: return self * self

		return cls(*(sum(terms, array()) for terms in itertools.product(self, repeat = other)))

	def __ipow__(self, other: int, /) -> typing.Self: return self ** other


class indices(collection[index]):

	def __mul__(self, other: typing.Iterable[sequence[int]], /) -> typing.Self:
		cls = type(self)

		return cls(*(left + right for left, right in itertools.product(self, other)))

	def __rmul__(self, other: typing.Iterable[sequence[int]], /) -> typing.Self: return self * other
	def __imul__(self, other: typing.Iterable[sequence[int]], /) -> typing.Self: return self * other
