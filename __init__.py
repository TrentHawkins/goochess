from __future__ import annotations


from datetime import datetime

from chess.base import Color
from chess.geometry import Rank, File, Square, Difference
from chess.material import Piece, Pawn, Rook, Bishop, Knight, King
from chess.game import Board, Side


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(Color.BLACK)
		self.white = Side(Color.WHITE)

		self[ Square.A8: Square.A6:+1] = self.black
		self[~Square.A8:~Square.A6:-1] = self.white

	def __hash__(self) -> int:
		return int(datetime.now().timestamp())
