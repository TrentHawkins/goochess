from __future__ import annotations


from dataclasses import dataclass
from enum import Enum
from typing import Generator


@dataclass
class RGB:

	R: int
	G: int
	B: int


	def __repr__(self) -> str:
		return f"{self.R};{self.G};{self.B}"


	def foreground(self, obj) -> str:
		return f"\x1b[38;2;{self}m{obj}\x1b[0m"

	def background(self, obj) -> str:
		return f"\x1b[48;2;{self}m{obj}\x1b[0m"


	@classmethod
	def fromhex(cls, code: str) -> RGB:
		code = code.lstrip("#").lower()

		return cls(*(int(code[i:i+2], 16) for i in (0, 2, 4)))


	@property
	def hex(self) -> str:
		return f"#{self.R:02x}{self.G:02x}{self.B:02x}"


class Color(int, Enum):

	BLACK = +1  # ⬛
	WHITE = -1  # ⬜


	def __bool__(self) -> bool:
		return bool(self + 1)

	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜\n"


	def piece(self, obj,
		black: RGB = RGB.fromhex("#000000"),
		white: RGB = RGB.fromhex("#ffffff"),
	) -> str:
		return black.foreground(obj) if self else white.foreground(obj)

	def square(self, obj,
		black: RGB = RGB.fromhex("#996633"),
		white: RGB = RGB.fromhex("#cc9966"),
	) -> str:
		return black.background(obj) if self else white.background(obj)
		