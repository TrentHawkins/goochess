from __future__ import annotations


from datetime import datetime
import os
import typing

import chess.geometry
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self):
		super().__init__(None for _ in chess.geometry.Square)

	def __repr__(self) -> str:
		representation  = ""
		representation += "▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖" + os.linesep
		representation += "▐▌  A B C D E F G H  ▐▌" + os.linesep

		for index, piece in enumerate(self):
			square = chess.geometry.Square(index)
			square_representation = str(square)

			if piece is not None:
				square_representation = square_representation.replace(" ", str(piece))

			if square.file == chess.geometry.File.A_:
				representation += "▐▌" + repr(square.rank)

			representation += square_representation + "\x1b[D"

			if square.file == chess.geometry.File.H_:
				representation += "\x1b[C" + repr(square.rank) + "▐▌" + os.linesep

		representation += "▐▌  A B C D E F G H  ▐▌" + os.linesep
		representation += "▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘"

		return representation

	def __setitem__(self, key: chess.geometry.Square | slice, value: chess.material.Piece | None | typing.Iterable[chess.material.Piece | None]):
		if isinstance(key, chess.geometry.Square):	key = slice(key, key + 1, +1)
		if isinstance(value, chess.material.Piece | None): value = [value]

		for integer, piece in zip(range(*key.indices(len(self))), value):
			self.update(chess.geometry.Square(integer), piece)

		super().__setitem__(key, value)

	def __delitem__(self, key: chess.geometry.Square | slice):
		if isinstance(key, chess.geometry.Square):	key = slice(key, key + 1, +1)

		self[key] = [None] * len(range(*key.indices(len(self))))


	def update(self, square: chess.geometry.Square,
		piece: chess.material.Piece | None = None,
	):
		other = self[square]

		if piece is not None: piece.square = square
		if other is not None: other.square = None


class Side(list[chess.material.Piece]):

	def __init__(self, game: Game, color: chess.geometry.Color):
		self.game = game
		self.color = color

		super().__init__(
			[
				chess.material.Rook  (game, self),
				chess.material.Knight(game, self),
				chess.material.Bishop(game, self),
				chess.material.Queen (game, self) if color else
				chess.material.King  (game, self),
				chess.material.King  (game, self) if color else
				chess.material.Queen (game, self),
				chess.material.Bishop(game, self),
				chess.material.Knight(game, self),
				chess.material.Rook  (game, self),

				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
				chess.material.Pawn  (game, self),
			]
		)

		self.ghost = chess.material.Piece(game, self)
		self.king = self[
			chess.geometry.Square.E8 if color else
			chess.geometry.Square.D8
		]


	@property
	def material(self) -> int:
		return sum(piece.value for piece in self if piece.square is not None)


class Game(Board):

	def __init__(self):
		super().__init__()

		self.black = Side(self, chess.geometry.Color.BLACK)
		self.white = Side(self, chess.geometry.Color.WHITE)

		self[+chess.geometry.Square.A8:+chess.geometry.Square.A6:chess.geometry.Difference.E] = self.black
		self[-chess.geometry.Square.A8:-chess.geometry.Square.A6:chess.geometry.Difference.W] = self.white

	def __hash__(self) -> int:
		return hash(datetime.now().timestamp())
