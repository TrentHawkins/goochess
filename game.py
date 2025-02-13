from __future__ import annotations


from datetime import datetime
from os import linesep
from typing import Iterable

from chess import Color
from chess import Square
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


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece
		self.source = self.piece.square
		self.target = square


class Side(list[Piece]):

	def __init__(self, color: Color):
		super().__init__(
			[
				Rook  (color),
				Knight(color),
				Bishop(color),
				Queen (color) if color + 1 else King  (color),
				King  (color) if color + 1 else Queen (color),
				Bishop(color),
				Knight(color),
				Rook  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
				Pawn  (color),
			]
		)


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)
