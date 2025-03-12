from __future__ import annotations


import pygame

import chess.theme
import chess.engine


BACKGROUND = (
	204,
	187,
	170,
)
GREY = (
	85,
	85,
	85,
)

pygame.init()

screen = pygame.display.set_mode(chess.theme.WINDOW)
running = True

game = chess.engine.Game()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	screen.fill(BACKGROUND)
	screen.fill(GREY, special_flags = pygame.BLEND_RGBA_MULT)

	game.draw(screen)

	pygame.display.flip()

pygame.quit()
