from __future__ import annotations


import pygame

import src.engine

from app.controller import GameController, InteractionState
from app.layout import BoardLayout
from app.theme import DEFAULT_THEME, load_theme, theme_spec
from app.views import GameView


def main() -> None:
	pygame.init()

	spec = theme_spec(DEFAULT_THEME)
	screen = pygame.display.set_mode(spec.layout.window)
	theme = load_theme(spec.name)
	layout = BoardLayout(spec.layout)
	game = src.engine.Game.from_forsyth_edwards()
	state = InteractionState()
	controller = GameController(game, layout, state)
	view = GameView(layout, theme)

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
				pygame.image.save(screen, "game/screenshot.png")

			controller.handle(event)

		screen.fill(theme.palette.dark)
		screen.fill(theme.palette.flash,
			special_flags = pygame.BLEND_RGBA_MULT,
		)
		view.draw(screen, game, state)
		pygame.display.flip()

	pygame.quit()


if __name__ == "__main__":
	main()
