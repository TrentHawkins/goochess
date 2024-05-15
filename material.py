from geometry import Colors, Squares, Moves


class Piece:

	turns: int

	moves: set[Moves] = set()
	capts: set[Moves] = moves


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.capts for base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: bool = False

	def __init__(self, color: Colors,
		board = None,
		square: Squares | None = None,
	) -> None:
		self.__pre_init__()

		self.color = color
		self.square = square
		self.board = board

		self.__post_init__()

	def __post_init__(self) -> None:
		...

	def __bool__(self) -> bool:
		return self.turn < self.turns


	def kill(self) -> None:
		self.__init__(self.color)



class Pawn(Piece):

	moves = {
		Moves.S,
	}
	capts = {
		Moves.SE,
		Moves.SW,
	}

	def __post_init__(self) -> None:
		super().__post_init__()

		self.moves = {move * self.color for move in self.moves}
		self.capts = {capt * self.color for capt in self.capts}


class Melee(Piece):

	...


class Ranged(Piece):

	...


class Rook(Ranged, Piece):

	moves = {
		Moves.N,
		Moves.E,
		Moves.S,
		Moves.W,
	}
	capts = moves

class Bishop(Ranged, Piece):

	moves = {
		Moves.NE,
		Moves.SE,
		Moves.SW,
		Moves.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		Moves.NNE,
		Moves.NEE,
		Moves.SEE,
		Moves.SSE,
		Moves.SSW,
		Moves.SWW,
		Moves.NWW,
		Moves.NNW,
	}
	capts = moves



class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	...
