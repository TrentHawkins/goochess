from re import compile, Pattern


class Index(int):

	lower_bound: int =  0
	upper_bound: int =  8


	def __new__(cls, coordinate: int):
		if cls.lower_bound <= coordinate < cls.upper_bound:
			return super().__new__(cls, coordinate)

		raise IndexError("coordinate out of chessboard bounds")


	def __add__(self, other):
		return self.__class__(super().__add__(other))

	def __sub__(self, other):
		return self.__class__(super().__sub__(other))


class Summable:

	def __radd__(self, other):
		return self + other if other else self

	def __rsub__(self, other):
		return self - other if other else self

	def __rmul__(self, other):
		return self * other if other else self


class BiIndex(Index, Summable):

	lower_bound: int = -7
	upper_bound: int = +8


	def __mul__(self, other):
		return self.__class__(super().__mul__(other))

	def __pos__(self):
		return self.__class__(super().__pos__())

	def __neg__(self):
		return self.__class__(super().__neg__())


class Vector(Summable,
	tuple[
		BiIndex,
		BiIndex,
	]
):

	def __new__(cls, *coordinates):
		return super().__new__(cls, coordinates)


	def __add__(self, other):
		return self.__class__(
			self[0] + other[0],
			self[1] + other[1],
		)

	def __sub__(self, other):
		return self.__class__(
			self[0] - other[0],
			self[1] - other[1],
		)

	def __mul__(self, other):
		return self.__class__(
			self[0] * other,
			self[1] * other,
		)

	def __pos__(self):
		return self.__class__(
			+self[0],
			+self[1],
		)

	def __neg__(self):
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

	def __new__(cls, square: str | tuple):
		if isinstance(square, str):
			if cls.notation.fullmatch(square):
				return super().__new__(cls,
					(
						Index( 8 - int(square[1])),
						Index(ord(square[0]) - 97),
					)
				)

		if isinstance(square, tuple):
			return super().__new__(cls, square)

		raise IndexError("invalid square")


	def __add__(self, other: Vector):
		return self.__class__(
			(
				self[0] - other[0],
				self[1] + other[1],
			)
		)

	def __sub__(self, other: Vector):
		return self.__class__(
			(
				self[0] + other[0],
				self[1] - other[1],
			)
		)


	@property
	def file(self) -> str:
		return chr(int(self[1]) + 97)

	@property
	def rank(self) -> int:
		return int( 8 - int(self[0]))
