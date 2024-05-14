from chess.square import Color

class Piece:

	def __init__(self, color: Color):
		self.square = None
		self.board = None

		self.color = color
