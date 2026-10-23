from __future__ import annotations


import pytest

from goochess.engine import Board, Game, Side
from goochess.geometry import Index
from goochess.material import Bishop, Ghost, King, Knight, Pawn, Queen, Rook


class EngineSetup:

	colors = (False, True)
	side_names = ("white", "black")
	empty = "8/8/8/8/8/8/8/8"
	initial = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
	asymmetric = "r1b1k2q/1p4n1/8/6N1/2B5/7P/4KQ2/R7"
	positions = (
		(empty, "-" * 64),
		(initial, "rnbqkbnr" + "pppppppp" + "-" * 32 + "PPPPPPPP" + "RNBQKBNR"),
		(asymmetric, "r-b-k--q" + "-p----n-" + "--------" + "------N-" + "--B-----" + "-------P" + "----KQ--" + "R-------"),
	)
	indices = (Index.A8, Index.B8, Index.H1)
	symbol_keys = (0, Index.B8, 63)
	symbols = "-PNBRQKpnbrqk"
	invalid_indices = (-1, -64, 64)


class TestBoard(EngineSetup):

	asymmetric_pieces = {
		Index.A8: (Rook, True),
		Index.C8: (Bishop, True),
		Index.E8: (King, True),
		Index.H8: (Queen, True),
		Index.B7: (Pawn, True),
		Index.G7: (Knight, True),
		Index.G5: (Knight, False),
		Index.C4: (Bishop, False),
		Index.H3: (Pawn, False),
		Index.E2: (King, False),
		Index.F2: (Queen, False),
		Index.A1: (Rook, False),
	}
	occupants = ((None, True), (Pawn, False), (Ghost, True))

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip(self, placement, flat) -> None:
		board = Board(placement)
		assert len(board) == 64
		assert repr(board) == placement
		assert tuple("-" if piece is None else repr(piece) for piece in board) == tuple(flat)
		assert not hasattr(board, "side")

		for index, symbol in zip(Index, flat, strict = True):
			piece = board[index]
			assert board.get(index) == symbol

			if symbol == "-":
				assert piece is None

			else:
				assert piece is not None
				assert piece.index is index
				assert piece.color is symbol.islower()
				assert not hasattr(piece, "game")

	def test_piece_types_and_colors(self) -> None:
		board = Board(self.asymmetric)
		assert {index for index in Index if board[index] is not None} == set(self.asymmetric_pieces)

		for index, (kind, color) in self.asymmetric_pieces.items():
			piece = board[index]
			assert piece is not None
			assert type(piece) is kind
			assert piece.color is color

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_assignment_and_replacement(self, color) -> None:
		board = Board(self.empty)
		outgoing = Pawn(not color)
		incoming = Knight(color)
		board[Index.E4] = outgoing
		assert outgoing.index is Index.E4
		board[Index.E4] = incoming
		assert board[Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert incoming.index is Index.E4
		assert not hasattr(outgoing, "game")
		assert not hasattr(incoming, "game")
		assert len(board) == 64

	@pytest.mark.parametrize("delete", (False, True))
	def test_removal_preserves_board_size(self, delete) -> None:
		board = Board(self.empty)
		piece = Pawn(False)
		board[Index.E4] = piece

		if delete:
			del board[Index.E4]

		else:
			board[Index.E4] = None

		assert board[Index.E4] is None  # pylint: disable = invalid-sequence-index
		assert piece.index is None
		assert len(board) == 64

	@pytest.mark.parametrize("symbol", EngineSetup.symbols)
	def test_symbol_assignment(self, symbol) -> None:
		board = Board(self.empty)
		board.set(Index.E4, symbol)
		assert board.get(Index.E4) == symbol
		piece = board[Index.E4]  # pylint: disable = invalid-sequence-index

		if symbol == "-":
			assert piece is None

		else:
			assert piece is not None
			assert piece.index is Index.E4
			assert piece.color is symbol.islower()
			assert not hasattr(piece, "game")

	def test_notation_tracks_mutation(self) -> None:
		board = Board(self.empty)
		board.set(Index.A8, "r")
		board[Index.H1] = King(False)
		assert repr(board) == "r7/8/8/8/8/8/8/7K"
		del board[Index.A8]
		assert repr(board) == "8/8/8/8/8/8/8/7K"

	@pytest.mark.parametrize("index", EngineSetup.invalid_indices)
	def test_invalid_assignment_preserves_placement(self, index) -> None:
		board = Board(self.initial)
		incoming = Knight(False)
		before = tuple(board)

		with pytest.raises(ValueError):
			board[index] = incoming

		assert tuple(board) == before
		assert incoming.index is None
		assert not hasattr(incoming, "game")

	@pytest.mark.parametrize("kind, expected", occupants)
	def test_empty(self, kind, expected) -> None:
		board = Board(self.empty)

		if kind is not None:
			board[Index.E4] = kind(False)

		assert board.empty(Index.E4) is expected


class TestSide(EngineSetup):

	counts = (0, 1, 2)
	contexts = (("white", False, "P"), ("black", True, "p"))

	@pytest.mark.parametrize("count", counts)
	def test_construction_with_game(self, count) -> None:
		game = Game(self.empty)
		pieces = tuple(Pawn(False) for _ in range(count))
		side = Side(game, *pieces)
		assert set(side) == set(pieces)
		assert side.game is game

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_empty_sides_have_distinct_roles(self, side_name, color, symbol) -> None:
		game = Game(self.empty)
		side = getattr(game, side_name)
		assert len(game.white) == len(game.black) == 0
		assert game.white == game.black
		assert game.white is not game.black
		assert side.game is game
		assert bool(side) is color
		assert side.other is game.side[not color]
		assert side.other.other is side
		assert repr(Pawn(color)) == symbol

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_truth_is_independent_of_roster_size(self, side_name, color, symbol) -> None:
		game = Game(self.empty)
		side = getattr(game, side_name)
		pawn = Pawn(color)
		assert len(side) == 0
		assert bool(side) is color
		game[Index.A2] = pawn
		assert len(side) == 1
		assert bool(side) is color
		assert bool(side.other) is (not color)
		assert pawn.side is side
		assert repr(pawn) == symbol
		del game[Index.A2]
		assert len(side) == 0
		assert bool(side) is color

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_distinct_same_color_pieces(self, color) -> None:
		game = Game(self.empty)
		first = Pawn(color)
		second = Pawn(color)
		game[Index.A2] = first
		game[Index.H2] = second
		assert first is not second
		assert first != second
		assert len(game.side[color]) == 2
		assert game.side[color] == {first, second}


class TestGame(EngineSetup):

	roster_positions = ((EngineSetup.empty, 0), (EngineSetup.initial, 16), (EngineSetup.asymmetric, 6))
	king_positions = ((EngineSetup.initial, Index.E1, Index.E8), (EngineSetup.asymmetric, Index.E2, Index.E8))

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip_and_game_binding(self, placement, flat) -> None:
		game = Game(placement)
		assert isinstance(game, Board)
		assert len(game) == 64
		assert repr(game) == placement

		for index, symbol in zip(Index, flat, strict = True):
			piece = game[index]
			assert game.get(index) == symbol

			if symbol == "-":
				assert piece is None

			else:
				assert piece is not None
				assert piece.index is index
				assert piece.color is symbol.islower()
				assert piece.game is game
				assert piece.side is game.side[piece.color]

	def test_sides_are_owned_per_game(self) -> None:
		first = Game(self.empty)
		second = Game(self.empty)
		piece = Pawn(False)
		first[Index.A2] = piece
		assert first.white == {piece}
		assert len(second.white) == 0

		for color, side_name in zip(self.colors, self.side_names, strict = True):
			assert getattr(first, side_name) is first.side[color]
			assert getattr(first, side_name) is not getattr(second, side_name)
			assert first.side[color].game is first
			assert second.side[color].game is second

	@pytest.mark.parametrize("placement, count", roster_positions)
	def test_initial_rosters_match_active_pieces(self, placement, count) -> None:
		game = Game(placement)
		active = {piece for piece in game if piece is not None}
		assert len(game.white) == len(game.black) == count
		assert set(game.white) | set(game.black) == active
		assert set(game.white).isdisjoint(game.black)

		for color in self.colors:
			side = game.side[color]
			assert set(side) == {piece for piece in active if piece.color is color}
			assert all(piece.game is game and piece.index is not None and game[piece.index] is piece for piece in side)

	@pytest.mark.parametrize("placement, white, black", king_positions)
	def test_initial_king_references(self, placement, white, black) -> None:
		game = Game(placement)
		assert game.white.king is game[white]
		assert game.black.king is game[black]
		assert game.white.king in game.white
		assert game.black.king in game.black

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_assignment_binds_game_and_side(self, color, index) -> None:
		game = Game(self.empty)
		side = game.side[color]
		piece = Knight(color)
		assert piece.index is None
		assert not hasattr(piece, "game")
		game[index] = piece
		assert game[index] is piece
		assert piece.game is game
		assert piece.side is side
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert len(game) == 64

	@pytest.mark.parametrize("outgoing_color", EngineSetup.colors)
	@pytest.mark.parametrize("incoming_color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_replacement_updates_rosters_and_clears_outgoing_index(self, outgoing_color, incoming_color, index) -> None:
		game = Game(self.empty)
		outgoing_side = game.side[outgoing_color]
		incoming_side = game.side[incoming_color]
		outgoing = Pawn(outgoing_color)
		incoming = Knight(incoming_color)
		game[index] = outgoing
		game[index] = incoming
		assert game[index] is incoming
		assert incoming_side == {incoming}
		assert len(incoming_side.other) == 0
		assert outgoing.index is None
		assert outgoing.side is outgoing_side
		assert outgoing.game is game
		assert incoming.index is index
		assert incoming.game is game
		assert len(game) == 64

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("delete", (False, True))
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_removal_updates_roster_without_shrinking_board(self, color, delete, index) -> None:
		game = Game(self.empty)
		side = game.side[color]
		piece = Rook(color)
		game[index] = piece

		if delete:
			del game[index]

		else:
			game[index] = None

		assert game[index] is None
		assert len(game.white) == len(game.black) == 0
		assert piece.index is None
		assert piece.side is side
		assert piece.game is game
		assert len(game) == 64

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_self_assignment_preserves_binding_and_roster(self, color, index) -> None:
		game = Game(self.empty)
		side = game.side[color]
		piece = Bishop(color)
		game[index] = piece
		game[index] = piece
		assert game[index] is piece
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert piece.game is game
		assert len(game) == 64

	@pytest.mark.parametrize("key", EngineSetup.symbol_keys)
	@pytest.mark.parametrize("symbol", EngineSetup.symbols)
	def test_symbol_assignment_updates_rosters(self, key, symbol) -> None:
		game = Game(self.empty)
		outgoing = Pawn(True)
		game[key] = outgoing
		game.set(key, symbol)
		assert game.get(key) == symbol
		assert outgoing.index is None
		assert outgoing.side is game.black
		assert outgoing.game is game
		assert len(game) == 64
		piece = game[key]

		if symbol == "-":
			assert piece is None
			assert len(game.white) == len(game.black) == 0

		else:
			assert piece is not None
			assert piece.index is Index(key)
			assert piece.game is game
			assert piece.color is symbol.islower()
			assert piece.side == {piece}
			assert len(piece.side.other) == 0

	@pytest.mark.parametrize("index", EngineSetup.invalid_indices)
	def test_invalid_assignment_preserves_occupancy_and_rosters(self, index) -> None:
		game = Game(self.empty)
		white = Pawn(False)
		black = Pawn(True)
		incoming = Knight(False)
		game[Index.A8] = white
		game[Index.H1] = black
		before = tuple(game)

		with pytest.raises(ValueError):
			game[index] = incoming

		assert tuple(game) == before
		assert game.white == {white}
		assert game.black == {black}
		assert white.index is Index.A8
		assert black.index is Index.H1
		assert incoming.index is None
		assert not hasattr(incoming, "game")
