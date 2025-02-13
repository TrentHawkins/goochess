from chess import *


def test_board_side_ref():

	game = Game()

	for square in Square.range(Square.A8, Square.A6):
		assert game.black[square] is game[+square]
		assert game.white[square] is game[-square]
