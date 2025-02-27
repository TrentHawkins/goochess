from __future__ import annotations


from contextlib import contextmanager
from datetime import datetime
import os
import typing

import chess.theme
import chess.algebra
import chess.material


black = chess.theme.DEFAULT.square.black.fg; C = "\x1b[C"
white = chess.theme.DEFAULT.square.white.bg; D = "\x1b[D"


def color(string: str) -> str: return black(white(string))


Square = chess.algebra.Square
Piece = chess.material.Piece | None


class Board(list[Piece]):

	def __init__(self):
		super().__init__(None for _ in Square)

	def __repr__(self) -> str:
		representation = ""
		representation += black("▗"  +       "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"  +       "▖") + os.linesep
		representation += black("▐") + color("▌  A B C D E F G H  ▐") + black("▌") + os.linesep

		for index, piece in enumerate(self):
			square = Square(index)

			if square.file == chess.algebra.File.A_:
				representation += black("▐") + color("▌" + repr(square.rank))

			representation += str(square).replace(" ", str(piece) if piece is not None else " ") + D

			if square.file == chess.algebra.File.H_:
				representation += C + color(repr(square.rank) + "▐") + black("▌") + os.linesep

		representation += black("▐") + color("▌  A B C D E F G H  ▐") + black("▌") + os.linesep
		representation += black("▝"  +       "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"  +       "▘")

		return representation

	def __setitem__(self, key: Square | slice, value: Piece | typing.Iterable[Piece]):
		if isinstance(key, Square): key = slice(key, key + 1, +1)
		if isinstance(value, Piece): value = [value]

		for integer, piece in zip(range(*key.indices(len(self))), value):
			self.update(Square(integer), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: Square | slice):
		if isinstance(key, Square): key = slice(key, key + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	def update(self, square: Square,
		piece: Piece = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None


class Side(list[chess.material.Piece]):

	def __init__(self, game: Game, color: chess.algebra.Color):
		self.game = game
		self.color = color

		super().__init__(
			[
				chess.material.Rook  (self),
				chess.material.Knight(self),
				chess.material.Bishop(self),
				chess.material.Queen (self) if self.color else
				chess.material.King  (self),
				chess.material.King  (self) if self.color else
				chess.material.Queen (self),
				chess.material.Bishop(self),
				chess.material.Knight(self),
				chess.material.Rook  (self),

				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
			]
		)

		self.ghost = chess.material.Piece(self)


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)

	@property
	def targets(self) -> set[Square]:
		return set().union(*(piece.targets for piece in self))

	@property
	def other(self) -> Side:
		return self.game.white if self.color else self.game.black

	@property
	def king(self) -> chess.material.King:
		return typing.cast(chess.material.King,
			self[
				Square.E8 if self.color else
				Square.D8
			]
		)

	@property
	def left_rook(self) -> chess.material.Rook:
		return typing.cast(chess.material.Rook,
			self[
				Square.A8 if self.color else
				Square.H8
			]
		)

	@property
	def right_rook(self) -> chess.material.Rook:
		return typing.cast(chess.material.Rook,
			self[
				Square.H8 if self.color else
				Square.A8
			]
		)

class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(self, chess.algebra.Color.BLACK)
		self.white = Side(self, chess.algebra.Color.WHITE)

		self[+Square.A8:+Square.A6:chess.algebra.Difference.E] = self.black
		self[-Square.A8:-Square.A6:chess.algebra.Difference.W] = self.white

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())
