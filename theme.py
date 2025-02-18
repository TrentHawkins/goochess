from __future__ import annotations


from dataclasses import dataclass


@dataclass
class RGB:

	R: int
	G: int
	B: int


	def __repr__(self) -> str:
		return f"{self.R};{self.G};{self.B}"


	@classmethod
	def fromhex(cls, color: str) -> RGB:
		color = color.lstrip("#")

		return cls(*(int(color[i:i+2], 16) for i in (0, 2, 4)))


	@property
	def hex(self) -> str:
		return f"#{self.R:02x}{self.G:02x}{self.B:02x}"


	def fg(self, obj) -> str:
		return f"\x1b[38;2;{self}m{obj}\x1b[0m"

	def bg(self, obj) -> str:
		return f"\x1b[48;2;{self}m{obj}\x1b[0m"


@dataclass
class Palette:

	black: RGB
	white: RGB


	@classmethod
	def fromhex(cls,
		black: str,
		white: str,
	) -> Palette:
		return cls(
			black = RGB.fromhex(black),
			white = RGB.fromhex(white),
		)



@dataclass
class Theme:

	square: Palette
	pieces: Palette


	@staticmethod
	def inv(obj) -> str:
		return f"\x1b[7m{obj}\x1b[27m"


DEFAULT = Theme(
	square = Palette.fromhex(
		black = "#bbaa99",
		white = "#665544",
	),
	pieces = Palette.fromhex(
		black = "#000000",
		white = "#ffffff",
	),
)
