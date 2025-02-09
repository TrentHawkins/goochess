import chess.base
import chess.geometry
import chess.material


class Board(list[chess.material.Piece | None]):

	def __init__(self):
		super().__init__(None for _ in chess.geometry.Square)

	def __setitem__(self, square: chess.geometry.Square, piece: chess.material.Piece | None):
		if piece is not None:
			piece.square = square

		del self[square]

		super().__setitem__(square, piece)

	def __delitem__(self, square: chess.geometry.Square):
		piece = self[square]

		if piece is not None:
			piece.square = None

			super().__delitem__(square)


class Move:

	def __init__(self, piece: chess.material.Piece, square: chess.geometry.Square):
		self.piece = piece

		self.source = self.piece.square
		self.target = square


class Side(set[chess.material.Piece]):

	def __init__(self, *args):
		super().__init__(*args)


class Position(Board):

	def __init__(self):
		super().__init__()

		self.board = Board()

		self.board[chess.geometry.Square.A8] = chess.material.Rook  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.B8] = chess.material.Knight(chess.base.Color.BLACK)
		self.board[chess.geometry.Square.C8] = chess.material.Bishop(chess.base.Color.BLACK)
		self.board[chess.geometry.Square.D8] = chess.material.Queen (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.E8] = chess.material.King  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.F8] = chess.material.Bishop(chess.base.Color.BLACK)
		self.board[chess.geometry.Square.G8] = chess.material.Knight(chess.base.Color.WHITE)
		self.board[chess.geometry.Square.H8] = chess.material.Rook  (chess.base.Color.BLACK)

		self.board[chess.geometry.Square.A7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.B7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.C7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.D7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.E7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.F7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.G7] = chess.material.Pawn  (chess.base.Color.BLACK)
		self.board[chess.geometry.Square.H7] = chess.material.Pawn  (chess.base.Color.BLACK)

		self.board[chess.geometry.Square.A2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.B2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.C2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.D2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.E2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.F2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.G2] = chess.material.Pawn  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.H2] = chess.material.Pawn  (chess.base.Color.WHITE)

		self.board[chess.geometry.Square.A1] = chess.material.Rook  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.B1] = chess.material.Knight(chess.base.Color.WHITE)
		self.board[chess.geometry.Square.C1] = chess.material.Bishop(chess.base.Color.WHITE)
		self.board[chess.geometry.Square.D1] = chess.material.Queen (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.E1] = chess.material.King  (chess.base.Color.WHITE)
		self.board[chess.geometry.Square.F1] = chess.material.Bishop(chess.base.Color.WHITE)
		self.board[chess.geometry.Square.G1] = chess.material.Knight(chess.base.Color.WHITE)
		self.board[chess.geometry.Square.H1] = chess.material.Rook  (chess.base.Color.WHITE)

		self.black = Side(piece for piece in self.board if piece is not None and piece.color == chess.base.Color.BLACK)
		self.white = Side(piece for piece in self.board if piece is not None and piece.color == chess.base.Color.WHITE)

