from __future__ import annotations


import pytest

from goochess.engine import Board, Game
from goochess.geometry import Color, Index
from goochess.material import Bishop, King, Knight, Pawn, Queen, Rook


class EngineSetup:

	empty = "8/8/8/8/8/8/8/8"
	initial = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
	asymmetric = "r1b1k2q/1p4n1/8/6N1/2B5/7P/4KQ2/R7"
	positions = (
		(empty, "-" * 64),
		(initial, "rnbqkbnr" + "pppppppp" + "-" * 32 + "PPPPPPPP" + "RNBQKBNR"),
		(asymmetric, "r-b-k--q" + "-p----n-" + "--------" + "------N-" + "--B-----" + "-------P" + "----KQ--" + "R-------"),
	)


class TestBoard(EngineSetup):

	indices = (Index.A8, Index.B8, Index.H1)
	symbol_keys = (0, Index.B8, 63)
	symbols = "-PNBRQKpnbrqk"
	replacements = (None, Knight)
	asymmetric_pieces = {
		Index.A8: (Rook, Color.BLACK),
		Index.C8: (Bishop, Color.BLACK),
		Index.E8: (King, Color.BLACK),
		Index.H8: (Queen, Color.BLACK),
		Index.B7: (Pawn, Color.BLACK),
		Index.G7: (Knight, Color.BLACK),
		Index.G5: (Knight, Color.WHITE),
		Index.C4: (Bishop, Color.WHITE),
		Index.H3: (Pawn, Color.WHITE),
		Index.E2: (King, Color.WHITE),
		Index.F2: (Queen, Color.WHITE),
		Index.A1: (Rook, Color.WHITE),
	}

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip(self, placement, flat) -> None:
		board = Board(placement)
		assert len(board) == 64
		assert repr(board) == placement
		assert tuple("-" if piece is None else repr(piece) for piece in board) == tuple(flat)

		for index, symbol in zip(Index, flat, strict = True):
			piece = board[index]
			assert board.get(index) == symbol

			if symbol == "-":
				assert piece is None

			else:
				assert piece is not None
				assert piece.index is index
				assert piece.board is board

	def test_all_piece_types_and_colors_at_asymmetric_indices(self) -> None:
		board = Board(self.asymmetric)
		assert {index for index in Index if board[index] is not None} == set(self.asymmetric_pieces)

		for index, (kind, color) in self.asymmetric_pieces.items():
			piece = board[index]
			assert piece is not None
			assert type(piece) is kind
			assert piece.color is color

	@pytest.mark.parametrize("index", indices)
	def test_assignment_rebinds_piece(self, index) -> None:
		previous = Board(self.empty)
		board = Board(self.empty)
		piece = Knight(Color.WHITE)
		previous[Index.D4] = piece
		del previous[Index.D4]
		board[index] = piece
		assert board[index] is piece
		assert piece.board is board
		assert piece.index is index
		assert len(board) == 64

	@pytest.mark.parametrize("index", indices)
	@pytest.mark.parametrize("kind", replacements)
	def test_replacement_clears_outgoing_index(self, index, kind) -> None:
		board = Board(self.empty)
		outgoing = Pawn(Color.BLACK)
		board[index] = outgoing
		incoming = None if kind is None else kind(Color.WHITE)
		board[index] = incoming
		assert board[index] is incoming
		assert outgoing.index is None
		assert outgoing.board is board
		assert len(board) == 64

		if incoming is not None:
			assert incoming.index is index
			assert incoming.board is board

	@pytest.mark.parametrize("index", indices)
	def test_deletion_clears_index_without_shrinking_board(self, index) -> None:
		board = Board(self.empty)
		piece = Rook(Color.WHITE)
		board[index] = piece
		del board[index]
		assert board[index] is None
		assert piece.index is None
		assert piece.board is board
		assert len(board) == 64

	@pytest.mark.parametrize("index", indices)
	def test_self_assignment_preserves_binding(self, index) -> None:
		board = Board(self.empty)
		piece = Bishop(Color.BLACK)
		board[index] = piece
		board[index] = piece
		assert board[index] is piece
		assert piece.index is index
		assert piece.board is board
		assert len(board) == 64

	@pytest.mark.parametrize("key", symbol_keys)
	@pytest.mark.parametrize("symbol", symbols)
	def test_symbol_assignment(self, key, symbol) -> None:
		board = Board(self.empty)
		outgoing = Pawn(Color.BLACK)
		board[key] = outgoing
		board.set(key, symbol)
		assert board.get(key) == symbol
		assert outgoing.index is None
		assert outgoing.board is board
		assert len(board) == 64
		piece = board[key]

		if symbol == "-":
			assert piece is None

		else:
			assert piece is not None
			assert piece.index is Index(key)
			assert piece.board is board

	def test_notation_tracks_mutation(self) -> None:
		board = Board(self.empty)
		board.set(Index.A8, "r")
		board[Index.H1] = King(Color.WHITE)
		assert repr(board) == "r7/8/8/8/8/8/8/7K"
		del board[Index.A8]
		assert repr(board) == "8/8/8/8/8/8/8/7K"


class TestSide(EngineSetup):

	colors = (Color.WHITE, Color.BLACK)

	def test_game_color_and_other_side(self) -> None:
		game = Game(self.empty)

		for side, other, color in ((game.white, game.black, Color.WHITE), (game.black, game.white, Color.BLACK)):
			assert side.game is game
			assert side.color is color
			assert side.other is other
			assert side.other.other is side

	@pytest.mark.parametrize("color", colors)
	def test_distinct_same_color_pieces(self, color) -> None:
		game = Game(self.empty)
		side = game.white if color is Color.WHITE else game.black
		first = Pawn(color)
		second = Pawn(color)
		side.add(first)
		side.add(second)
		assert first is not second
		assert first != second
		assert len(side) == 2
		assert set(side) == {first, second}


class TestGame(EngineSetup):

	positions = ((EngineSetup.empty, 0), (EngineSetup.initial, 16), (EngineSetup.asymmetric, 6))

	@pytest.mark.parametrize("placement, count", positions)
	def test_initial_rosters_match_active_pieces(self, placement, count) -> None:
		game = Game(placement)
		active = {piece for piece in game if piece is not None}
		assert len(game) == 64
		assert len(game.white) == len(game.black) == count
		assert set(game.white) | set(game.black) == active
		assert set(game.white).isdisjoint(game.black)

		for side, color in ((game.white, Color.WHITE), (game.black, Color.BLACK)):
			assert set(side) == {piece for piece in active if piece.color is color}
			assert all(piece.board is game and piece.index is not None and game[piece.index] is piece for piece in side)
