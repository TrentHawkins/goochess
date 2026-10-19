from __future__ import annotations


import abc
import enum
import contextlib
import typing

from . import mathematics
from . import geometry
from . import algebra

if typing.TYPE_CHECKING: from .engine import Side, Game


class Piece:

	value: int =  0
	white: str = "-"
	black: str = "-"

	moves: mathematics.arrays
	specs: mathematics.arrays


	def __init__(self, side: Side,
		square: geometry.Square | None = None,
	) -> None:
		self.side = side
		self.square = square

		self.moved = False  # to be set to `True` by the move executor

	def __repr__(self) -> str:
		return (self.white if self.color else self.black).strip()

	def __hash__(self) -> int:
		return id(self)

	def __eq__(self, other) -> bool:
		return self is other


	@property
	def targets(self) -> mathematics.indices:
		return mathematics.indices()

	@property
	def squares(self) -> mathematics.indices:
		return self.targets

	@property
	def color(self) -> geometry.Color:
		return self.side.color

	@property
	def game(self) -> Game:
		return self.side.game


class Omni(Piece, abc.ABC):

	@property
	def targets(self) -> mathematics.indices:
		targets = super().targets

		if self.square is None:
			return targets

		for move in self.moves:
			with contextlib.suppress(ValueError):
				targets.update(self.search(self.square, move))

		return targets


	@abc.abstractmethod
	def search(self, square: geometry.Square,
		move: mathematics.array,
	) -> typing.Generator[algebra.Move]:
		...


class Melee(Omni):

	def search(self, square: geometry.Square,
		move: mathematics.array,
	) -> typing.Generator[algebra.Move]:
		if step := algebra.Move(square := square + move, self): yield step
		if step := algebra.Capt(square                 , self): yield step


class Ranged(Omni):

	def search(self, square: geometry.Square,
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
	def forward(self) -> mathematics.array:
		return geometry.Compass.north if self.color else geometry.Compass.south

	@property
	def targets(self) -> mathematics.indices:
		targets = super().targets

		if self.square is None:
			return targets

		Δ = self.forward; ᐊ, ᐅ = tuple(geometry.Compass.files)

		try: square = self.square + Δ
		except ValueError: return targets

		with contextlib.suppress(ValueError):
			if step := algebra.Move(square    , self): targets.add(step)
			if step := algebra.Rush(square + Δ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := algebra.Capt(square + ᐊ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := algebra.Capt(square + ᐅ, self): targets.add(step)

		return targets


class Ghost(Piece):

	white = "P"  # "♙"
	black = "p"  # "♟"
