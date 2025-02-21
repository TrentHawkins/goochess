from __future__ import annotations


from datetime import datetime
from os import linesep
from typing import Iterable
from weakref import ref as weakref

from chess.geometry import Color, File, Difference, Square
from chess.material import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class Board(list[Piece | None]):

	def __init__(self):
		super().__init__(None for _ in Square)

	def __repr__(self) -> str:
		representation  = ""
		representation += "▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖" + linesep
		representation += "▐▌  A B C D E F G H  ▐▌" + linesep

		for index, piece in enumerate(self):
			square = Square(index)
			square_representation = str(square)

			if piece is not None:
				square_representation = square_representation.replace(" ", str(piece))

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

	def __init__(self, color: Color, game: Game):
		self.game = game

		super().__init__(
			[
				Rook  (color, self.game),
				Knight(color, self.game),
				Bishop(color, self.game),
				Queen (color, self.game) if color else
				King  (color, self.game),
				King  (color, self.game) if color else
				Queen (color, self.game),
				Bishop(color, self.game),
				Knight(color, self.game),
				Rook  (color, self.game),

				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
				Pawn  (color, self.game),
			]
		)

		self.king = self[Square.E8 if color else Square.D8]
		self.ghost = Piece(color, self.game)


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(Color.BLACK, self)
		self.white = Side(Color.WHITE, self)

		self[+Square.A8:+Square.A6:Difference.E] = self.black
		self[-Square.A8:-Square.A6:Difference.W] = self.white

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())
