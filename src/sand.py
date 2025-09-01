from __future__ import annotations


class A:

	def __init__(self, x, y):
		self.x = x
		self.y = y


from enum import Enum


class As(A, Enum):

	ONE = "f", 1
	TWO = "g", 1
