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

	game.draw(screen)

	pygame.display.flip()

pygame.quit()
