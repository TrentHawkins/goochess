from __future__ import annotations


import enum

from . import mathematics

class Compass(mathematics.arrays):

	north = mathematics.array( 0, -1)
	south = mathematics.array( 0,  1)
	east  = mathematics.array( 1,  0)
	west  = mathematics.array(-1,  0)

	ranks = mathematics.arrays(
		north,
		south,
	)
	files = mathematics.arrays(
		east,
		west,
	)


class Index(mathematics.index[2, 8], enum.Enum):

#	A        : B        : C        : D        : E        : F        : G        : H
	A8 = 0o00; B8 = 0o01; C8 = 0o02; D8 = 0o03; E8 = 0o04; F8 = 0o05; G8 = 0o06; H8 = 0o07  # 8
	A7 = 0o10; B7 = 0o11; C7 = 0o12; D7 = 0o13; E7 = 0o14; F7 = 0o15; G7 = 0o16; H7 = 0o17  # 7
	A6 = 0o20; B6 = 0o21; C6 = 0o22; D6 = 0o23; E6 = 0o24; F6 = 0o25; G6 = 0o26; H6 = 0o27  # 6
	A5 = 0o30; B5 = 0o31; C5 = 0o32; D5 = 0o33; E5 = 0o34; F5 = 0o35; G5 = 0o36; H5 = 0o37  # 5
	A4 = 0o40; B4 = 0o41; C4 = 0o42; D4 = 0o43; E4 = 0o44; F4 = 0o45; G4 = 0o46; H4 = 0o47  # 4
	A3 = 0o50; B3 = 0o51; C3 = 0o52; D3 = 0o53; E3 = 0o54; F3 = 0o55; G3 = 0o56; H3 = 0o57  # 3
	A2 = 0o60; B2 = 0o61; C2 = 0o62; D2 = 0o63; E2 = 0o64; F2 = 0o65; G2 = 0o66; H2 = 0o67  # 2
	A1 = 0o70; B1 = 0o71; C1 = 0o72; D1 = 0o73; E1 = 0o74; F1 = 0o75; G1 = 0o76; H1 = 0o77  # 1


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
