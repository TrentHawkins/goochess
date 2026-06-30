from __future__ import annotations


import os

import pytest


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture
def pygame_screen():
	import pygame

	from app.layout import LayoutSpec

	pygame.init()
	screen = pygame.display.set_mode(LayoutSpec().window)
	yield screen
	pygame.quit()
