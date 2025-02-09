from __future__ import annotations


import os

from chess.base import Color
from chess.geometry import Square
from chess.material import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class Board(list[Piece | None]):

	def __init__(self):
		super().__init__(None for _ in Square)

	def __repr__(self) -> str:
		representation = ""

		for square in Square:
			if not square % 8:
				representation += os.linesep

			representation += repr(square.color)

		return representation + os.linesep

	def __setitem__(self, square: Square, piece: Piece | None):
		if piece is not None:
			piece.square = square

		del self[square]  # capture the existing piece if any

		super().__setitem__(square, piece)

	def __delitem__(self, square: Square):
		piece = self[square]

		if piece is not None:
			piece.square = None

			super().__delitem__(square)


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece
		self.source = self.piece.square
		self.target = square


class Side(set[Piece]):

	def __init__(self, *args):
		super().__init__(*args)


	@property
	def captured(self) -> set[Piece]:
		return set(piece for piece in self if piece.square is None)


class Position(Board):

	def __init__(self):
		super().__init__()

		self[Square.A8] = Rook  (Color.BLACK)
		self[Square.B8] = Knight(Color.BLACK)
		self[Square.C8] = Bishop(Color.BLACK)
		self[Square.D8] = Queen (Color.BLACK)
		self[Square.E8] = King  (Color.BLACK)
		self[Square.F8] = Bishop(Color.BLACK)
		self[Square.G8] = Knight(Color.BLACK)
		self[Square.H8] = Rook  (Color.BLACK)
		self[Square.A7] = Pawn  (Color.BLACK)
		self[Square.B7] = Pawn  (Color.BLACK)
		self[Square.C7] = Pawn  (Color.BLACK)
		self[Square.D7] = Pawn  (Color.BLACK)
		self[Square.E7] = Pawn  (Color.BLACK)
		self[Square.F7] = Pawn  (Color.BLACK)
		self[Square.G7] = Pawn  (Color.BLACK)
		self[Square.H7] = Pawn  (Color.BLACK)
		self[Square.A2] = Pawn  (Color.WHITE)
		self[Square.B2] = Pawn  (Color.WHITE)
		self[Square.C2] = Pawn  (Color.WHITE)
		self[Square.D2] = Pawn  (Color.WHITE)
		self[Square.E2] = Pawn  (Color.WHITE)
		self[Square.F2] = Pawn  (Color.WHITE)
		self[Square.G2] = Pawn  (Color.WHITE)
		self[Square.H2] = Pawn  (Color.WHITE)
		self[Square.A1] = Rook  (Color.WHITE)
		self[Square.B1] = Knight(Color.WHITE)
		self[Square.C1] = Bishop(Color.WHITE)
		self[Square.D1] = Queen (Color.WHITE)
		self[Square.E1] = King  (Color.WHITE)
		self[Square.F1] = Bishop(Color.WHITE)
		self[Square.G1] = Knight(Color.WHITE)
		self[Square.H1] = Rook  (Color.WHITE)

		self.black = Side(piece for piece in self if piece is not None and piece.color == Color.BLACK)
		self.white = Side(piece for piece in self if piece is not None and piece.color == Color.WHITE)
