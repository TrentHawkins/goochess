import geometry
import material


class Board(list[material.Piece | None]):

	def __setitem__(self, square: geometry.Square, new_piece: material.Piece | None) -> None:
		old_piece = self[square]

		if old_piece is not None:
			old_piece.kill()

		super().__setitem__(square, new_piece)

	def __delitem__(self, square: geometry.Square) -> None:
		self[square] = None
