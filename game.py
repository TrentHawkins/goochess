import geometry
import material


class Board(list[material.Piece | None]):

	def __init__(self):
		super().__init__(None for _ in geometry.Square)

	def __setitem__(self, square: geometry.Square, new_piece: material.Piece | None) -> None:
		old_piece = self[square]

		if old_piece is not None:
			old_piece.discard()

		super().__setitem__(square, new_piece)

		if new_piece is not None:
			new_piece.add(
				board = self,
				square = square,
			)

	def __delitem__(self, square: geometry.Square) -> None:
		self[square] = None
