from geometry import Board, Color, Square

class Piece:

	def __init__(self, color: Color):
		self.square = None
		self.board = None

		self.color = color
