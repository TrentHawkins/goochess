from __future__ import annotations

import enum

from . import mathematics

class Compass(mathematics.arrays):

	north = mathematics.array( 1, 0)
	south = mathematics.array(-1, 0)
	east  = mathematics.array(0,  1)
	west  = mathematics.array(0, -1)

	ranks = mathematics.arrays(
		north,
		south,
	)
	files = mathematics.arrays(
		east,
		west,
	)


class Color(int, enum.Enum):

	WHITE =  1
	BLACK = -1


	def __bool__(self) -> bool:
		return self == Color.WHITE


class Square(mathematics.index[2, 8], enum.Enum):

#	 1       :  2       :  3       :  4       :  5       :  6       :  7       :  8
	A1 = 0o00; A2 = 0o10; A3 = 0o20; A4 = 0o30; A5 = 0o40; A6 = 0o50; A7 = 0o60; A8 = 0o70  # A
	B1 = 0o01; B2 = 0o11; B3 = 0o21; B4 = 0o31; B5 = 0o41; B6 = 0o51; B7 = 0o61; B8 = 0o71  # B
	C1 = 0o02; C2 = 0o12; C3 = 0o22; C4 = 0o32; C5 = 0o42; C6 = 0o52; C7 = 0o62; C8 = 0o72  # C
	D1 = 0o03; D2 = 0o13; D3 = 0o23; D4 = 0o33; D5 = 0o43; D6 = 0o53; D7 = 0o63; D8 = 0o73  # D
	E1 = 0o04; E2 = 0o14; E3 = 0o24; E4 = 0o34; E5 = 0o44; E6 = 0o54; E7 = 0o64; E8 = 0o74  # E
	F1 = 0o05; F2 = 0o15; F3 = 0o25; F4 = 0o35; F5 = 0o45; F6 = 0o55; F7 = 0o65; F8 = 0o75  # F
	G1 = 0o06; G2 = 0o16; G3 = 0o26; G4 = 0o36; G5 = 0o46; G6 = 0o56; G7 = 0o66; G8 = 0o76  # G
	H1 = 0o07; H2 = 0o17; H3 = 0o27; H4 = 0o37; H5 = 0o47; H6 = 0o57; H7 = 0o67; H8 = 0o77  # H


	def __repr__(self) -> str:
		return self.name.lower()

	def __str__(self) -> str:
		return repr(self)

	def __bool__(self) -> bool:
		return bool(sum(self.array) & 1)

	@property
	def rank(self) -> int:
		return int(self.name[1])

	@property
	def file(self) -> str:
		return self.name[0].lower()

	@property
	def color(self) -> Color:
		return Color.WHITE if self else Color.BLACK
