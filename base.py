from __future__ import annotations

from enum import Enum


class Color(int, Enum):

	WHITE = -1  # ⬜
	BLACK = +1  # ⬛


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


class Set[T](set[T]):

	def __init__(self, *,
		squares: set[T] | None = None,
		targets: set[T] | None = None,
		special: set[T] | None = None,
	) -> None:
		self.special = special or set[T]()
		self.squares = squares or self.special
		self.targets = targets or self.squares

		super().__init__(self.squares | self.targets | self.special)


	def union(self, *args: Set[T]) -> Set[T]:
		return Set(
			squares = self.squares.union(*(arg.squares for arg in args)),
			targets = self.targets.union(*(arg.targets for arg in args)),
			special = self.special.union(*(arg.special for arg in args)),
		)

	def intersection(self, *args: Set[T]) -> Set[T]:
		return Set(
			squares = self.squares.intersection(*(arg.squares for arg in args)),
			targets = self.targets.intersection(*(arg.targets for arg in args)),
			special = self.special.intersection(*(arg.special for arg in args)),
		)

	def difference(self, *args: Set[T]) -> Set[T]:
		return Set(
			squares = self.squares.difference(*(arg.squares for arg in args)),
			targets = self.targets.difference(*(arg.targets for arg in args)),
			special = self.special.difference(*(arg.special for arg in args)),
		)
