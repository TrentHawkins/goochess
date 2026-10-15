from __future__ import annotations


import typing

from .mathematics import array as Vector, arrays as Vectors, indices as Squares
from .geometry import Color, Index
from .algebra import Move, Capt

if typing.TYPE_CHECKING: from .engine import Board


class Piece:

	north = Vector( 1,  0)
	south = Vector(-1,  0)
	east  = Vector( 0,  1)
	west  = Vector( 0, -1)

	ranks = Vectors(
		north,
		south,
	)
	files = Vectors(
		east,
		west,
	)

	white: str
	black: str

	moves: Vectors
	capts: Vectors
	specs: Vectors
	stock: Vectors


	def __init__(self,
		board: Board,
		color: Color,
		index: Index | None = None,
	) -> None:
		self.board = board
		self.color = color
		self.index = index

	def __repr__(self) -> str:
		return self.white if self.color else self.black


	@property
	def targets(self) -> Squares:
		return Squares()


class Pawn(Piece):

	moves = Vectors(
		Piece.north,
		Piece.north * 2,
	)
	capts = Vectors(Piece.north) * Piece.files

	white: str = ""  # "♙"
	black: str = ""  # "♟"


	@property
	def targets(self) -> Squares:
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


class Melee(Piece):

	@property
	def targets(self) -> Squares:
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
	def targets(self) -> Squares:
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


class Assymetric(Piece):

	...


class Rook(Ranged, Officer):

	moves = Piece.ranks | Piece.files

	white: str = "R"  # "♖"
	black: str = "r"  # "♜"


class Bishop(Ranged, Assymetric, Officer):

	moves = Piece.ranks * Piece.files

	white: str = "B"  # "♗"
	black: str = "b"  # "♝"


class Knight(Melee, Assymetric, Officer):

	moves = Rook.moves * Bishop.moves - Rook.moves

	white: str = "N"  # "♘"
	black: str = "n"  # "♞"


class Star(Piece):

	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star, Officer):

	white: str = "Q"  # "♕"
	black: str = "q"  # "♛"


class King(Melee, Star):

	white: str = "K"  # "♔"
	black: str = "k"  # "♚"
