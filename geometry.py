from enum import Enum


class Color(int, Enum):

	WHITE = -1
	BLACK = +1


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


class Square(int):

	def __init__(self, square: int):
		self.piece = "Hello!"


	def __repr__(self):
		return self.file + self.rank

	def __add__(self, other: int):
		return self.__class__(super().__add__(other))

	def __sub__(self, other: int):
		return self.__class__(super().__sub__(other))


	@property
	def _row(self) -> int:
		return self >> 3

	@property
	def _column(self) -> int:
		return self - (self._row << 3)

	@property
	def _diagonal(self) -> int:
		return self._row + self._column

	@property
	def rank(self) -> str:
		return str(8 - self._row)

	@property
	def file(self) -> str:
		return chr(int(self._column) + 97)

	@property
	def color(self) -> Color:
		return Color(((self._diagonal & 1) << 1) - 1)


class Board(Square, Enum):

	A8 = 0o00; B8 = 0o01; C8 = 0o02; D8 = 0o03; E8 = 0o04; F8 = 0o05; G8 = 0o06; H8 = 0o07
	A7 = 0o10; B7 = 0o11; C7 = 0o12; D7 = 0o13; E7 = 0o14; F7 = 0o15; G7 = 0o16; H7 = 0o17
	A6 = 0o20; B6 = 0o21; C6 = 0o22; D6 = 0o23; E6 = 0o24; F6 = 0o25; G6 = 0o26; H6 = 0o27
	A5 = 0o30; B5 = 0o31; C5 = 0o32; D5 = 0o33; E5 = 0o34; F5 = 0o35; G5 = 0o36; H5 = 0o37
	A4 = 0o40; B4 = 0o41; C4 = 0o42; D4 = 0o43; E4 = 0o44; F4 = 0o45; G4 = 0o46; H4 = 0o47
	A3 = 0o50; B3 = 0o51; C3 = 0o52; D3 = 0o53; E3 = 0o54; F3 = 0o55; G3 = 0o56; H3 = 0o57
	A2 = 0o60; B2 = 0o61; C2 = 0o62; D2 = 0o63; E2 = 0o64; F2 = 0o65; G2 = 0o66; H2 = 0o67
	A1 = 0o70; B1 = 0o71; C1 = 0o72; D1 = 0o73; E1 = 0o74; F1 = 0o75; G1 = 0o76; H1 = 0o77
