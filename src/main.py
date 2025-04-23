from __future__ import annotations


import pygame; pygame.init()

import src.theme
import src.engine


running = True

game = src.engine.Game.from_forsyth_edwards()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F12:
				pygame.image.save(src.theme.screen, "game/screenshot.png")

		game.clicked(event)

	src.theme.screen.fill(src.theme.EMPTY)
	src.theme.screen.fill(src.theme.DARK,
		special_flags = pygame.BLEND_RGBA_MULT,
	)

	game.draw(src.theme.screen)

	pygame.display.flip()

pygame.quit()
