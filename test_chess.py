import chess.base
import chess.geometry
import chess.material
import chess.game


class TestChess:

	def test_board(self):

		board = chess.game.Board()
		board[chess.geometry.Square.A1] = chess.material.Rook(chess.base.Color.WHITE)
