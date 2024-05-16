from enum import Enum
from typing import Self


class Group(int):

	def __add__(self, other: int) -> Self:
		return self.__class__(super().__add__(other))

	def __sub__(self, other: int) -> Self:
		return self.__class__(super().__sub__(other))


class Ring(Group):

	def __mul__(self, other: int) -> Self:
		return self.__class__(super().__mul__(other))


class Move(Ring, Enum):

	N = -0o10  # king queen rook pawn (white)
	E = +0o01  # king queen rook
	S = +0o10  # king queen rook pawn (black)
	W = -0o01  # king queen rook

	N2 = N * 2  # pawn (leap)
	S2 = S * 2  # pawn (leap)
	E2 = E * 2  # king (castle)
	W2 = W * 2  # king (castle)
	W3 = W * 3  # rook (castling short (kingside))
	E4 = E * 4  # rook (castling long (queenside))

	NE = N + E  # queen bishop pawn (white capture)
	SE = S + E  # queen bishop pawn (black capture)
	NW = N + W  # queen bishop pawn (white capture)
	SW = S + W  # queen bishop pawn (black capture)

	N2E = N + NE  # knight
	NE2 = NE + E  # knight
	SE2 = SE + E  # knight
	S2E = S + SE  # knight
	S2W = S + SW  # knight
	SW2 = SW + W  # knight
	NW2 = NW + W  # knight
	N2W = N + NW  # knight


	def __repr__(self) -> str:
		return self.name


class Color(int, Enum):

	WHITE = -1  # ⬜
	BLACK = +1  # ⬛


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


class File(int, Enum):

	A = 0o0  # A
	B = 0o1  # B
	C = 0o2  # C
	D = 0o3  # D
	E = 0o4  # E
	F = 0o5  # F
	G = 0o6  # G
	H = 0o7  # H


	def __repr__(self) -> str:
		return self.name.lower()


class Rank(int, Enum):

	_8 = 0o0  # 8
	_7 = 0o1  # 7
	_6 = 0o2  # 6
	_5 = 0o3  # 5
	_4 = 0o4  # 4
	_3 = 0o5  # 3
	_2 = 0o6  # 2
	_1 = 0o7  # 1


	def __repr__(self) -> str:
		return str(0o10 - self.value)


class Square(Group, Enum):

#	A          B          C          D          E          F          G          H        :
	A8 = 0o00; B8 = 0o01; C8 = 0o02; D8 = 0o03; E8 = 0o04; F8 = 0o05; G8 = 0o06; H8 = 0o07;  # 8
	A7 = 0o10; B7 = 0o11; C7 = 0o12; D7 = 0o13; E7 = 0o14; F7 = 0o15; G7 = 0o16; H7 = 0o17;  # 7
	A6 = 0o20; B6 = 0o21; C6 = 0o22; D6 = 0o23; E6 = 0o24; F6 = 0o25; G6 = 0o26; H6 = 0o27;  # 6
	A5 = 0o30; B5 = 0o31; C5 = 0o32; D5 = 0o33; E5 = 0o34; F5 = 0o35; G5 = 0o36; H5 = 0o37;  # 5
	A4 = 0o40; B4 = 0o41; C4 = 0o42; D4 = 0o43; E4 = 0o44; F4 = 0o45; G4 = 0o46; H4 = 0o47;  # 4
	A3 = 0o50; B3 = 0o51; C3 = 0o52; D3 = 0o53; E3 = 0o54; F3 = 0o55; G3 = 0o56; H3 = 0o57;  # 3
	A2 = 0o60; B2 = 0o61; C2 = 0o62; D2 = 0o63; E2 = 0o64; F2 = 0o65; G2 = 0o66; H2 = 0o67;  # 2
	A1 = 0o70; B1 = 0o71; C1 = 0o72; D1 = 0o73; E1 = 0o74; F1 = 0o75; G1 = 0o76; H1 = 0o77;  # 1


	def __repr__(self) -> str:
		return self.name.lower()


	@property
	def rank(self) -> Rank:
		return Rank(self >> 3)

	@property
	def file(self) -> File:
		return File(self - (self.rank << 3))

	@property
	def color(self) -> Color:
		return Color(((self.rank + self.file & 1) << 1) - 1)
