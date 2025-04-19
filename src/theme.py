from __future__ import annotations


from abc import abstractmethod
from copy import copy
from enum import Enum

import pygame


type RGB = tuple[
	int,
	int,
	int,
]

RESOLUTION = 1440
WINDOW = pygame.Vector2(
	RESOLUTION,
	RESOLUTION,
)

BOARD_W = RESOLUTION
BOARD_H = BOARD_W * 8 // 9
BOARD = pygame.Vector2(
	BOARD_W,
	BOARD_H,
)
BOARD_OFFSET = BOARD_W - BOARD_H

SQUARE_W = BOARD_W // 8
SQUARE_H = BOARD_H // 8
SQUARE = pygame.Vector2(
	SQUARE_W,
	SQUARE_H,
)
SQUARE_OFFSET = SQUARE_W // 2

PIECE_W = BOARD_W *   5 //  32
PIECE_H = PIECE_W * 460 // 360
PIECE = pygame.Vector2(
	PIECE_W,
	PIECE_H,
)
PIECE_OFFSET = pygame.Vector2(
	+PIECE_W     // 100,
	-PIECE_H * 2 // 13 ,
)

HIGH = (
	0xFF,
	0xFF,
	0xFF,
)
BRIGHT = (
	0x33,
	0x33,
	0x33,
)
DARK = (
	0x33,
	0x33,
	0x33,
)
RED = (
	0x66,
	0x00,
	0x00,
)
GREEN = (
	0x22,
	0x33,
	0x11,
)
GOLD = (
	0x33,
	0x22,
	0x11,
)
BLUE = (
	0x11,
	0x22,
	0x33,
)

WHITE = (
	0xAA,
	0x99,
	0x88,
)
EMPTY = (
	0xDD,
	0xCC,
	0xBB,
)
BLACK = (
	0x77,
	0x66,
	0x55,
)


screen = pygame.display.set_mode(WINDOW)


class Main(Enum):

	BOARD  = pygame.transform.smoothscale(pygame.image.load(f"graphics/board/stone1.jpg").convert(), WINDOW)
	GAME   = pygame.transform.smoothscale(pygame.image.load(f"graphics/board/stone1.jpg").convert(), WINDOW)
	SQUARE = pygame.transform.smoothscale(pygame.image.load(f"graphics/board/bevel.png" ).convert(), SQUARE)

	BPIECE = pygame.Surface(PIECE,
		flags = pygame.SRCALPHA,
	)

	BPAWN    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/pawn.png"   ).convert_alpha(), PIECE)
	BGHOST   = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/pawn.png"   ).convert_alpha(), PIECE)
	BROOK    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/rook.png"   ).convert_alpha(), PIECE)
	BKNIGHT  = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/knight.png" ).convert_alpha(), PIECE)
	BKNIGHTR = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/knightr.png").convert_alpha(), PIECE)
	BBISHOP  = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/bishop.png" ).convert_alpha(), PIECE)
	BBISHOPR = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/bishopr.png").convert_alpha(), PIECE)
	BQUEEN   = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/queen.png"  ).convert_alpha(), PIECE)
	BKING    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/black/king.png"   ).convert_alpha(), PIECE)

	WPIECE = pygame.Surface(PIECE,
		flags = pygame.SRCALPHA,
	)

	WPAWN    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/pawn.png"   ).convert_alpha(), PIECE)
	WGHOST   = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/pawn.png"   ).convert_alpha(), PIECE)
	WROOK    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/rook.png"   ).convert_alpha(), PIECE)
	WKNIGHT  = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/knight.png" ).convert_alpha(), PIECE)
	WKNIGHTR = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/knightr.png").convert_alpha(), PIECE)
	WBISHOP  = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/bishop.png" ).convert_alpha(), PIECE)
	WBISHOPR = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/bishopr.png").convert_alpha(), PIECE)
	WQUEEN   = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/queen.png"  ).convert_alpha(), PIECE)
	WKING    = pygame.transform.smoothscale(pygame.image.load(f"graphics/piece/white/king.png"   ).convert_alpha(), PIECE)


class Drawable(pygame.sprite.Sprite):

	def __init__(self, *args):
		super().__init__(*args)


	@property
	def decal(self) -> str:
		return self.__class__.__name__

	@property
	def surf(self) -> pygame.Surface:
		return Main[self.decal.upper()].value

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect()


	def draw(self, screen: pygame.Surface, *,
		special_flags: int,
	):
		screen.blit(
			self.surf,
			self.rect, special_flags = special_flags,
		)


class Highlightable(Drawable):

	highlight_color: RGB = BRIGHT


	@abstractmethod
	def clicked(self, event: pygame.event.Event) -> bool:
		return NotImplemented

	def highlight(self, screen: pygame.Surface,
		highlight_color: RGB | None = None,
	):
		surf = copy(self.surf)
		surf.fill(highlight_color if highlight_color is not None else self.highlight_color,
			special_flags = pygame.BLEND_RGB_ADD,
		)
		screen.blit(surf, self.rect)
