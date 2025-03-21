from __future__ import annotations


from abc import abstractmethod
from copy import copy

import pygame



RESOLUTION = 1152
WINDOW = (
	RESOLUTION,
	RESOLUTION,
)

BOARD_W = RESOLUTION
BOARD_H = BOARD_W * 8 // 9
BOARD = (
	BOARD_W,
	BOARD_H,
)
BOARD_OFFSET = BOARD_W - BOARD_H

SQUARE_W = BOARD_W // 8
SQUARE_H = BOARD_H // 8
SQUARE = (
	SQUARE_W,
	SQUARE_H,
)
SQUARE_OFFSET = SQUARE_W // 2

PIECE_W = BOARD_W *   5 //  32
PIECE_H = PIECE_W * 460 // 360
PIECE = (
	PIECE_W,
	PIECE_H,
)
PIECE_OFFSET = (PIECE_H - SQUARE_W) // 2

BRIGHT = (
	0x66,
	0x66,
	0x66,
)
DARK = (
	0x33,
	0x33,
	0x33,
)
RED = (
	0x99,
	0x00,
	0x00,
)
GREEN = (
	0x66,
	0x99,
	0x33,
)
BLUE = (
	0x66,
	0x99,
	0xCC,
)

WHITE = (
	0xFF,
	0xEE,
	0xDD,
)
EMPTY = (
	0xCC,
	0xBB,
	0xAA,
)
BLACK = (
	0x99,
	0x88,
	0x77,
)

class Drawable(pygame.sprite.Sprite):

	def __init__(self, *args):
		super().__init__()

		self.surf: pygame.Surface
		self.rect: pygame.Rect


	@property
	@abstractmethod
	def decal(self) -> str:
		raise NotImplementedError


	def draw(self, screen: pygame.Surface, *,
		special_flags: int,
	):
		screen.blit(
			self.surf,
			self.rect, special_flags = special_flags,
		)


class Highlightable(Drawable):

	highlight_color: tuple[
		int,
		int,
		int,
	] = BRIGHT


	@abstractmethod
	def clicked(self, event: pygame.event.Event) -> bool:
		return NotImplemented

	def highlight(self, screen: pygame.Surface):
		surf = copy(self.surf)
		surf.fill(self.highlight_color,
			special_flags = pygame.BLEND_RGB_ADD,
		)
		screen.blit(surf, self.rect)
