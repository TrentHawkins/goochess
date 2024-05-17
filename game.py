from chess import Piece, Square

class Board(list[Piece | None]):

	def __setitem__(self, square: Square, new_piece: Piece | None) -> None:
		old_piece = self[square]

		if old_piece is not None:
			old_piece.kill()

		super().__setitem__(square, new_piece)

	def __delitem__(self, square: Square) -> None:
		self[square] = None
