from __future__ import annotations


from abc import abstractmethod

import pygame



RESOLUTION = 1152
WINDOW = (
	RESOLUTION,
	RESOLUTION,
)

BOARD_W = RESOLUTION
BOARD_H = BOARD_W * 7 // 8
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


class Drawable(pygame.sprite.Sprite):

	def __init__(self, *args, **kwargs):
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

	highlight_color = (
		85,
		85,
		85,
		85,
	)


	@abstractmethod
	def clicked(self, event: pygame.event.Event) -> bool:
		raise NotImplementedError

	def highlight(self, screen: pygame.Surface):
		surf = self.surf.copy()
		surf.fill(self.highlight_color,
			special_flags = pygame.BLEND_RGB_ADD,
		)
		screen.blit(surf, self.rect)

