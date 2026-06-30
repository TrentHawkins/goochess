from __future__ import annotations


from dataclasses import dataclass

import pygame

import src.algebra
import src.engine
import src.material
import src.rules

from app.controller import InteractionState
from app.layout import BoardLayout
from app.theme import RGB, Theme


@dataclass(frozen = True, slots = True)
class SquareView:

	square: src.algebra.Square
	layout: BoardLayout
	theme: Theme


	@property
	def rect(self) -> pygame.Rect:
		return self.layout.square_rect(self.square)

	def draw(self, screen: pygame.Surface) -> None:
		color = self.theme.palette.black if self.square.color else self.theme.palette.white
		screen.fill(color, self.rect)
		screen.blit(self.theme.square, self.rect,
			special_flags = pygame.BLEND_RGBA_MULT,
		)

	def highlight(self, screen: pygame.Surface, color: RGB, *,
		width: int = 1,
		thick: int = 0,
	) -> None:
		rect = self.rect.inflate(
			-self.rect.width  // (width + 1) * 24 // 25,
			-self.rect.height // (width + 1) * 24 // 25,
		)
		surface = pygame.Surface(rect.size,
			flags = pygame.SRCALPHA,
		)
		pygame.draw.ellipse(surface, color, surface.get_rect(), thick * self.rect.width // 128)
		screen.blit(surface, rect,
			special_flags = pygame.BLEND_RGB_ADD,
		)


@dataclass(frozen = True, slots = True)
class MoveView:

	move: src.rules.Move
	layout: BoardLayout
	theme: Theme


	def draw(self, screen: pygame.Surface) -> None:
		if isinstance(self.move, src.rules.Spec):
			color = self.theme.palette.blue
		elif isinstance(self.move, src.rules.Capt):
			color = self.theme.palette.red
		else:
			color = self.theme.palette.green

		width = 1
		thick = 0
		if isinstance(self.move, src.rules.Capt) and self.move.other is not None:
			width = self.theme.piece_style(self.move.other).capture_width
			thick = 8

		SquareView(self.move.target, self.layout, self.theme).highlight(
			screen,
			color,
			width = width,
			thick = thick,
		)


@dataclass(frozen = True, slots = True)
class PieceView:

	piece: src.material.Piece
	layout: BoardLayout
	theme: Theme


	@property
	def rect(self) -> pygame.Rect:
		style = self.theme.piece_style(self.piece)
		base_x, base_y = self.theme.layout.piece_offset
		offset_x, offset_y = style.offset

		return self.theme.piece_surface(self.piece).get_rect(
			center = self.layout.square_rect(self.piece.square).center,
		).move(base_x + offset_x, base_y + offset_y)

	def draw(self, screen: pygame.Surface, *,
		selected: bool = False,
		ghost_visible: bool = False,
	) -> None:
		surface = self.theme.piece_surface(self.piece)

		if isinstance(self.piece, src.material.Ghost):
			surface = surface.copy()
			alpha = 170 if ghost_visible else 0
			surface.fill((*self.theme.palette.high, alpha),
				special_flags = pygame.BLEND_RGBA_MULT,
			)
		elif selected:
			surface = surface.copy()
			surface.fill(self.theme.palette.bright,
				special_flags = pygame.BLEND_RGB_ADD,
			)

		screen.blit(surface, self.rect)

	def draw_promotion(self, screen: pygame.Surface, officer: src.material.Officer) -> None:
		screen.blit(
			self.theme.officer_surface(officer, self.piece.color),
			self.rect,
		)


@dataclass(frozen = True, slots = True)
class BoardView:

	board: src.engine.Board
	layout: BoardLayout
	theme: Theme


	def label(self, screen: pygame.Surface, item: src.algebra.File | src.algebra.Rank, rect: pygame.Rect) -> None:
		text = self.theme.font.render(repr(item).upper(), True, self.theme.palette.label)
		text = pygame.transform.smoothscale(text,
			(text.get_width(), text.get_height() * 8 // 9),
		)
		text_rect = text.get_rect(
			center = rect.center - pygame.Vector2(0, self.theme.layout.square_size[1] // 126),
		)
		screen.blit(text, text_rect)

	def draw(self, screen: pygame.Surface) -> None:
		board_w, board_h = self.theme.layout.board_size
		corner_w, corner_h = self.theme.layout.corner_size

		for file in src.algebra.File:
			rect = self.layout.file_rect(file)
			self.label(screen, file, rect)
			self.label(screen, file, rect.move(0, board_h + corner_h))

		for rank in src.algebra.Rank:
			rect = self.layout.rank_rect(rank)
			self.label(screen, rank, rect)
			self.label(screen, rank, rect.move(board_w + corner_w, 0))

		for square in src.algebra.Square:
			SquareView(square, self.layout, self.theme).draw(screen)

		screen.blit(self.theme.background, self.theme.background.get_rect(),
			special_flags = pygame.BLEND_RGBA_MULT,
		)


@dataclass(frozen = True, slots = True)
class GameView:

	layout: BoardLayout
	theme: Theme


	def draw(self,
		screen: pygame.Surface,
		game: src.engine.Game,
		state: InteractionState,
	) -> None:
		BoardView(game, self.layout, self.theme).draw(screen)

		moves: tuple[src.rules.Move, ...] = ()
		if state.selected is not None:
			if state.promotion is not None:
				moves = (state.promotion,)
			else:
				moves = tuple(state.selected.squares)

			for move in moves:
				MoveView(move, self.layout, self.theme).draw(screen)

		visible_ghosts = {
			move.other
			for move in moves
			if isinstance(move, src.rules.EnPassant) and move.other is not None
		}

		for piece in game:
			if piece is None:
				continue

			view = PieceView(piece, self.layout, self.theme)
			if piece is state.selected and state.promotion is not None:
				view.draw_promotion(screen, state.promotion.officer)
			else:
				view.draw(
					screen,
					selected = piece is state.selected,
					ghost_visible = piece in visible_ghosts,
				)
