from __future__ import annotations


from chess import Square
from chess import Piece


class Move:

	def __init__(self, piece: Piece, square: Square):
		self.piece = piece
		self.source = self.piece.square
		self.target = square
