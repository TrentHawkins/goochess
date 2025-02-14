from __future__ import annotations


from datetime import datetime
from os import linesep
from typing import Iterable

from chess import Color
from chess import Difference, Square
from chess import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class Board(list[Piece | None]):

	def __init__(self):
		super().__init__(None for _ in Square)

	def __repr__(self) -> str:
		representation = ""

		for square in Square:
			if not square % 8:
				representation += linesep

			representation += repr(square.color)

		return representation + linesep

	def __setitem__(self, key: Square | slice, value: Piece | None | Iterable[Piece | None]):
		if isinstance(key, Square):	key = slice(key, key + 1, +1)
		if isinstance(value, Piece | None): value = [value]

		for integer, piece in zip(range(*key.indices(len(self))), value):
			self.update(Square(integer), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: Square | slice):
		if isinstance(key, Square):	key = slice(key, key + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	def update(self, square: Square,
		piece: Piece | None = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None


class Side(list[Piece]):

	def __init__(self, color: Color):
		super().__init__(
			[
				Rook  (color),
				Knight(color),
				Bishop(color),
				Queen (color) if color else King  (color),
				King  (color) if color else Queen (color),
				Bishop(color),
				Knight(color),
				Rook  (color),
			] + [
				Pawn  (color),
			] * 0o10
		)

		self.king = self[Square.E8 if color else Square.D8]


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(Color.BLACK)
		self.white = Side(Color.WHITE)

		self[+Square.A8:+Square.A6:Difference.E] = self.black
		self[-Square.A8:-Square.A6:Difference.W] = self.white

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())
