import chess.geometry
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self) -> None:
		super().__init__(None for _ in chess.geometry.Square)

	def __getitem__(self, square: chess.geometry.Square) -> chess.material.Piece | None:
		return super().__getitem__(int(square))

	def __setitem__(self, square: chess.geometry.Square, new_piece: chess.material.Piece | None) -> None:
		old_piece = self[square]

		if old_piece is not None:
			old_piece.discard()

		super().__setitem__(int(square), new_piece)

		if new_piece is not None:
			new_piece.add(
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
