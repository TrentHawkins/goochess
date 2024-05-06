from re import compile, Pattern
from typing import Self


class Index(int):

	lower: int =  0
	upper: int =  8


	def __new__(cls, index: int) -> Self:
		if cls.lower <= index < cls.upper:
			return super().__new__(cls, index)

		raise IndexError(f"{cls.__name__.lower()} out of chessboard bounds")


	def __add__(self, other) -> Self:
		return self.__class__(super().__add__(other))

	def __sub__(self, other) -> Self:
		return self.__class__(super().__sub__(other))


class Summable:

	def __radd__(self, other) -> Self:
		return self + other if other else self

	def __rsub__(self, other) -> Self:
		return self - other if other else self

	def __rmul__(self, other) -> Self:
		return self * other if other else self


class BiIndex(Index, Summable):

	lower: int = -7
	upper: int = +8


	def __mul__(self, other) -> Self:
		return self.__class__(super().__mul__(other))

	def __pos__(self) -> Self:
		return self.__class__(super().__pos__())

	def __neg__(self) -> Self:
		return self.__class__(super().__neg__())


class Vector(Summable,
	tuple[
		BiIndex,
		BiIndex,
	]
):

	def __new__(cls, *indices) -> Self:
		return super().__new__(cls, indices)


	def __add__(self, other) -> Self:
		return self.__class__(
			self[0] + other[0],
			self[1] + other[1],
		)

	def __sub__(self, other) -> Self:
		return self.__class__(
			self[0] - other[0],
			self[1] - other[1],
		)

	def __mul__(self, other) -> Self:
		return self.__class__(
			self[0] * other,
			self[1] * other,
		)

	def __pos__(self) -> Self:
		return self.__class__(
			+self[0],
			+self[1],
		)

	def __neg__(self) -> Self:
		return self.__class__(
			-self[0],
			-self[1],
		)


class Square(
	tuple[
		Index,
		Index,
	]
):

	files: str = "abcdefgh"
	ranks: str = "12345678"

	notation: Pattern = compile(f"[{files}][{ranks}]")


	def __new__(cls, *indices: Index) -> Self:
		return super().__new__(cls, indices)


	def __repr__(self):
		return self.file + self.rank

	def __add__(self, other: Vector) -> Self:
		return self.__class__(
			self[0] - other[0],
			self[1] + other[1],
		)

	def __sub__(self, other: Self) -> Vector:
		return Vector(
			BiIndex(other[0]) - self[0],
			BiIndex(self[1]) - other[1],
		)


	@classmethod
	def from_notation(cls, square: str) -> Self:
		if cls.notation.fullmatch(square):
			return cls(
				Index( 8 - int(square[1])),
				Index(ord(square[0]) - 97),
			)

		raise IndexError("invalid square")


	@property
	def file(self) -> str:
		return chr(int(self[1]) + 97)

	@property
	def rank(self) -> str:
		return str( 8 - int(self[0]))
