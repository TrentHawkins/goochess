from __future__ import annotations


import pytest

from goochess.engine import Board, Game, Side
from goochess.geometry import Compass, Index
from goochess.material import Bishop, King, Knight, Pawn, Queen, Rook


class EngineSetup:

	side_names = ("white", "black")
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
	invalid_indices = (-1, -64, 64)
	roster_positions = ((EngineSetup.empty, 0), (EngineSetup.initial, 16), (EngineSetup.asymmetric, 6))
	king_positions = ((EngineSetup.initial, Index.E1, Index.E8), (EngineSetup.asymmetric, Index.E2, Index.E8))
	asymmetric_pieces = {
		Index.A8: (Rook, "black"),
		Index.C8: (Bishop, "black"),
		Index.E8: (King, "black"),
		Index.H8: (Queen, "black"),
		Index.B7: (Pawn, "black"),
		Index.G7: (Knight, "black"),
		Index.G5: (Knight, "white"),
		Index.C4: (Bishop, "white"),
		Index.H3: (Pawn, "white"),
		Index.E2: (King, "white"),
		Index.F2: (Queen, "white"),
		Index.A1: (Rook, "white"),
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
				assert piece.side is (board.white if symbol.isupper() else board.black)

	def test_all_piece_types_and_sides_at_asymmetric_indices(self) -> None:
		board = Board(self.asymmetric)
		assert {index for index in Index if board[index] is not None} == set(self.asymmetric_pieces)

		for index, (kind, side_name) in self.asymmetric_pieces.items():
			piece = board[index]
			assert piece is not None
			assert type(piece) is kind
			assert piece.side is getattr(board, side_name)

	def test_sides_are_owned_per_board(self) -> None:
		first = Board(self.empty)
		second = Board(self.empty)
		piece = Pawn(first.white)
		first[Index.A2] = piece
		assert first.white == {piece}
		assert len(second.white) == 0

		for side_name in self.side_names:
			assert getattr(first, side_name) is not getattr(second, side_name)
			assert getattr(first, side_name).board is first
			assert getattr(second, side_name).board is second

	@pytest.mark.parametrize("placement, count", roster_positions)
	def test_initial_rosters_match_active_pieces(self, placement, count) -> None:
		board = Board(placement)
		active = {piece for piece in board if piece is not None}
		assert len(board.white) == len(board.black) == count
		assert set(board.white) | set(board.black) == active
		assert set(board.white).isdisjoint(board.black)

		for side in (board.white, board.black):
			assert set(side) == {piece for piece in active if piece.side is side}
			assert all(piece.board is board and piece.index is not None and board[piece.index] is piece for piece in side)

	@pytest.mark.parametrize("placement, white, black", king_positions)
	def test_initial_king_references(self, placement, white, black) -> None:
		board = Board(placement)
		assert board.white.king is board[white]
		assert board.black.king is board[black]
		assert board.white.king in board.white
		assert board.black.king in board.black

	@pytest.mark.parametrize("side_name", EngineSetup.side_names)
	@pytest.mark.parametrize("index", indices)
	def test_assignment_places_affiliated_piece(self, side_name, index) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		piece = Knight(side)
		assert piece.index is None
		assert piece.board is board
		board[index] = piece
		assert board[index] is piece
		assert piece.side is side
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert len(board) == 64

	@pytest.mark.parametrize("outgoing_name", EngineSetup.side_names)
	@pytest.mark.parametrize("incoming_name", EngineSetup.side_names)
	@pytest.mark.parametrize("index", indices)
	def test_replacement_updates_rosters_and_clears_outgoing_index(self, outgoing_name, incoming_name, index) -> None:
		board = Board(self.empty)
		outgoing_side = getattr(board, outgoing_name)
		incoming_side = getattr(board, incoming_name)
		outgoing = Pawn(outgoing_side)
		incoming = Knight(incoming_side)
		board[index] = outgoing
		board[index] = incoming
		assert board[index] is incoming
		assert incoming_side == {incoming}
		assert len(incoming_side.other) == 0
		assert outgoing.index is None
		assert outgoing.side is outgoing_side
		assert outgoing.board is board
		assert incoming.index is index
		assert incoming.board is board
		assert len(board) == 64

	@pytest.mark.parametrize("side_name", EngineSetup.side_names)
	@pytest.mark.parametrize("delete", (False, True))
	@pytest.mark.parametrize("index", indices)
	def test_removal_updates_roster_without_shrinking_board(self, side_name, delete, index) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		piece = Rook(side)
		board[index] = piece

		if delete:
			del board[index]

		else:
			board[index] = None

		assert board[index] is None
		assert len(board.white) == 0
		assert len(board.black) == 0
		assert piece.index is None
		assert piece.side is side
		assert piece.board is board
		assert len(board) == 64

	@pytest.mark.parametrize("side_name", EngineSetup.side_names)
	@pytest.mark.parametrize("index", indices)
	def test_self_assignment_preserves_binding_and_roster(self, side_name, index) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		piece = Bishop(side)
		board[index] = piece
		board[index] = piece
		assert board[index] is piece
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert piece.board is board
		assert len(board) == 64

	@pytest.mark.parametrize("key", symbol_keys)
	@pytest.mark.parametrize("symbol", symbols)
	def test_symbol_assignment(self, key, symbol) -> None:
		board = Board(self.empty)
		outgoing = Pawn(board.black)
		board[key] = outgoing
		board.set(key, symbol)
		assert board.get(key) == symbol
		assert outgoing.index is None
		assert outgoing.side is board.black
		assert outgoing.board is board
		assert len(board) == 64
		piece = board[key]

		if symbol == "-":
			assert piece is None
			assert len(board.white) == 0
			assert len(board.black) == 0

		else:
			assert piece is not None
			assert piece.index is Index(key)
			assert piece.board is board
			assert piece.side is (board.white if symbol.isupper() else board.black)
			assert piece.side == {piece}
			assert len(piece.side.other) == 0

	def test_notation_tracks_mutation(self) -> None:
		board = Board(self.empty)
		board.set(Index.A8, "r")
		board[Index.H1] = King(board.white)
		assert repr(board) == "r7/8/8/8/8/8/8/7K"
		del board[Index.A8]
		assert repr(board) == "8/8/8/8/8/8/8/7K"

	@pytest.mark.parametrize("index", invalid_indices)
	def test_invalid_assignment_preserves_occupancy_and_rosters(self, index) -> None:
		board = Board(self.empty)
		white = Pawn(board.white)
		black = Pawn(board.black)
		incoming = Knight(board.white)
		board[Index.A8] = white
		board[Index.H1] = black
		before = tuple(board)

		with pytest.raises(ValueError):
			board[index] = incoming

		assert tuple(board) == before
		assert board.white == {white}
		assert board.black == {black}
		assert white.index is Index.A8
		assert black.index is Index.H1
		assert incoming.index is None


class TestSide(EngineSetup):

	counts = (0, 1, 2)
	contexts = (("white", True, Compass.north, "P"), ("black", False, Compass.south, "p"))

	@pytest.mark.parametrize("count", counts)
	def test_construction_without_board(self, count) -> None:
		affiliation = Side()
		pieces = tuple(Pawn(affiliation) for _ in range(count))
		side = Side(*pieces)
		assert set(side) == set(pieces)
		assert not hasattr(side, "board")

	@pytest.mark.parametrize("side_name, is_white, forward, symbol", contexts)
	def test_empty_sides_have_distinct_context(self, side_name, is_white, forward, symbol) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		pawn = Pawn(side)
		assert len(board.white) == 0
		assert len(board.black) == 0
		assert board.white == board.black
		assert board.white is not board.black
		assert side.board is board
		assert bool(side) is is_white
		assert side.other is (board.black if is_white else board.white)
		assert side.other.other is side
		assert side.forward == forward
		assert pawn.side is side
		assert repr(pawn) == symbol

	@pytest.mark.parametrize("side_name, is_white, forward, symbol", contexts)
	def test_truth_is_independent_of_roster_size(self, side_name, is_white, forward, symbol) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		pawn = Pawn(side)
		assert len(side) == 0
		assert bool(side) is is_white
		board[Index.A2] = pawn
		assert len(side) == 1
		assert bool(side) is is_white
		assert bool(side.other) is (not is_white)
		assert side.forward == forward
		assert repr(pawn) == symbol
		del board[Index.A2]
		assert len(side) == 0
		assert bool(side) is is_white

	@pytest.mark.parametrize("side_name", EngineSetup.side_names)
	def test_distinct_same_side_pieces(self, side_name) -> None:
		board = Board(self.empty)
		side = getattr(board, side_name)
		first = Pawn(side)
		second = Pawn(side)
		board[Index.A2] = first
		board[Index.H2] = second
		assert first is not second
		assert first != second
		assert len(side) == 2
		assert set(side) == {first, second}


class TestGame(EngineSetup):

	def test_inherits_board_position_behavior(self) -> None:
		game = Game(self.initial)
		assert isinstance(game, Board)
		assert repr(game) == self.initial
		assert game.white.board is game
		assert game.black.board is game
		assert len(game.white) == len(game.black) == 16
