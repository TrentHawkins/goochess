from __future__ import annotations


import abc
import contextlib
import typing

from .mathematics import array, arrays, indices
from .geometry import Color, Index, Compass
from .algebra import Move, Capt, Rush

if typing.TYPE_CHECKING: from .engine import Side, Game


class Piece:

	value: int
	white: str
	black: str

	moves: arrays
	specs: arrays


	def __init__(self, side: Side,
		square: Index | None = None,
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
	def targets(self) -> indices:
		return indices()

	@property
	def squares(self) -> indices:
		return self.targets

	@property
	def color(self) -> Color:
		return self.side.color

	@property
	def game(self) -> Game:
		return self.side.game


class Omni(Piece, abc.ABC):

	@property
	def targets(self) -> indices:
		targets = super().targets

		if self.square is None:
			return targets

		for move in self.moves:
			with contextlib.suppress(ValueError):
				targets.update(self.search(self.square, move))

		return targets


	@abc.abstractmethod
	def search(self, square: Index,
		move: array,
	) -> typing.Generator[Move]:
		...


class Melee(Omni):

	def search(self, square: Index,
		move: array,
	) -> typing.Generator[Move]:
		if step := Move(square := square + move, self): yield step
		if step := Capt(square                 , self): yield step


class Ranged(Omni):

	def search(self, square: Index,
		move: array,
	) -> typing.Generator[Move]:
		while step := Move(square := square + move, self): yield step
		if    step := Capt(square                 , self): yield step


class Officer(Omni):

	...


class Rook(Ranged, Officer):

	value =  5
	white = "R"  # "♖"
	black = "r"  # "♜"

	moves = Compass.ranks | Compass.files


class Bishop(Ranged, Officer):

	value =  3
	white = "B"  # "♗"
	black = "b"  # "♝"

	moves = Compass.ranks * Compass.files


class Knight(Melee, Officer):

	value =  3
	white = "N"  # "♘"
	black = "n"  # "♞"

	moves = Rook.moves * Bishop.moves - Rook.moves


class Star(Omni):

	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star, Officer):

	value =  9
	white = "Q"  # "♕"
	black = "q"  # "♛"


class King(Melee, Star):

	value =  0
	white = "K"  # "♔"
	black = "k"  # "♚"


class Pawn(Piece):

	value =  1
	white = "P"  # "♙"
	black = "p"  # "♟"


	@property
	def forward(self) -> array:
		return Compass.north if self.color else Compass.south

	@property
	def targets(self) -> indices:
		targets = super().targets

		if self.square is None:
			return targets

		Δ = self.forward; ᐊ, ᐅ = tuple(Compass.files)

		try: square = self.square + Δ
		except ValueError: return targets

		with contextlib.suppress(ValueError):
			if step := Move(square    , self): targets.add(step)
			if step := Rush(square + Δ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := Capt(square + ᐊ, self): targets.add(step)

		with contextlib.suppress(ValueError):
			if step := Capt(square + ᐅ, self): targets.add(step)

		return targets
