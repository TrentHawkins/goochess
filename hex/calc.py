from __future__ import annotations


from abc import ABC
from math import pi, sin, tan
from typing import Self


class Tangent(float, ABC):

	def __mul__    (self, value: float) -> Self: return self.__class__(super().__mul__    (value))
	def __truediv__(self, value: float) -> Self: return self.__class__(super().__truediv__(value))

	def sin(self, sides: int) -> float: return sin(self.angle(sides))
	def tan(self, sides: int) -> float: return tan(self.angle(sides))

	def angle(self, sides: int) -> float: return pi / sides
	def outer(self, sides: int) -> float: return NotImplemented
	def inner(self, sides: int) -> float: return NotImplemented


class Side(Tangent):

	def outer(self, sides: int) -> Self: return self / self.sin(sides)
	def inner(self, sides: int) -> Self: return self / self.tan(sides)


class Circ(Tangent):

	def outer(self, sides: int) -> Self: return self * self.tan(sides)
	def inner(self, sides: int) -> Self: return self * self.sin(sides)


class RegularPolygon:

	def __init__(self, side: float):
		self.side = Side(side)

	def __init_subclass__(cls, *args,
		sides: int = 6,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.sides = sides
		cls.angle = pi / sides


	@property
	def outer(self) -> float:
		return self.side.outer(self.sides)

	@property
	def inner(self) -> float:
		return self.side.inner(self.sides)


	def area(self, side: float) -> float:
		return self.perimeter(side) * side / 2 / self.inner

	def perimeter(self, side: float) -> float:
		return self.sides * side
