from chess import *


class TestChess:

	def test_board(self):

		board = Board()
		board[Square.A1] = Rook(Color.WHITE)
