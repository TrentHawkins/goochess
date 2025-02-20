from __future__ import annotations


from datetime import datetime
from os import linesep
from typing import Iterable

from chess import DEFAULT
from chess import Color, File, Difference, Square
from chess import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class Board(list[Piece | None]):

	def __init__(self):
		super().__init__(None for _ in Square)

	def __repr__(self) -> str:
		representation  = ""
		representation += "▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖" + linesep
		representation += "▐▌  A B C D E F G H  ▐▌" + linesep

		for index, piece in enumerate(self):
			square = Square(index)
			square_representation = repr(square)

			if piece is not None:
				piece_color = DEFAULT.pieces.black if piece.color else DEFAULT.pieces.white
				square_representation = square_representation.replace(" ", piece_color.bg(piece.black))

			if square.file == File.A_:
				representation += "▐▌" + repr(square.rank)

			representation += square_representation + "\x1b[D"

			if square.file == File.H_:
				representation += "\x1b[C" + repr(square.rank) + "▐▌" + linesep

		representation += "▐▌  A B C D E F G H  ▐▌" + linesep
		representation += "▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘"

		return representation

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
