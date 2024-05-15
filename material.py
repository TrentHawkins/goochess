import geometry


class Piece:

	turns: int

	moves: set[geometry.Moves] = set()
	capts: set[geometry.Moves] = moves


	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.capts for base in cls.__bases__))

	def __pre_init__(self) -> None:
		self.turn: int = 0
		self.moved: bool = False

	def __init__(self, color: geometry.Colors,
		board = None,
		square: geometry.Squares | None = None,
	) -> None:
		self.__pre_init__()

		self.color = color
		self.board = board
		self.square = square

		self.__post_init__()

	def __post_init__(self) -> None:
		...

	def __bool__(self) -> bool:
		return self.turn < self.turns


	def kill(self) -> None:
		self.__init__(self.color)



class Pawn(Piece):

	moves = {
		geometry.Moves.S,
	}
	capts = {
		geometry.Moves.SE,
		geometry.Moves.SW,
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
		geometry.Moves.N,
		geometry.Moves.E,
		geometry.Moves.S,
		geometry.Moves.W,
	}
	capts = moves

class Bishop(Ranged, Piece):

	moves = {
		geometry.Moves.NE,
		geometry.Moves.SE,
		geometry.Moves.SW,
		geometry.Moves.NW,
	}
	capts = moves


class Knight(Melee, Piece):

	moves = {
		geometry.Moves.NNE,
		geometry.Moves.NEE,
		geometry.Moves.SEE,
		geometry.Moves.SSE,
		geometry.Moves.SSW,
		geometry.Moves.SWW,
		geometry.Moves.NWW,
		geometry.Moves.NNW,
	}
	capts = moves



class Queen(Rook, Bishop):

	...


class King(Melee, Queen):

	...
