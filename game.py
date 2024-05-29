import chess.geometry
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self) -> None:
		super().__init__(None for _ in chess.geometry.Square)

	def __getitem__(self, square: chess.geometry.Square) -> chess.material.Piece | None:
		return super().__getitem__(square)

	def __setitem__(self, square: chess.geometry.Square, piece: chess.material.Piece | None) -> None:
		_piece = self[square]

		if _piece is not None:
			_piece.discard()

		super().__setitem__(square, piece)

		if piece is not None:
			piece.add(
				board = self,
				square = square,
			)

	def __delitem__(self, square: chess.geometry.Square) -> None:
		self[square] = None


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
