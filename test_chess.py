from __future__ import annotations


from chess.algebra import Square
from chess.material import King, Rook
from chess.engine import Game


def test_board_side_ref():

	game = Game()

	for square in Square.range(Square.A8, Square.A6):
		assert game.black[square] is game[+square]
		assert game.white[square] is game[-square]

	assert game[Square.E8] is game.black.king and isinstance(game.black.king, King)
	assert game[Square.E1] is game.white.king and isinstance(game.white.king, King)

	assert game[Square.A8] is game.black.left_rook and isinstance(game.black.left_rook, Rook)
	assert game[Square.A1] is game.white.left_rook and isinstance(game.white.left_rook, Rook)

	assert game[Square.H8] is game.black.right_rook and isinstance(game.black.right_rook, Rook)
	assert game[Square.H1] is game.white.right_rook and isinstance(game.white.right_rook, Rook)
