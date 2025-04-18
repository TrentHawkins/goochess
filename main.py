from __future__ import annotations


import pygame  #; pygame.init()

import chess.theme
import chess.engine


running = True

game = chess.engine.Game.from_forsyth_edwards("rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 1")

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		game.clicked(event)

	chess.theme.screen.fill(chess.theme.EMPTY)
	chess.theme.screen.fill(chess.theme.DARK, special_flags = pygame.BLEND_RGBA_MULT)

	game.draw(chess.theme.screen)

	pygame.display.flip()

pygame.quit()
