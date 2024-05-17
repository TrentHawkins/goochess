from enum import Enum


class Color(int, Enum):

	WHITE = -1  # ⬜
	BLACK = +1  # ⬛


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"
