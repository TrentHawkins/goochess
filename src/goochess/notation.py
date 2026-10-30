from __future__ import annotations


import collections
import itertools
import typing


class rank(str):

	expansion = str.maketrans({str(n + 1): "-" * (n + 1) for n in range(8)})


	def __new__(cls, notation: str, /):
		return super().__new__(cls, notation.translate(cls.expansion))

	def __str__(self) -> str:
		return "".join(str(len(tuple(group))) if char == "-" else "".join(group) for char, group in itertools.groupby(self))


class board(tuple[rank, ...]):

	def __new__(cls, iterable: str | typing.Iterable[rank], /) -> typing.Self:
		if isinstance(iterable, str):
			iterable = map(rank, iterable.split("/"))

		return super().__new__(cls, iterable)

	def __str__(self) -> str:
		return "/".join(map(str, self))


	@property
	def serial(self) -> str:
		return "".join(self)


class serial(str):

	def __new__(cls, value: str, /) -> typing.Self:
		flat = board(value).serial if "/" in value else value[:]

		return super().__new__(cls, flat)

	def __str__(self) -> str:
		return str(board(self.ranks))


	@property
	def ranks(self) -> typing.Iterable[rank]:
		return (rank(self[index:index + 8]) for index in range(0, len(self), 8))


class position(collections.namedtuple("position", "placement color castling en_passant halfmove fullmove")):

	__slots__ = ()

	placement: board
	color: bool
	castling: str
	en_passant: str
	halfmove: int
	fullmove: int


	def __new__(cls, notation: str, /) -> typing.Self:
		placement, color, castling, en_passant, halfmove, fullmove = notation.split()

		return super().__new__(cls,
			board(placement),
			color == "b",
			castling,
			en_passant,
			int(halfmove),
			int(fullmove),
		)

	def __getnewargs__(self) -> tuple[str]:
		return (str(self),)

	def __str__(self) -> str:
		color = "b" if self.color else "w"

		return f"{self.placement} {color} {self.castling} {self.en_passant} {self.halfmove} {self.fullmove}"
