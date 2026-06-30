from __future__ import annotations


from dataclasses import dataclass

import pygame

import src.algebra


@dataclass(frozen = True, slots = True)
class LayoutSpec:

	window: tuple[int, int] = (2160, 1440)
	board_width: int = 1440


	@property
	def board_height(self) -> int:
		return self.board_width * 8 // 9

	@property
	def board_size(self) -> tuple[int, int]:
		return self.board_width, self.board_height

	@property
	def board_offset(self) -> tuple[int, int]:
		return (
			(self.window[0] - self.board_width) // 2,
			(self.board_width - self.board_height) * 3 // 4,
		)

	@property
	def square_size(self) -> tuple[int, int]:
		return self.board_width // 8, self.board_height // 8

	@property
	def corner_size(self) -> tuple[int, int]:
		square_w, square_h = self.square_size
		return square_w // 4, square_h // 4

	@property
	def file_size(self) -> tuple[int, int]:
		square_w, _ = self.square_size
		_, corner_h = self.corner_size
		return square_w, corner_h

	@property
	def rank_size(self) -> tuple[int, int]:
		_, square_h = self.square_size
		corner_w, _ = self.corner_size
		return corner_w, square_h

	@property
	def piece_size(self) -> tuple[int, int]:
		width = self.board_width * 5 // 32
		return width, width * 460 // 360

	@property
	def piece_offset(self) -> tuple[int, int]:
		piece_w, piece_h = self.piece_size
		return piece_w // 100, -piece_h * 4 // 27


@dataclass(frozen = True, slots = True)
class BoardLayout:

	spec: LayoutSpec


	@property
	def board_rect(self) -> pygame.Rect:
		return pygame.Rect(self.spec.board_offset, self.spec.board_size)

	def square_rect(self, square: src.algebra.Square) -> pygame.Rect:
		square_w, square_h = self.spec.square_size
		offset_x, offset_y = self.spec.board_offset

		return pygame.Rect(
			offset_x + square_w * int(square.file),
			offset_y + square_h * (int(square.rank) >> 3),
			square_w,
			square_h,
		)

	def square_at(self, position: tuple[int, int]) -> src.algebra.Square | None:
		if not self.board_rect.collidepoint(position):
			return None

		offset_x, offset_y = self.spec.board_offset
		square_w, square_h = self.spec.square_size
		file = (position[0] - offset_x) // square_w
		rank = (position[1] - offset_y) // square_h

		return src.algebra.Square((rank << 3) + file)

	def file_rect(self, file: src.algebra.File) -> pygame.Rect:
		square_w, _ = self.spec.square_size
		_, corner_h = self.spec.corner_size
		offset_x, offset_y = self.spec.board_offset

		return pygame.Rect(
			offset_x + square_w * int(file),
			offset_y - corner_h,
			*self.spec.file_size,
		)

	def rank_rect(self, rank: src.algebra.Rank) -> pygame.Rect:
		_, square_h = self.spec.square_size
		corner_w, _ = self.spec.corner_size
		offset_x, offset_y = self.spec.board_offset

		return pygame.Rect(
			offset_x - corner_w,
			offset_y + square_h * (int(rank) >> 3),
			*self.spec.rank_size,
		)
