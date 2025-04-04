from __future__ import annotations


from copy import copy
from pathlib import Path
from typing import TYPE_CHECKING, Self

import pygame

import chess.theme
import chess.algebra
import chess.rules

if TYPE_CHECKING: import chess.engine


class Piece(chess.theme.Highlightable):

	value: int = 0
	width: int = 0
	ghost: int = 0

	black: str = " "
	white: str = " "

	moves: chess.algebra.Vectors
	capts: chess.algebra.Vectors
	specs: chess.algebra.Vectors


	def __init__(self, side: chess.engine.Side,
		square: chess.algebra.Square | None = None,
	):
		self.side = side
		self.square = square

		self.moved: bool = False

		super().__init__()

		try: self.surf = pygame.transform.smoothscale(pygame.image.load(self.decal).convert_alpha(), chess.theme.PIECE)
		except FileNotFoundError: self.surf = pygame.Surface(chess.theme.PIECE,
			flags = pygame.SRCALPHA,
		)

	def __repr__(self) -> str:
		return self.black if self.color else self.white

	def __call__(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		self.moved = self.moved or move
		self.game[source], self.game[target] = kept, self.game[source]

		return self


	@property
	def decal(self) -> Path:
		return Path("chess/graphics/piece") / self.color.name.lower() / f"{self.__class__.__name__.lower()}.png"

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + chess.theme.PIECE_OFFSET,
		) if self.square is not None else self.surf.get_rect()

	@property
	def color(self) -> chess.algebra.Color:
		return self.side.color

	@property
	def game(self) -> chess.engine.Game:
		return self.side.game

	@property
	def king(self) -> King:
		return self.side.king

	@property
	def targets(self) -> chess.algebra.Squares:
		return chess.algebra.Squares()

	@property
	def squares(self) -> chess.algebra.Squares:
		squares = self.targets.copy()

		for step in self.targets:
			with step:
				if not self.king.safe:
					squares.discard(step)

		return squares


	def clicked(self, event: pygame.event.Event) -> bool:
		if (selected := self.square is not None and self.square.clicked(event)):
			self.game.selected = self

		return selected

	def draw(self, screen: pygame.Surface):
		if self.square is not None:
			if self.ghost:
				surf = copy(self.surf)
				surf.fill((*chess.theme.WHITE, 85 * (3 - self.ghost)),
					special_flags = pygame.BLEND_RGBA_MULT,
				)

			else:
				surf = self.surf

			screen.blit(surf, self.rect)


class Melee(Piece):

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for move in self.moves:
				try:
					if step := chess.rules.Move(self.square + move, self): targets.add(step)
					if step := chess.rules.Capt(self.square + move, self): targets.add(step)

				except ValueError:
					continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for move in self.moves:
				target = self.square

				try:
					while step := chess.rules.Move(target := target + move, self):
						targets.add(step)

				except ValueError:
					continue

				if step := chess.rules.Capt(target, self):
					targets.add(step)

		return targets


class Officer(Piece):

	width: int = 6


class Pawn(Piece):

	value: int = 1
	width: int = 2

	black: str = "\u265f"
	white: str = "\u2659"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.S,
	)
	capts = chess.algebra.Vectors(
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
	)


#	def __call__(self, target: chess.algebra.Square,
#		move: bool = True,
#		kept: Piece | None = None,
#	) -> Self:
#		assert (source := self.square) is not None
#
#		if move and not self.moved and target == source + chess.algebra.Vector.S2 * self.color:
#			self.side.ghost = self.game[source + chess.algebra.Vector.S  * self.color] = Ghost(self.side)
#
#		if move and isinstance(self.game[target], Ghost):
#			self.game[target + chess.algebra.Vector.N * self.color] = kept
#
#		return super().__call__(target, move, kept)


	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for move in self.moves * self.color:
				target = self.square

				try:
					if step := chess.rules.Move(target := target + move, self):
						targets.add(step)

						if step := chess.rules.Rush(target := target + move, self):
							targets.add(step)

				except ValueError:
					continue

			for capt in self.capts * self.color:
				try:
					target = self.square + capt

					if step := chess.rules.EnPassant(target, self): targets.add(step)
					if step := chess.rules.Capt     (target, self): targets.add(step)

				except ValueError:
					continue

		return targets

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				chess.theme.PIECE_OFFSET.x * 49 // 25,
				chess.theme.PIECE_OFFSET.y * 25 // 24,
			),
		) if self.square is not None else self.surf.get_rect()


	def promote(self, to: type):
		if issubclass(to, Officer):
			self.__class__ = to  # type: ignore

class Ghost(Piece):

	width = 2
	ghost = 3

	@property
	def decal(self) -> Path:
		return Path("chess/graphics/piece") / self.color.name.lower() / "pawn.png"

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center + pygame.Vector2(
				chess.theme.PIECE_OFFSET.x * 49 // 25,
				chess.theme.PIECE_OFFSET.y * 25 // 24,
			),
		) if self.square is not None else self.surf.get_rect()


class Rook(Ranged, Officer):

	value: int = 5
	width: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.N,
		chess.algebra.Vector.E,
		chess.algebra.Vector.S,
		chess.algebra.Vector.W,
	)


class Assymetric(Officer):

	@property
	def decal(self) -> Path:
		return super().decal.with_suffix(".flipped" + super().decal.suffix) if self.color else super().decal


class Bishop(Ranged, Assymetric, Officer):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	moves = chess.algebra.Vectors(
		chess.algebra.Vector.NE,
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
		chess.algebra.Vector.NW,
	)


class Knight(Melee, Assymetric, Officer):

	value: int = 3
	width: int = 5

	black: str = "\u265e"
	white: str = "\u2658"

#	moves = chess.algebra.Vectors(
#		chess.algebra.Vector.N2E,
#		chess.algebra.Vector.NE2,
#		chess.algebra.Vector.SE2,
#		chess.algebra.Vector.S2E,
#		chess.algebra.Vector.S2W,
#		chess.algebra.Vector.SW2,
#		chess.algebra.Vector.NW2,
#		chess.algebra.Vector.N2W,
#	)
	moves = Rook.moves * Bishop.moves - Rook.moves


class Star(Piece):

	width: int = 8

#	moves = chess.algebra.Vectors(
#			chess.algebra.Vector.N, chess.algebra.Vector.NE,
#			chess.algebra.Vector.E, chess.algebra.Vector.SE,
#			chess.algebra.Vector.S, chess.algebra.Vector.SW,
#			chess.algebra.Vector.W, chess.algebra.Vector.NW,
#	)
	moves = Rook.moves | Bishop.moves


class Queen(Ranged, Star, Officer):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Star):

	black: str = "\u265a"
	white: str = "\u2654"

	specs = chess.algebra.Vectors(
		chess.algebra.Vector.W2,
		chess.algebra.Vector.E2,
	)


	def __call__(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> Self:
		assert (source := self.square) is not None

		if not self.moved and move:
			if target == source + chess.algebra.Vector.E2: self.side.east_rook(target + chess.algebra.Vector.W, move, kept)
			if target == source + chess.algebra.Vector.W2: self.side.west_rook(target + chess.algebra.Vector.E, move, kept)

		return super().__call__(target, move, kept)


	@property
	def squares(self) -> chess.algebra.Squares:
		squares = super().squares

		if self.square is not None and not self.moved:
			if step := chess.rules.CastWest(self.square + chess.algebra.Vector.W2, self): squares.add(step)
			if step := chess.rules.CastEast(self.square + chess.algebra.Vector.E2, self): squares.add(step)

		return squares

	@property
	def safe(self) -> bool:
		assert self.square is not None
		return self.square not in self.side.other.targets.capts
