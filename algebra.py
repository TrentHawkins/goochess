from __future__ import annotations


import enum
import pathlib
import re

import pygame

import chess.theme


class Color(int, enum.Enum):

	BLACK = +1  # ⬛
	WHITE = -1  # ⬜


	def __bool__(self) -> bool:
		return bool(self + 1)

	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"


class File(int, enum.Enum):

	A_ = 0o00  # A
	B_ = 0o01  # B
	C_ = 0o02  # C
	D_ = 0o03  # D
	E_ = 0o04  # E
	F_ = 0o05  # F
	G_ = 0o06  # G
	H_ = 0o07  # H


	def __repr__(self) -> str:
		return self.name.strip("_").lower()


class Rank(int, enum.Enum):

	_8 = 0o00  # 8
	_7 = 0o10  # 7
	_6 = 0o20  # 6
	_5 = 0o30  # 5
	_4 = 0o40  # 4
	_3 = 0o50  # 3
	_2 = 0o60  # 2
	_1 = 0o70  # 1


	def __repr__(self) -> str:
		return self.name.strip("_").lower()


	def final(self, color: Color) -> bool:
		return self == self._1 if color else self == self._8


class Difference(int, enum.Enum):

	O =  0o00  # null

	N = -0o10  # king queen rook pawn(white)
	E = +0o01  # king queen rook
	S = +0o10  # king queen rook pawn(black)
	W = -0o01  # king queen rook

	N2 = N * 2  # pawn(white leap)
	S2 = S * 2  # pawn(black leap)
	E2 = E * 2  # king(castle)
	W2 = W * 2  # king(castle)
	E4 = E * 4  # rook(castle)
	W3 = W * 3  # rook(castle)

	NE = N + E  # queen bishop pawn(white capture)
	SE = S + E  # queen bishop pawn(black capture)
	SW = S + W  # queen bishop pawn(black capture)
	NW = N + W  # queen bishop pawn(white capture)

	N2E = N + NE  # knight
	NE2 = NE + E  # knight
	SE2 = SE + E  # knight
	S2E = S + SE  # knight
	S2W = S + SW  # knight
	SW2 = SW + W  # knight
	NW2 = NW + W  # knight
	N2W = N + NW  # knight


	def __repr__(self) -> str:
		symbols = {
			self.N.name: "▲",  # king queen rook pawn(white)
			self.E.name: "▶",  # king queen rook
			self.S.name: "▼",  # king queen rook pawn(black)
			self.W.name: "◀",  # king queen rook
		}

		parts = re.compile(r"([NSWE])(\d*)").findall(self.name)  # Extract movement letters and optional numbers

		representation = ""

		for direction, count in parts:
			representation += symbols[direction] * (int(count) if count else 1)

		return representation

	def __add__(self, other: int) -> Difference: return Difference(super().__add__(other))
	def __sub__(self, other: int) -> Difference: return Difference(super().__sub__(other))
	def __mul__(self, other: int) -> Difference: return Difference(super().__mul__(other))

	def __floordiv__(self, other: int) -> Difference: return Difference(super().__floordiv__(other))

	def __pos__(self) -> Difference: return Difference(+super())
	def __neg__(self) -> Difference: return Difference(-super())


class Square(int, enum.Enum):

#	A        : B        : C        : D        : E        : F        : G        : H        :
	A8 = 0o00; B8 = 0o01; C8 = 0o02; D8 = 0o03; E8 = 0o04; F8 = 0o05; G8 = 0o06; H8 = 0o07;  # 8
	A7 = 0o10; B7 = 0o11; C7 = 0o12; D7 = 0o13; E7 = 0o14; F7 = 0o15; G7 = 0o16; H7 = 0o17;  # 7
	A6 = 0o20; B6 = 0o21; C6 = 0o22; D6 = 0o23; E6 = 0o24; F6 = 0o25; G6 = 0o26; H6 = 0o27;  # 6
	A5 = 0o30; B5 = 0o31; C5 = 0o32; D5 = 0o33; E5 = 0o34; F5 = 0o35; G5 = 0o36; H5 = 0o37;  # 5
	A4 = 0o40; B4 = 0o41; C4 = 0o42; D4 = 0o43; E4 = 0o44; F4 = 0o45; G4 = 0o46; H4 = 0o47;  # 4
	A3 = 0o50; B3 = 0o51; C3 = 0o52; D3 = 0o53; E3 = 0o54; F3 = 0o55; G3 = 0o56; H3 = 0o57;  # 3
	A2 = 0o60; B2 = 0o61; C2 = 0o62; D2 = 0o63; E2 = 0o64; F2 = 0o65; G2 = 0o66; H2 = 0o67;  # 2
	A1 = 0o70; B1 = 0o71; C1 = 0o72; D1 = 0o73; E1 = 0o74; F1 = 0o75; G1 = 0o76; H1 = 0o77;  # 1


	def __init__(self, *args):
		super().__init__(*args)

		self.black = (
			153,
			136,
			119,
		)
		self.white = (
			255,
			238,
			221,
		)

		self.rect = pygame.Rect(
			pygame.Vector2(
				chess.theme.SQUARE_W * (self.file),
				chess.theme.SQUARE_H * (self.rank >> 0b11) + chess.theme.BOARD_OFFSET * 2 // 3,
			),
			pygame.Vector2(*chess.theme.SQUARE),
		)

	def __repr__(self) -> str:
		return self.name.lower()

	def __add__(self, other: int   ) -> Square: return Square(super().__add__(other))
	def __sub__(self, other: Square) -> int   : return        super().__sub__(other)
	def __mul__(self, color: Color ) -> Square:
		return +self if color else ~self

	def __pos__(self) -> Square: return Square(       self)
	def __neg__(self) -> Square: return Square(0o77 - self)

	def __invert__(self) -> Square:
		return Square(self ^ 0o70)

	def __iadd__(self, other: int   ) -> Square: return self + other
	def __isub__(self, other: Square) -> int   : return self - other
	def __imul__(self, color: Color ) -> Square: return self * color


	@classmethod
	def fromnotation(cls, notation: str) -> Square:
		file, rank = notation

		return cls((0o10 - int(rank) << 0b11) + ord(file) - ord("a"))

	@classmethod
	def range(cls, *args):
		for square in range(*args):
			yield cls(square)


	@property
	def rank(self) -> Rank:
		return Rank(self >> 0b11 << 0b11)

	@property
	def file(self) -> File:
		return File(self - self.rank)

	@property
	def color(self) -> Color:
		return Color((((self.rank >> 0b11) + self.file & 1) << 1) - 1)

	@property
	def decal(self) -> pathlib.Path:
		return pathlib.Path("chess/graphics/board/bevel.png")


	def draw(self, screen: pygame.Surface):
		self.surf = pygame.transform.smoothscale(pygame.image.load(self.decal).convert_alpha(), chess.theme.SQUARE)

		pygame.draw.rect(screen, self.black if self.color else self.white, self.rect)
		screen.blit(
			self.surf,
			self.rect, special_flags = pygame.BLEND_RGBA_MULT,
		)
