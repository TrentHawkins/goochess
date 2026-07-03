from __future__ import annotations


from dataclasses import dataclass

import pygame

import src.algebra
import src.engine
import src.material
import src.rules

from app.controller import InteractionState
from app.layout import BoardLayout
from app.theme import Appearance, BoardTheme, PieceTheme, RGB


@dataclass(frozen = True, slots = True)
class SquareView:

	square: src.algebra.Square

	layout: BoardLayout
	theme: BoardTheme


	@property
	def rect(self) -> pygame.Rect:
		return self.layout.square_rect(self.square)


	def draw(self, screen: pygame.Surface):
		color = self.theme.palette.black if self.square.color else self.theme.palette.white
		screen.fill(color, self.rect)
		screen.blit(self.theme.square, self.rect,
			special_flags = pygame.BLEND_RGBA_MULT,
		)

	def highlight(self, screen: pygame.Surface, color: RGB, *,
		width: int = 1,
		thick: int = 0,
	):
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
	appearance: Appearance


	def draw(self, screen: pygame.Surface):
		if   isinstance(self.move, src.rules.Spec): color = self.appearance.board.palette.special
		elif isinstance(self.move, src.rules.Capt): color = self.appearance.board.palette.capture
		else                                      : color = self.appearance.board.palette.move

		width = 1
		thick = 0

		if isinstance(self.move, src.rules.Capt) and self.move.other is not None:
			width = self.appearance.pieces.style(self.move.other).capture_width
			thick = 8

		SquareView(self.move.target, self.layout, self.appearance.board).highlight(screen, color,
			width = width,
			thick = thick,
		)


@dataclass(frozen = True, slots = True)
class PieceView:

	piece: src.material.Piece

	layout: BoardLayout
	theme: PieceTheme


	@property
	def rect(self) -> pygame.Rect:
		style = self.theme.style(self.piece)
		base_x, base_y = self.layout.spec.piece_offset
		offset_x, offset_y = style.offset

		return self.theme.surface(self.piece).get_rect(center = self.layout.square_rect(self.piece.square).center).move(
			base_x + offset_x,
			base_y + offset_y,
		)

	def draw(self, screen: pygame.Surface, *,
		selected: bool = False,
		ghost_visible: bool = False,
	):
		surface = self.theme.surface(self.piece)

		if isinstance(self.piece, src.material.Ghost):
			surface = surface.copy()
			alpha = self.theme.effects.ghost_alpha if ghost_visible else self.theme.effects.hidden_alpha
			surface.fill((*self.theme.effects.high, alpha),
				special_flags = pygame.BLEND_RGBA_MULT,
			)

		elif selected:
			surface = surface.copy()
			surface.fill(self.theme.effects.selected,
				special_flags = pygame.BLEND_RGB_ADD,
			)

		screen.blit(surface, self.rect)

	def draw_promotion(self, screen: pygame.Surface, officer: src.material.Officer):
		screen.blit(
			self.theme.officer_surface(officer, self.piece.color),
			self.rect,
		)


@dataclass(frozen = True, slots = True)
class BoardView:

	board: src.engine.Board

	layout: BoardLayout
	theme: BoardTheme


	def label(self, screen: pygame.Surface, item: src.algebra.File | src.algebra.Rank, rect: pygame.Rect):
		text = self.theme.font.render(repr(item).upper(), True, self.theme.palette.label)
		text = pygame.transform.smoothscale(text, (text.get_width(), text.get_height() * 8 // 9))
		text_rect = text.get_rect(
			center = rect.center - pygame.Vector2(0, self.layout.spec.square_size[1] // 126),
		)
		screen.blit(text, text_rect)

	def draw(self, screen: pygame.Surface):
		board_w, board_h = self.layout.spec.board_size
		board_rect = self.layout.board_rect
		square_w, square_h = self.layout.spec.square_size
		frame = self.theme.frame

		for file in src.algebra.File:
			if frame is None:
				rect = self.layout.file_rect(file)
				other = rect.move(0, board_h + rect.height)

			else:
				rect = frame.file.get_rect(
					left = board_rect.left + square_w * int(file),
					bottom = board_rect.top,
				)
				other = rect.move(0, board_h + rect.height)
				screen.blit(frame.file, rect)
				screen.blit(frame.file, other)

			self.label(screen, file, rect)
			self.label(screen, file, other)

		for rank in src.algebra.Rank:
			if frame is None:
				rect = self.layout.rank_rect(rank)
				other = rect.move(board_w + rect.width, 0)

			else:
				rect = frame.rank.get_rect(
					right = board_rect.left,
					top = board_rect.top + square_h * (int(rank) >> 3),
				)
				other = rect.move(board_w + rect.width, 0)
				screen.blit(frame.rank, rect)
				screen.blit(frame.rank, other)

			self.label(screen, rank, rect)
			self.label(screen, rank, other)

		for square in src.algebra.Square:
			SquareView(square, self.layout, self.theme).draw(screen)

		if frame is not None:
			screen.blit(frame.corner, frame.corner.get_rect(right = board_rect.left, bottom = board_rect.top))
			screen.blit(frame.corner, frame.corner.get_rect(right = board_rect.left, top = board_rect.bottom))
			screen.blit(frame.corner, frame.corner.get_rect(left = board_rect.right, top = board_rect.bottom))
			screen.blit(frame.corner, frame.corner.get_rect(left = board_rect.right, bottom = board_rect.top))

		screen.blit(self.theme.background, self.theme.background.get_rect(),
			special_flags = pygame.BLEND_RGBA_MULT,
		)


@dataclass(frozen = True, slots = True)
class GameView:

	layout: BoardLayout
	appearance: Appearance


	def draw(self,
		screen: pygame.Surface,
		game: src.engine.Game,
		state: InteractionState,
	):
		BoardView(game, self.layout, self.appearance.board).draw(screen)

		moves: tuple[src.rules.Move, ...] = ()

		if state.selected is not None:
			if state.promotion is not None: moves = (state.promotion,)
			else                          : moves = tuple(state.selected.squares)

			for move in moves:
				MoveView(move, self.layout, self.appearance).draw(screen)

		visible_ghosts = {move.other for move in moves if isinstance(move, src.rules.EnPassant) and move.other is not None}

		for piece in game:
			if piece is None:
				continue

			view = PieceView(piece, self.layout, self.appearance.pieces)

			if piece is state.selected and state.promotion is not None:
				view.draw_promotion(screen, state.promotion.officer)

			else:
				view.draw(screen,
					selected = piece is state.selected,
					ghost_visible = piece in visible_ghosts,
				)
