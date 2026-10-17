from __future__ import annotations


import enum
import typing

from .mathematics import arrays, indices

from .geometry import Color, Index, Compass
from .algebra import Move, Capt

if typing.TYPE_CHECKING: from .engine import Board


class Piece:

	value: int
	white: str
	black: str

	moves: arrays
	specs: arrays


	def __init__(self,
		board: Board,
		color: Color,
		index: Index,
	) -> None:
		self.board = board
		self.color = color
		self.index = index

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


class Melee(Piece):

	@property
	def targets(self) -> indices:
		targets = super().targets

		if self.index is None:
			return targets

		for move in self.moves:
			target = self.index

			try:
				if step := Move(target := target + move, self): targets.add(step)
				if step := Capt(target                 , self): targets.add(step)

			except ValueError:
				continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> indices:
		targets = super().targets

		if self.index is None:
			return targets

		for move in self.moves:
			target = self.index

			try:
				while step := Move(target := target + move, self): targets.add(step)
				if    step := Capt(target                 , self): targets.add(step)

			except ValueError:
				continue

		return targets


class Officer(Piece):

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


class Star(Piece):

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
	white = " "  # "♙"
	black = " "  # "♟"

	moves = Compass.north
	capts = Compass.north * Compass.files
	specs = Compass.north


	@property
	def targets(self) -> indices:
		targets = super().targets

		if self.index is None:
			return targets

		for move in self.moves * self.color:
			target = self.index

			try:
				if step := Move(target := target + move, self): targets.add(step)

			except ValueError:
				continue

		for capt in self.capts * self.color:
			target = self.index

			try:
				if step := Capt(target := target + capt, self): targets.add(step)

			except ValueError:
				continue

		return targets
