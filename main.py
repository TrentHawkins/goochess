from __future__ import annotations


import pygame  #; pygame.init()

import chess.theme
import chess.engine


running = True

game = chess.engine.Game()

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
