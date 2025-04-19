from __future__ import annotations


import pygame  #; pygame.init()

import src.theme
import src.engine


running = True

game = src.engine.Game.from_forsyth_edwards()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		game.clicked(event)

	game.draw(src.theme.screen)

	pygame.display.flip()

pygame.quit()
