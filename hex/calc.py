from __future__ import annotations

import math
import typing


class RegularPolygon:

	def __init__(self, sides: int):
		self.sides = sides


	@property
	def angle(self) -> float:
		return math.pi / self.sides

	@property
	def outer(self) -> float:
		return math.sin(self.angle)

	@property
	def inner(self) -> float:
		return math.tan(self.angle)


	def outer_circ(self, side: float) -> float: return side / self.outer
	def inner_circ(self, side: float) -> float: return side / self.inner
	def outer_side(self, circ: float) -> float: return circ * self.outer
	def inner_side(self, circ: float) -> float: return circ * self.inner

	def size(self, circ: float, sides: int) -> float:
		return self.inner_circ(self.__class__(sides).inner_side(circ))

	def area(self, side: float) -> float:
		return self.perimeter(side) * side / 2 / self.inner

	def perimeter(self, side: float) -> float:
		return self.sides * side
