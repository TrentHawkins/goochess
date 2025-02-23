from __future__ import annotations


import itertools
import typing

import chess.theme
import chess.algebra
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece:

	range: int = 0
	value: int = 0

	black: str = " "
	white: str = " "

	moves: set[chess.algebra.Difference] = set()
	capts: set[chess.algebra.Difference] = set()


	def __init_subclass__(cls, *args, **kwargs):
		super().__init_subclass__(*args, **kwargs)

		cls.moves = cls.moves.union(*(base.moves for base in cls.__bases__))
		cls.capts = cls.capts.union(*(base.moves for base in cls.__bases__)) if not cls.capts else cls.moves

	#	cls.value += sum(base.value for base in cls.__bases__)


	def __init__(self,
		game: chess.engine.Game,
		side: chess.engine.Side, square: chess.algebra.Square | None = None,
	):
		self.game = game
		self.side = side

		self.square = square
		self.color = self.side.color

		self.turn: int = 0
		self.moved: bool = False

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __str__(self) -> str:
		color = chess.theme.DEFAULT.pieces.black if self.color else chess.theme.DEFAULT.pieces.white

		return color.bg(self.black)


	@property
	def squares(self) -> set[chess.algebra.Square]:
		return set()


class Officer(Piece):

	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.moves | self.capts:
				square = self.square

				for _ in range(self.range):
					try:
						square += move

						if not chess.rules.Move(self, square):
							break

						squares.add(square)

						if not chess.rules.Capt(self, square):
							break

					except ValueError:
						break

		return squares


class Melee(Officer):

	range: int = 1


class Ranged(Officer):

	range: int = 7


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	moves = {
		chess.algebra.Difference.S,
	}
	capts = {
		chess.algebra.Difference.SE,
		chess.algebra.Difference.SW,
	}


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			for move in self.moves:
				try:
					if chess.rules.Move(self, square := self.square + move * self.color):
						squares.add(square)

					if not self.moved:
						if chess.rules.Move(self, square := square + move * self.color):
							squares.add(square)

				except ValueError:
					continue

			for move in self.capts:
				try:
					if chess.rules.Capt(self, square := self.square + move * self.color):
						squares.add(square)

				except ValueError:
					continue

		return squares


class Rook(Ranged):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	moves: set[chess.algebra.Difference] = {
		chess.algebra.Difference.N,
		chess.algebra.Difference.E,
		chess.algebra.Difference.S,
		chess.algebra.Difference.W,
	}


class Bishop(Ranged):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	moves: set[chess.algebra.Difference] = {
		chess.algebra.Difference.NE,
		chess.algebra.Difference.SE,
		chess.algebra.Difference.SW,
		chess.algebra.Difference.NW,
	}

class Knight(Melee):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

	moves: set[chess.algebra.Difference] = {
		straight + diagonal for straight, diagonal in itertools.product(Rook.moves, Bishop.moves)
	} - Rook.moves
#	moves: set[chess.geometry.Difference] = {
#		chess.geometry.Difference.N2E,
#		chess.geometry.Difference.NE2,
#		chess.geometry.Difference.SE2,
#		chess.geometry.Difference.S2E,
#		chess.geometry.Difference.S2W,
#		chess.geometry.Difference.SW2,
#		chess.geometry.Difference.NW2,
#		chess.geometry.Difference.N2W,
#	}


class Queen(Rook, Bishop):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Queen):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = super().squares

		if self.square is not None:
			if chess.rules.CastleShort(self.game, self.side): squares.add(self.square + chess.algebra.Difference.E2)
			if chess.rules.CastleLong (self.game, self.side): squares.add(self.square + chess.algebra.Difference.W2)

		return squares


	def safe(self,
		square: chess.algebra.Square | None = None
	) -> bool:
		if square is None:
			square = self.square

		return True
