from __future__ import annotations


import pygame

import src.engine

from app.controller import GameController, InteractionState
from app.layout import BoardLayout, LayoutSpec
from app.theme import load_appearance
from app.views import GameView


def main() -> None:
	pygame.init()

	layout_spec = LayoutSpec()
	screen = pygame.display.set_mode(layout_spec.window)
	appearance = load_appearance(layout_spec)
	layout = BoardLayout(layout_spec)
	game = src.engine.Game.from_forsyth_edwards()
	state = InteractionState()
	controller = GameController(game, layout, state)
	view = GameView(layout, appearance)

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
				pygame.image.save(screen, "game/screenshot.png")

			controller.handle(event)

		screen.fill(appearance.board.palette.background)
		screen.fill(appearance.board.palette.flash,
			special_flags = pygame.BLEND_RGBA_MULT,
		)
		view.draw(screen, game, state)
		pygame.display.flip()

	pygame.quit()


if __name__ == "__main__":
	main()
