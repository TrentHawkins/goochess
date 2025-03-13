from __future__ import annotations


from datetime import datetime
import os
import pathlib
import typing

import pygame

import chess.theme
import chess.algebra
import chess.material


Piece = chess.material.Piece | None


class Board(list[Piece], pygame.sprite.Sprite):

	def __init__(self):
		super().__init__(None for _ in chess.algebra.Square)

		self.surf = pygame.transform.smoothscale(pygame.image.load(self.decal).convert(), chess.theme.WINDOW)
		self.rect = self.surf.get_rect(
			center = pygame.Vector2(
				chess.theme.RESOLUTION // 2,
				chess.theme.RESOLUTION // 2,
			)
		)

	def __repr__(self) -> str:
		...  # TODO: FEN (part)

	def __setitem__(self, key: chess.algebra.Square | slice, value: Piece | typing.Iterable[Piece]):
		if isinstance(key, chess.algebra.Square): key = slice(key, key + 1, +1)
		if isinstance(value, Piece): value = [value]

		for index, piece in zip(range(*key.indices(len(self))), value):
			self.update(chess.algebra.Square(index), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.algebra.Square | slice):
		if isinstance(key, chess.algebra.Square): key = slice(key, key + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	@property
	def decal(self) -> pathlib.Path:
		return pathlib.Path("chess/graphics/board/mask.png")


	def update(self, square: chess.algebra.Square,
		piece: Piece = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None

	def draw(self, screen: pygame.Surface):
		for square in chess.algebra.Square:
			square.draw(screen)

		screen.blit(
			self.surf,
			self.rect, special_flags = pygame.BLEND_RGBA_MULT,
		)


class Side(list[chess.material.Piece]):

	def __init__(self, game: Game, color: chess.algebra.Color):
		self.game = game
		self.color = color

		super().__init__(
			[
				chess.material.Rook  (self),
				chess.material.Knight(self),
				chess.material.Bishop(self),
				chess.material.Queen (self) if self.color else
				chess.material.King  (self),
				chess.material.King  (self) if self.color else
				chess.material.Queen (self),
				chess.material.Bishop(self),
				chess.material.Knight(self),
				chess.material.Rook  (self),

				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
				chess.material.Pawn  (self),
			]
		)

		self.ghost = chess.material.Piece(self)


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)

	@property
	def targets(self) -> set[chess.algebra.Square]:
		return set().union(*(piece.targets for piece in self))

	@property
	def other(self) -> Side:
		return self.game.white if self.color else self.game.black

	@property
	def king(self) -> chess.material.King:
		return typing.cast(chess.material.King,
			self[
				chess.algebra.Square.E8 if self.color else
				chess.algebra.Square.D8
			]
		)

	@property
	def left_rook(self) -> chess.material.Rook:
		return typing.cast(chess.material.Rook,
			self[
				chess.algebra.Square.A8 if self.color else
				chess.algebra.Square.H8
			]
		)

	@property
	def right_rook(self) -> chess.material.Rook:
		return typing.cast(chess.material.Rook,
			self[
				chess.algebra.Square.H8 if self.color else
				chess.algebra.Square.A8
			]
		)


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(self, chess.algebra.Color.BLACK)
		self.white = Side(self, chess.algebra.Color.WHITE)

		self[+chess.algebra.Square.A8:+chess.algebra.Square.A6:chess.algebra.Difference.E] = self.black
		self[-chess.algebra.Square.A8:-chess.algebra.Square.A6:chess.algebra.Difference.W] = self.white

	def __repr__(self) -> str:
		...  # TODO: FEN (full)

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())


	def draw(self, screen: pygame.Surface):
		super().draw(screen)

		for piece in self:
			if piece is not None:
				piece.draw(screen)