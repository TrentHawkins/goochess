from __future__ import annotations


import itertools


class rank(str):

	expansion = str.maketrans({str(n): "-" * n for n in range(1, 9)})


	def __new__(cls, notation: str, /):
		return super().__new__(cls, notation.translate(cls.expansion))

	def __str__(self) -> str:
		return "".join(str(len(tuple(group))) if char == "-" else "".join(group) for char, group in itertools.groupby(self))


class board(list[rank]):

	def __init__(self, notation: str, /):
		super().__init__(rank(line) for line in notation.split("/"))

	def __str__(self) -> str:
		return "/".join(str(rank) for rank in self)
