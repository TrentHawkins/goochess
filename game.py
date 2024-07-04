import chess.geometry
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self) -> None:
		super().__init__(None for _ in chess.geometry.Square)

	def __setitem__(self, square: chess.geometry.Square, piece: chess.material.Piece | None) -> None:
		if piece is not None:
			assert piece.board == self
			piece.square = square

		del self[square]
		super().__setitem__(square, piece)

	def __delitem__(self, square: chess.geometry.Square) -> None:
		piece = self[square]

		if piece is not None:
			piece.square = None
			super().__delitem__(square)


class Move:

	def __init__(self, piece: chess.material.Piece, square: chess.geometry.Square) -> None:
		self.piece = piece

		self.source = self.piece.square
		self.target = square


class Side(set[chess.material.Piece]):

	def __init__(self, *args):
		super().__init__(*args)


class Position(Board):

	def __init__(self):
		super().__init__()

		self.white = Side()
		self.black = Side()
