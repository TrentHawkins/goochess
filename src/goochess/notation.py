from __future__ import annotations


import collections
import itertools
import re
import typing


class rank(str):

	expansion = str.maketrans({str(n + 1): "-" * (n + 1) for n in range(8)})
	symbols = "PNBRQKpnbrqk-"


	def __new__(cls, notation: str, /) -> typing.Self:
		expanded = notation.translate(cls.expansion)

		if len(expanded) != 8 or any(symbol not in cls.symbols for symbol in expanded):
			raise ValueError(f"invalid rank {notation!r}")

		return super().__new__(cls, expanded)

	def __str__(self) -> str:
		return "".join(str(len(tuple(group))) if char == "-" else "".join(group) for char, group in itertools.groupby(self))


class board(tuple[rank, ...]):

	def __new__(cls, iterable: str | typing.Iterable[str], /) -> typing.Self:
		if isinstance(iterable, str):
			iterable = iterable.split("/")

		ranks = tuple(map(rank, iterable))

		if len(ranks) != 8:
			raise ValueError("a board must contain eight ranks")

		return super().__new__(cls, ranks)

	def __str__(self) -> str:
		return "/".join(map(str, self))


	@property
	def serial(self) -> str:
		return "".join(self)


class serial(str):

	def __new__(cls, value: str, /) -> typing.Self:
		flat = board(value).serial if "/" in value else value[:]

		if len(flat) != 64 or any(symbol not in rank.symbols for symbol in flat):
			raise ValueError("a serial board must contain 64 valid squares")

		return super().__new__(cls, flat)

	def __str__(self) -> str:
		return str(board(self.ranks))


	@property
	def ranks(self) -> typing.Iterable[rank]:
		return (rank(self[index: index + 8]) for index in range(0, len(self), 8))


class color(int):

	def __new__(cls, value: str | int, /) -> typing.Self:
		if value in ("w", "b"):
			value = value == "b"

		if not isinstance(value, int) or value not in (0, 1):
			raise ValueError(f"invalid color {value!r}")

		return super().__new__(cls, value)

	def __str__(self) -> str:
		return "b" if self else "w"


class castling(str):

	def __new__(cls, value: str, /) -> typing.Self:
		if not value or re.fullmatch(r"-|K?Q?k?q?", value) is None:
			raise ValueError(f"invalid castling rights {value!r}")

		return super().__new__(cls, value)


class en_passant(str):

	def __new__(cls, value: str, /) -> typing.Self:
		if re.fullmatch(r"-|[a-h][36]", value) is None:
			raise ValueError(f"invalid en passant target {value!r}")

		return super().__new__(cls, value)


class halfmove(int):

	def __new__(cls, value: str | int, /) -> typing.Self:
		if isinstance(value, str):
			if not value.isascii() or not value.isdecimal():
				raise ValueError(f"invalid halfmove clock {value!r}")

			value = int(value)

		if not isinstance(value, int) or value < 0:
			raise ValueError(f"invalid halfmove clock {value!r}")

		return super().__new__(cls, value)


class fullmove(int):

	def __new__(cls, value: str | int, /) -> typing.Self:
		if isinstance(value, str):

			if not value.isascii() or not value.isdecimal():
				raise ValueError(f"invalid fullmove number {value!r}")

			value = int(value)

		if not isinstance(value, int) or value < 1:
			raise ValueError(f"invalid fullmove number {value!r}")

		return super().__new__(cls, value)


class position(
	collections.namedtuple(
		"position",
		[
			"placement",
			"color",
			"castling",
			"en_passant",
			"halfmove",
			"fullmove",
		]
	)
):

	__slots__ = ()

	placement: board
	color: color
	castling: castling
	enpassant: en_passant
	halfmove: halfmove
	fullmove: fullmove


	def __new__(cls, notation: str, /) -> typing.Self:
		placement, active, rights, target, clock, number = notation.split()

		return super().__new__(cls,
			board(placement),
			color(active),
			castling(rights),
			en_passant(target),
			halfmove(clock),
			fullmove(number),
		)

	def __getnewargs__(self) -> tuple[str]:
		return str(self),

	def __str__(self) -> str:
		return " ".join(map(str, self))
