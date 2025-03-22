from __future__ import annotations


import contextlib
import pathlib
import itertools
import typing

import pygame

import chess.theme
import chess.algebra
import chess.rules

if typing.TYPE_CHECKING: import chess.engine


class Piece(chess.theme.Highlightable):

	value: int = 0

	black: str = " "
	white: str = " "

	moves: set[chess.algebra.Vector] = set()


	def __init__(self, side: chess.engine.Side,
		square: chess.algebra.Square | None = None,
	):
		self.side = side
		self.square = square

		self.moved: bool = False

		super().__init__()

		try: self.surf = pygame.transform.smoothscale(pygame.image.load(self.decal).convert_alpha(), chess.theme.PIECE)
		except FileNotFoundError: self.surf = pygame.Surface(chess.theme.PIECE)

	def __repr__(self) -> str:
		return self.black if self.color else self.white


	@property
	def decal(self) -> pathlib.Path:
		return pathlib.Path("chess/graphics/piece") / self.color.name.lower() / f"{self.__class__.__name__.lower()}.png"

	@property
	def rect(self) -> pygame.Rect:
		return self.surf.get_rect(
			center = self.square.rect.center,
			bottom = self.square.rect.bottom + 20,
		) if self.square is not None else self.surf.get_rect()

	@property
	def color(self) -> chess.algebra.Color:
		return self.side.color

	@property
	def game(self) -> chess.engine.Game:
		return self.side.game

	@property
	def targets(self) -> set[chess.algebra.Square]:
		return set()

	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = self.targets.copy()

		for square in squares:
			with self.test(square):
				if not self.side.king.safe:
					squares.discard(square)

		return squares


	@contextlib.contextmanager
	def test(self, target: chess.algebra.Square):
		assert (source := self.square) is not None

		kept = self.game[target]

		self.move(target, move = False             ); yield self
		self.move(source, move = False, kept = kept)

	def move(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> typing.Self:
		assert (source := self.square) is not None

		self.moved = self.moved or move
		self.game[source], self.game[target] = kept, self.game[source]

		return self


	def squares_from(self, steps: set[chess.algebra.Vector]) -> set[chess.algebra.Square]:
		return {self.square + step for step in steps} if self.square is not None else set()

	def clicked(self, event: pygame.event.Event) -> bool:
		if (selected := self.square is not None and self.square.clicked(event)):
			self.game.selected = self

		return selected

	def draw(self, screen: pygame.Surface):
		if self.square is not None:
			screen.blit(
				self.surf,
				self.rect,
			)


class Ghost(Piece):

	...


class Officer(Piece):

	...


class Melee(Piece):

	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for move in self.moves:
				try:
					target = self.square + move

					if chess.rules.Move(self, target): targets.add(target)
					if chess.rules.Capt(self, target): targets.add(target)

				except ValueError:
					continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for move in self.moves:
				target = self.square

				while True:
					try:
						target += move

						if chess.rules.Move(self, target):
							targets.add(target)

						else:
							break

					except ValueError:
						break

				if chess.rules.Capt(self, target):
					targets.add(target)

		return targets


class Assymetric(Piece):

	@property
	def decal(self) -> pathlib.Path:
		return super().decal.with_suffix(".flipped" + super().decal.suffix) if self.color else super().decal


class Pawn(Piece):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	moves = {
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
	}

	@property
	def targets(self) -> set[chess.algebra.Square]:
		targets = super().targets

		if self.square is not None:
			for move in self.moves:
				try:
					target = self.square + move * self.color

					if chess.rules.Capt(self, target):
						targets.add(target)

				except ValueError: continue

		return targets


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = self.targets

		if self.square is not None:
			try:
				square = self.square + (move := chess.algebra.Vector.S * self.color)

				if chess.rules.Move(self, square):
					squares.add(square)
					square += move

					if chess.rules.Rush(self, square):
						squares.add(square)

			except ValueError:
				...

		return squares


class Rook(Ranged, Officer):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	moves = {
		chess.algebra.Vector.N,
		chess.algebra.Vector.E,
		chess.algebra.Vector.S,
		chess.algebra.Vector.W,
	}


class Bishop(Ranged, Assymetric, Officer):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	moves = {
		chess.algebra.Vector.NE,
		chess.algebra.Vector.SE,
		chess.algebra.Vector.SW,
		chess.algebra.Vector.NW,
	}


class Knight(Melee, Assymetric, Officer):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

	moves = {straight + diagonal for straight, diagonal in itertools.product(Rook.moves, Bishop.moves)} - Rook.moves
#	moves = {
#		chess.algebra.Vector.N2E,
#		chess.algebra.Vector.NE2,
#		chess.algebra.Vector.SE2,
#		chess.algebra.Vector.S2E,
#		chess.algebra.Vector.S2W,
#		chess.algebra.Vector.SW2,
#		chess.algebra.Vector.NW2,
#		chess.algebra.Vector.N2W,
#	}


class Star(Piece):

	moves = Rook.moves | Bishop.moves
#	moves = {
#		chess.algebra.Vectors.N, chess.algebra.Vectors.NE,
#		chess.algebra.Vectors.E, chess.algebra.Vectors.SE,
#		chess.algebra.Vectors.S, chess.algebra.Vectors.SW,
#		chess.algebra.Vectors.W, chess.algebra.Vectors.NW,
#	}


class Queen(Ranged, Officer, Star):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Star):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	@property
	def squares(self) -> set[chess.algebra.Square]:
		squares = self.targets

		if self.square is not None:
			for move, Castle in zip(
				[
					chess.algebra.Vector.W2,
					chess.algebra.Vector.E2,
				],
				[
					chess.rules.CastleLong ,
					chess.rules.CastleShort,
				],
			):
				if Castle(self.side):
					try: squares.add(self.square + move)
					except ValueError: continue

		return squares

	@property
	def safe(self) -> bool:
		assert self.square is not None
		return self.square not in self.side.other.targets
