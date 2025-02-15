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
		code = code.lstrip("#")

		return cls(*(int(code[i:i+2], 16) for i in (0, 2, 4)))


	@property
	def hex(self) -> str:
		return f"#{self.R:02x}{self.G:02x}{self.B:02x}"


class Theme:

	class Square:

		BLACK = RGB.fromhex("#996633")
		WHITE = RGB.fromhex("#cc9966")

	class Piece:

		BLACK = RGB.fromhex("#000000")
		WHITE = RGB.fromhex("#ffffff")


class Color(int, Enum):

	BLACK = +1  # ⬛
	WHITE = -1  # ⬜


	def __bool__(self) -> bool:
		return bool(self + 1)

	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


	def piece(self, obj,
		black: RGB = Theme.Piece.BLACK,
		white: RGB = Theme.Piece.WHITE,
	) -> str:
		return black.foreground(obj) if self else white.foreground(obj)

	def square(self, obj,
		black: RGB = Theme.Square.BLACK,
		white: RGB = Theme.Square.WHITE,
	) -> str:
		return black.background(obj) if self else white.background(obj)
