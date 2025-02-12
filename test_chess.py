from chess import *


def test_board_side_ref():

	game = Game()

	assert game.black[0] is game[Square.A8]
	assert game.white[0] is game[Square.A1]
