from __future__ import annotations

from enum import Enum

from .mathematics import index


class Square(index[2, 8], Enum):

#	 1       :  2       :  3       :  4       :  5       :  6       :  7       :  8
	A1 = 0o00; A2 = 0o01; A3 = 0o02; A4 = 0o03; A5 = 0o04; A6 = 0o05; A7 = 0o06; A8 = 0o07  # A
	B1 = 0o10; B2 = 0o11; B3 = 0o12; B4 = 0o13; B5 = 0o14; B6 = 0o15; B7 = 0o16; B8 = 0o17  # B
	C1 = 0o20; C2 = 0o21; C3 = 0o22; C4 = 0o23; C5 = 0o24; C6 = 0o25; C7 = 0o26; C8 = 0o27  # C
	D1 = 0o30; D2 = 0o31; D3 = 0o32; D4 = 0o33; D5 = 0o34; D6 = 0o35; D7 = 0o36; D8 = 0o37  # D
	E1 = 0o40; E2 = 0o41; E3 = 0o42; E4 = 0o43; E5 = 0o44; E6 = 0o45; E7 = 0o46; E8 = 0o47  # E
	F1 = 0o50; F2 = 0o51; F3 = 0o52; F4 = 0o53; F5 = 0o54; F6 = 0o55; F7 = 0o56; F8 = 0o57  # F
	G1 = 0o60; G2 = 0o61; G3 = 0o62; G4 = 0o63; G5 = 0o64; G6 = 0o65; G7 = 0o66; G8 = 0o67  # G
	H1 = 0o70; H2 = 0o71; H3 = 0o72; H4 = 0o73; H5 = 0o74; H6 = 0o75; H7 = 0o76; H8 = 0o77  # H


	def __repr__(self) -> str:
		return self.name.lower()

	def __bool__(self) -> bool:
		return bool(sum(self.vector) & 1)


	@property
	def rank(self) -> int:
		return int(self.name[1])

	@property
	def file(self) -> str:
		return self.name[0].lower()
