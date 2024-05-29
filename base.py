from __future__ import annotations

from enum import Enum
from typing import Iterable, Self


class Color(int, Enum):

	WHITE = -1  # ⬜
	BLACK = +1  # ⬛


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


class Set[T]:

	def __init__(self, *,
		squares: set[T] | None = None,
		targets: set[T] | None = None,
		special: set[T] | None = None,
	) -> None:
		self.special = special or set()
		self.squares = squares or self.special
		self.targets = targets or self.squares

	def __repr__(self) -> str:
		return repr(self.squares | self.targets)


	def union(self, *args: Self) -> Self:
		return self.__class__(
			squares = self.squares.union(arg.squares for arg in args),
			targets = self.targets.union(arg.targets for arg in args),
			special = self.special.union(arg.special for arg in args),
		)

	def intersection(self, *args: Self) -> Self:
		return self.__class__(
			squares = self.squares.intersection(arg.squares for arg in args),
			targets = self.targets.intersection(arg.targets for arg in args),
			special = self.special.intersection(arg.special for arg in args),
		)

	def difference(self, *args: Self) -> Self:
		return self.__class__(
			squares = self.squares.intersection(arg.squares for arg in args),
			targets = self.targets.intersection(arg.targets for arg in args),
			special = self.special.intersection(arg.special for arg in args),
		)
