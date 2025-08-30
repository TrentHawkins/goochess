from __future__ import annotations


from enum import Enum, Flag, auto
from typing import Generator, Self, overload

import hex


class Color(int, Flag):

	BLUE  = auto()
	GREEN = auto()
	RED   = auto()


class vector(hex.array,
	dimension = 3,
	traceless = True,
):

	...


class Vector(vector, Enum,
	dimension = 3,
	traceless = True,
):

	OO = ( 0,  0,  0)
	BP = ( 0,  0, +3)
	BM = ( 0,  0, -3)
	GP = ( 0, +3,  0)
	GM = ( 0, -3,  0)
	RP = (+3,  0,  0)
	RM = (-3,  0,  0)


	@classmethod
	def generate(cls, size: int) -> Generator[vector]:
		if not size:
			yield cls.OO

			return

		for grid in cls.generate(size - 1):
			for unit in Vector:
				yield unit.value + grid

	@classmethod
	def print(cls, size: int) -> None:
		for vector in sorted(set(cls.generate(size))):
			print("".join(f"{component:>+3}" for component in vector))


class Vectors(hex.collection[vector]):

	@overload
	def __mul__(self, other: Vectors, /) -> Self:
		...

	@overload
	def __mul__(self, other: int, /) -> Self:
		...

	def __mul__(self, other: Vectors | int, /) -> Self:
		match other:
			case Vectors(): return self.__class__(*(left + right for left in self for right in other))
			case     int(): return self.__class__(*(left * other for left in self))
			case         _: return NotImplemented
