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

	steps: chess.algebra.Vectors


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
	def king(self) -> King:
		return self.side.king

	@property
	def targets(self) -> chess.algebra.Squares:
		return chess.algebra.Squares()

	@property
	def squares(self) -> chess.algebra.Squares:
		squares = self.targets.copy()

		for square in self.targets.moves | self.targets.capts:
			with self.test(square):
				if not self.king.safe:
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
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for move in self.steps.moves:
				try:
					if chess.rules.Move(self, target := self.square + (move := move * self.color)):
						targets.moves.add(target)

				except ValueError:
					continue

			for capt in self.steps.capts:
				try:
					if chess.rules.Capt(self, target := self.square + capt * self.color):
						targets.capts.add(target)

				except ValueError:
					continue

		return targets


class Ranged(Piece):

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for step in self.steps:
				target = self.square

				try:
					while chess.rules.Move(self, target := target + step):
						targets.moves.add(target)

				except ValueError:
					continue

				if chess.rules.Capt(self, target):
					targets.capts.add(target)

		return targets


class Assymetric(Piece):

	@property
	def decal(self) -> pathlib.Path:
		return super().decal.with_suffix(".flipped" + super().decal.suffix) if self.color else super().decal


class Pawn(Melee):

	value: int = 1

	black: str = "\u265f"
	white: str = "\u2659"

	steps = chess.algebra.Vectors(
		moves = {
			chess.algebra.Vector.S,
		},
		capts = {
			chess.algebra.Vector.SE,
			chess.algebra.Vector.SW,
		},
		specs = {
			chess.algebra.Vector.S2,
		},
	)

	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			for move in self.steps.moves:
				if  chess.rules.Move(self, target := self.square + (move := move * self.color)) \
				and chess.rules.Rush(self, target :=      target +  move):
					targets.moves.add(target)

		return targets


	def promote(self, to: type):
		if issubclass(to, Officer):
			self.__class__ = to  # type: ignore


class Rook(Ranged, Officer):

	value: int = 5

	black: str = "\u265c"
	white: str = "\u2656"

	steps = chess.algebra.Vectors(
		moves = {
			chess.algebra.Vector.N,
			chess.algebra.Vector.E,
			chess.algebra.Vector.S,
			chess.algebra.Vector.W,
		}
	)


class Bishop(Ranged, Assymetric, Officer):

	value: int = 3

	black: str = "\u265d"
	white: str = "\u2657"

	steps = chess.algebra.Vectors(
		moves = {
			chess.algebra.Vector.NE,
			chess.algebra.Vector.SE,
			chess.algebra.Vector.SW,
			chess.algebra.Vector.NW,
		}
	)


class Knight(Melee, Assymetric, Officer):

	value: int = 3

	black: str = "\u265e"
	white: str = "\u2658"

#	steps = chess.algebra.Vectors(
#		moves = {
#			chess.algebra.Vector.N2E,
#			chess.algebra.Vector.NE2,
#			chess.algebra.Vector.SE2,
#			chess.algebra.Vector.S2E,
#			chess.algebra.Vector.S2W,
#			chess.algebra.Vector.SW2,
#			chess.algebra.Vector.NW2,
#			chess.algebra.Vector.N2W,
#		}
#	)
	steps = Rook.steps * Bishop.steps - Rook.steps


class Star(Piece):

#	steps = chess.algebra.Vectors(
#		moves = {
#			chess.algebra.Vector.N, chess.algebra.Vector.NE,
#			chess.algebra.Vector.E, chess.algebra.Vector.SE,
#			chess.algebra.Vector.S, chess.algebra.Vector.SW,
#			chess.algebra.Vector.W, chess.algebra.Vector.NW,
#		}
#	)
	steps = Rook.steps | Bishop.steps


class Queen(Ranged, Officer, Star):

	value: int = 9

	black: str = "\u265b"
	white: str = "\u2655"


class King(Melee, Star):

	value: int = 0

	black: str = "\u265a"
	white: str = "\u2654"


	def move(self, target: chess.algebra.Square,
		move: bool = True,
		kept: Piece | None = None,
	) -> typing.Self:
		assert (source := self.square) is not None

		try:
			if target == source + chess.algebra.Vector.E2: self.side.east_rook.move(target + chess.algebra.Vector.W, move, kept)
			if target == source + chess.algebra.Vector.W2: self.side.west_rook.move(target + chess.algebra.Vector.E, move, kept)

		except:
			...

		super().move(target, move, kept)

		return self


	@property
	def targets(self) -> chess.algebra.Squares:
		targets = super().targets

		if self.square is not None:
			try:
				if chess.rules.CastleWest(self.side): targets.specs.add(self.square + chess.algebra.Vector.W2)
				if chess.rules.CastleEast(self.side): targets.specs.add(self.square + chess.algebra.Vector.E2)

			except:
				...

		return targets

	@property
	def safe(self) -> bool:
		assert self.square is not None
		return self.square not in self.side.other.targets
