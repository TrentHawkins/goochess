from __future__ import annotations


import abc
import enum
import contextlib
import typing

from . import mathematics
from . import structs
from . import geometry
from . import algebra
if typing.TYPE_CHECKING: from . import engine


class Piece:

	index: geometry.Index | None = None
	position: engine.Position

	value: int =  0
	white: str = "-"
	black: str = "-"

	moves: mathematics.arrays
	specs: mathematics.arrays


	def __init__(self, color: bool, /) -> None:
		self.color = color
		self.moved = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __call__(self, target: int | geometry.Index, /, *,
		kept: Piece | None = None,
		moved: bool = True,
	) -> typing.Self:
		assert (source := self.index) is not None

		target = geometry.Index(target)

		self.position[source] = kept
		self.position[target] = self

		self.moved = moved

		return self

	def __hash__(self) -> int:
		return id(self)

	def __eq__(self, other) -> bool:
		return self is other


	@staticmethod
	def fromnotation(notation: str, /) -> Piece:
		cls = Roster[notation.upper()].value

		return cls(notation.islower())


	@property
	def side(self) -> engine.Side:
		return self.position.side[self.color]

	@property
	def targets(self) -> algebra.Moves:
		return algebra.Moves()

	@property
	def squares(self) -> algebra.Moves:
		squares = self.targets

		for step in tuple(squares):
			with step.simulated:
				if self.side.king is not None and not self.side.king.safe:
					squares.discard(step)

		return squares


class Omni(Piece, abc.ABC):

	@property
	def targets(self) -> algebra.Moves:
		targets = super().targets

		if self.index is None:
			return targets

		for move in self.moves:
			with contextlib.suppress(ValueError):
				targets.update(self.search(self.index, move))

		return targets


	@abc.abstractmethod
	def search(self, square: geometry.Index,
		move: mathematics.array,
	) -> typing.Generator[algebra.Move]:
		...


class Melee(Omni):

	def search(self, square: geometry.Index,
		move: mathematics.array,
	) -> typing.Generator[algebra.Move]:
		if step := algebra.Move(square := square + move, self): yield step
		if step := algebra.Capt(square                 , self): yield step


class Ranged(Omni):

	def search(self, square: geometry.Index,
		move: mathematics.array,
	) -> typing.Generator[algebra.Move]:
		while step := algebra.Move(square := square + move, self): yield step
		if    step := algebra.Capt(square                 , self): yield step


class Rook(Ranged, Omni):

	value =  5
	white = "R"  # "♖"
	black = "r"  # "♜"

	moves = geometry.Compass.ranks | geometry.Compass.files


class Bishop(Ranged, Omni):

	value =  3
	white = "B"  # "♗"
	black = "b"  # "♝"

	moves = geometry.Compass.ranks * geometry.Compass.files


class Knight(Melee, Omni):

	value =  3
	white = "N"  # "♘"
	black = "n"  # "♞"

	moves = Rook.moves * Bishop.moves - Rook.moves


class Star(Omni):

	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star):

	value =  9
	white = "Q"  # "♕"
	black = "q"  # "♛"


class Officer(enum.Enum):

	Q = Queen
	R = Rook
	N = Knight
	B = Bishop


class King(Melee, Star):

	white = "K"  # "♔"
	black = "k"  # "♚"


	@property
	def safe(self) -> bool:
		return self.index is not None and self.index not in self.side.other.targets


class Pawn(Piece):

	value =  1
	white = "P"  # "♙"
	black = "p"  # "♟"


	@property
	def targets(self) -> algebra.Moves:
		targets = super().targets

		if self.index is None:
			return targets

		Δ = geometry.Compass.south if self.color else geometry.Compass.north

		try: square = self.index + Δ
		except ValueError: return targets

		with contextlib.suppress(ValueError):
			if step := algebra.Move(square    , self): targets.add(step)
			if step := algebra.Rush(square + Δ, self): targets.add(step)

		for move in geometry.Compass.files:
			with contextlib.suppress(ValueError):
				target = square + move
				cls = algebra.EnPassant if isinstance(self.position[target], Ghost) else algebra.Capt

				if step := cls(target, self): targets.add(step)

		return targets


class Roster(enum.Enum):

	P = Pawn
	Q = Queen
	R = Rook
	N = Knight
	B = Bishop
	K = King


class Ghost(Piece):

	def __init__(self, rusher: Pawn, /) -> None:
		assert isinstance(rusher, Pawn)

		super().__init__(rusher.color)

		self.rusher = rusher
