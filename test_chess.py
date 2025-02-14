from chess import Square, King, Game


def test_board_side_ref():

	game = Game()

	for square in Square.range(Square.A8, Square.A6):
		assert game.black[square] is game[+square]
		assert game.white[square] is game[-square]

	assert game[Square.E8] is game.black.king and isinstance(game.black.king, King)
	assert game[Square.E1] is game.white.king and isinstance(game.black.king, King)
