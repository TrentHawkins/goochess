from __future__ import annotations


import pygame  #; pygame.init()

import chess.theme
import chess.engine


running = True

game = chess.engine.Game.from_forsyth_edwards()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		game.clicked(event)

	game.draw(chess.theme.screen)

	pygame.display.flip()

pygame.quit()
