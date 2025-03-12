from __future__ import annotations


from abc import ABC as AbstractClass, abstractmethod

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


class Decal(pygame.sprite.Sprite, AbstractClass):

	@abstractmethod
	def draw(self, screen: pygame.Surface):
		...
