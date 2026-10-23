from __future__ import annotations


import abc
import enum
import contextlib
import typing

from . import mathematics
from . import geometry
from . import algebra
if typing.TYPE_CHECKING: from . import engine


class Piece:

	index: geometry.Index | None = None
	game: engine.Game

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
		return self.game.side[self.color]

	@property
	def targets(self) -> mathematics.indices:
		return mathematics.indices()

	@property
	def squares(self) -> mathematics.indices:
		return self.targets


class Omni(Piece, abc.ABC):

	@property
	def targets(self) -> mathematics.indices:
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


class Pawn(Piece):

	value =  1
	white = "P"  # "♙"
	black = "p"  # "♟"


	@property
	def targets(self) -> mathematics.indices:
		targets = super().targets

		if self.index is None:
			return targets

		Δ = geometry.Compass.south if self.color else geometry.Compass.north; ᐊ, ᐅ = tuple(geometry.Compass.files)

		try: square = self.index + Δ
		except ValueError: return targets

		with contextlib.suppress(ValueError):
			if step := algebra.Move(square    , self): targets.add(step)
			if step := algebra.Rush(square + Δ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := algebra.Capt(square + ᐊ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := algebra.Capt(square + ᐅ, self): targets.add(step)

		return targets


class Roster(enum.Enum):

	P = Pawn
	Q = Queen
	R = Rook
	N = Knight
	B = Bishop
	K = King


class Ghost(Piece):

	...
