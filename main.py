from __future__ import annotations


import pygame;

import chess.theme
import chess.engine


pygame.init()
screen = pygame.display.set_mode(chess.theme.WINDOW)

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

running = True

game = chess.engine.Game()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		game.clicked(event)

	screen.fill(BACKGROUND)
	screen.fill(GREY, special_flags = pygame.BLEND_RGBA_MULT)

	game.draw(screen)

	pygame.display.flip()

pygame.quit()
