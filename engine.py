from __future__ import annotations


from datetime import datetime
import os
import typing

import chess.algebra
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self):
		super().__init__(None for _ in chess.algebra.Square)

	def __repr__(self) -> str:
		representation  = ""
		representation += "▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖" + os.linesep
		representation += "▐▌  A B C D E F G H  ▐▌" + os.linesep

		for index, piece in enumerate(self):
			square = chess.algebra.Square(index)
			square_representation = str(square)

			if piece is not None:
				square_representation = square_representation.replace(" ", str(piece))

			if square.file == chess.algebra.File.A_:
				representation += "▐▌" + repr(square.rank)

			representation += square_representation + "\x1b[D"

			if square.file == chess.algebra.File.H_:
				representation += "\x1b[C" + repr(square.rank) + "▐▌" + os.linesep

		representation += "▐▌  A B C D E F G H  ▐▌" + os.linesep
		representation += "▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘"

		return representation

	def __setitem__(self, key: chess.algebra.Square | slice, value: chess.material.Piece | None | typing.Iterable[chess.material.Piece | None]):
		if isinstance(key, chess.algebra.Square): key = slice(key, key + 1, +1)
		if isinstance(value, chess.material.Piece | None): value = [value]

		for integer, piece in zip(range(*key.indices(len(self))), value):
			self.update(chess.algebra.Square(integer), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.algebra.Square | slice):
		if isinstance(key, chess.algebra.Square): key = slice(key, key + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	def update(self, square: chess.algebra.Square,
		piece: chess.material.Piece | None = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None


class Side(list[chess.material.Piece]):

	def __init__(self, game: Game, color: chess.algebra.Color):
		self.game = game
		self.color = color

		super().__init__(
			[
				chess.material.Rook  (self.game, self),
				chess.material.Knight(self.game, self),
				chess.material.Bishop(self.game, self),
				chess.material.Queen (self.game, self) if self.color else
				chess.material.King  (self.game, self),
				chess.material.King  (self.game, self) if self.color else
				chess.material.Queen (self.game, self),
				chess.material.Bishop(self.game, self),
				chess.material.Knight(self.game, self),
				chess.material.Rook  (self.game, self),

				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
				chess.material.Pawn  (self.game, self),
			]
		)

		self.ghost = chess.material.Piece(self.game, self)


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)

	@property
	def squares(self) -> set[chess.algebra.Square]:
		return NotImplemented

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

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())
