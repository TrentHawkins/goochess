from __future__ import annotations


import pygame

import chess.theme
import chess.engine


pygame.init()
screen = pygame.display.set_mode(chess.theme.WINDOW)

running = True

game = chess.engine.Game()

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		game.clicked(event)

	screen.fill(chess.theme.EMPTY)
	screen.fill(chess.theme.DARK, special_flags = pygame.BLEND_RGBA_MULT)

	game.draw(screen)

	pygame.display.flip()

pygame.quit()
