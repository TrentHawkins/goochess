from __future__ import annotations


import typing


type pair[T] = tuple[T, T]
type seq[T] = tuple[T, ...]


class switch[T](tuple[T, T]):

	def __new__(cls,
		false: T,
		true : T, /
	) -> typing.Self:
		return super().__new__(cls,
			(
				false,
				true ,
			)
		)

	def __getnewargs__(self) -> pair[T]:
		return self

	def __getitem__(self, index: int) -> T:
		return super().__getitem__(index & 1)


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
