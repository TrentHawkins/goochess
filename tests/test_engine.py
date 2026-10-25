from __future__ import annotations


import pytest

from goochess.algebra import Capt
from goochess.engine import Board, Position, Side
from goochess.geometry import Index
from goochess.material import Bishop, King, Knight, Pawn, Queen, Rook
from goochess.mathematics import indices


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
				assert not hasattr(piece, "position")

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
		assert not hasattr(outgoing, "position")
		assert not hasattr(incoming, "position")
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
			assert not hasattr(piece, "position")

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
		assert not hasattr(incoming, "position")

	def test_binding_wraps_placement(self) -> None:
		board = Board(self.empty)
		outgoing = Pawn(False)
		incoming = Knight(True)
		board[Index.E4] = outgoing

		with board.binding(Index.E4, incoming) as bound:
			assert bound is None
			assert board[Index.E4] is outgoing  # pylint: disable = invalid-sequence-index
			assert outgoing.index is None
			assert incoming.index is None
			list.__setitem__(board, Index.E4, incoming)

		assert board[Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert incoming.index is Index.E4
		assert not hasattr(incoming, "position")


class TestSide(EngineSetup):

	counts = (0, 1, 2)
	contexts = (("white", False, "P"), ("black", True, "p"))
	target_cases = (
		(False, Index.B1, Index.E2, Index.H8, (Index.A3, Index.C3, Index.D2, Index.E3, Index.E4)),
		(True, Index.B8, Index.E7, Index.H1, (Index.A6, Index.C6, Index.D7, Index.E6, Index.E5)),
	)

	@pytest.mark.parametrize("count", counts)
	def test_construction_with_position(self, count) -> None:
		position = Position(self.empty)
		pieces = tuple(Pawn(False) for _ in range(count))
		side = Side(position, *pieces)
		assert set(side) == set(pieces)
		assert side.position is position

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_empty_sides_have_distinct_roles(self, side_name, color, symbol) -> None:
		position = Position(self.empty)
		side = getattr(position, side_name)
		assert len(position.white) == len(position.black) == 0
		assert position.white == position.black
		assert position.white is not position.black
		assert side.position is position
		assert bool(side) is color
		assert side.other is position.side[not color]
		assert side.other.other is side
		assert repr(Pawn(color)) == symbol

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_truth_is_independent_of_roster_size(self, side_name, color, symbol) -> None:
		position = Position(self.empty)
		side = getattr(position, side_name)
		pawn = Pawn(color)
		assert len(side) == 0
		assert bool(side) is color
		position[Index.A2] = pawn
		assert len(side) == 1
		assert bool(side) is color
		assert bool(side.other) is (not color)
		assert pawn.side is side
		assert repr(pawn) == symbol
		del position[Index.A2]
		assert len(side) == 0
		assert bool(side) is color

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_distinct_same_color_pieces(self, color) -> None:
		position = Position(self.empty)
		first = Pawn(color)
		second = Pawn(color)
		position[Index.A2] = first
		position[Index.H2] = second
		assert first is not second
		assert first != second
		assert len(position.side[color]) == 2
		assert position.side[color] == {first, second}

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_empty_roster_has_no_targets(self, color) -> None:
		side = Position(self.empty).side[color]
		assert side.targets == indices()
		assert isinstance(side.targets, indices)

	@pytest.mark.parametrize("color, knight_square, pawn_square, opponent_square, expected", target_cases)
	def test_targets_combine_own_pieces(self, color, knight_square, pawn_square, opponent_square, expected) -> None:
		position = Position(self.empty)
		position[knight_square] = Knight(color)
		position[pawn_square] = Pawn(color)
		position[opponent_square] = Knight(not color)
		targets = position.side[color].targets
		assert isinstance(targets, indices)
		assert targets == indices(*expected)

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_targets_restore_after_capture_simulation(self, color) -> None:
		position = Position(self.empty)
		piece = Knight(color)
		other = Pawn(not color)
		position[Index.C3] = piece
		position[Index.D5] = other
		side = piece.side
		before = side.targets, side.other.targets

		with Capt(Index.D5, piece):
			assert side == {piece}
			assert len(side.other) == 0
			assert side.other.targets == indices()
			assert side.targets != before[0]

		assert side == {piece}
		assert side.other == {other}
		assert (side.targets, side.other.targets) == before


class TestPosition(EngineSetup):

	roster_positions = ((EngineSetup.empty, 0), (EngineSetup.initial, 16), (EngineSetup.asymmetric, 6))
	king_positions = ((EngineSetup.initial, Index.E1, Index.E8), (EngineSetup.asymmetric, Index.E2, Index.E8))

	def test_binding_wraps_placement_and_rosters(self) -> None:
		position = Position(self.empty)
		outgoing = Pawn(False)
		incoming = Knight(True)
		position[Index.E4] = outgoing

		with position.binding(Index.E4, incoming) as bound:
			assert bound is None
			assert position[Index.E4] is outgoing  # pylint: disable = invalid-sequence-index
			assert outgoing.index is None
			assert outgoing not in position.white
			assert incoming.index is None
			assert not hasattr(incoming, "position")
			list.__setitem__(position, Index.E4, incoming)

		assert position[Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert len(position.white) == 0
		assert incoming.index is Index.E4
		assert incoming.position is position
		assert incoming.side is position.black
		assert position.black == {incoming}

	def test_binding_propagates_body_exception_without_attaching_incoming(self) -> None:
		position = Position(self.empty)
		incoming = Knight(True)

		with pytest.raises(RuntimeError, match = "placement failed"):
			with position.binding(Index.E4, incoming) as bound:
				assert bound is None

				raise RuntimeError("placement failed")

		assert position[Index.E4] is None  # pylint: disable = invalid-sequence-index
		assert incoming.index is None
		assert not hasattr(incoming, "position")
		assert len(position.white) == len(position.black) == 0

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip_and_position_binding(self, placement, flat) -> None:
		position = Position(placement)
		assert isinstance(position, Board)
		assert len(position) == 64
		assert repr(position) == placement

		for index, symbol in zip(Index, flat, strict = True):
			piece = position[index]
			assert position.get(index) == symbol

			if symbol == "-":
				assert piece is None

			else:
				assert piece is not None
				assert piece.index is index
				assert piece.color is symbol.islower()
				assert piece.position is position
				assert piece.side is position.side[piece.color]

	def test_sides_are_owned_per_position(self) -> None:
		first = Position(self.empty)
		second = Position(self.empty)
		piece = Pawn(False)
		first[Index.A2] = piece
		assert first.white == {piece}
		assert len(second.white) == 0

		for color, side_name in zip(self.colors, self.side_names, strict = True):
			assert getattr(first, side_name) is first.side[color]
			assert getattr(first, side_name) is not getattr(second, side_name)
			assert first.side[color].position is first
			assert second.side[color].position is second

	@pytest.mark.parametrize("placement, count", roster_positions)
	def test_initial_rosters_match_active_pieces(self, placement, count) -> None:
		position = Position(placement)
		active = {piece for piece in position if piece is not None}
		assert len(position.white) == len(position.black) == count
		assert set(position.white) | set(position.black) == active
		assert set(position.white).isdisjoint(position.black)

		for color in self.colors:
			side = position.side[color]
			assert set(side) == {piece for piece in active if piece.color is color}
			assert all(piece.position is position and piece.index is not None and position[piece.index] is piece for piece in side)

	@pytest.mark.parametrize("placement, white, black", king_positions)
	def test_initial_king_references(self, placement, white, black) -> None:
		position = Position(placement)
		assert position.white.king is position[white]
		assert position.black.king is position[black]
		assert position.white.king in position.white
		assert position.black.king in position.black

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_assignment_binds_position_and_side(self, color, index) -> None:
		position = Position(self.empty)
		side = position.side[color]
		piece = Knight(color)
		assert piece.index is None
		assert not hasattr(piece, "position")
		position[index] = piece
		assert position[index] is piece
		assert piece.position is position
		assert piece.side is side
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert len(position) == 64

	@pytest.mark.parametrize("outgoing_color", EngineSetup.colors)
	@pytest.mark.parametrize("incoming_color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_replacement_updates_rosters_and_clears_outgoing_index(self, outgoing_color, incoming_color, index) -> None:
		position = Position(self.empty)
		outgoing_side = position.side[outgoing_color]
		incoming_side = position.side[incoming_color]
		outgoing = Pawn(outgoing_color)
		incoming = Knight(incoming_color)
		position[index] = outgoing
		position[index] = incoming
		assert position[index] is incoming
		assert incoming_side == {incoming}
		assert len(incoming_side.other) == 0
		assert outgoing.index is None
		assert outgoing.side is outgoing_side
		assert outgoing.position is position
		assert incoming.index is index
		assert incoming.position is position
		assert len(position) == 64

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("delete", (False, True))
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_removal_updates_roster_without_shrinking_board(self, color, delete, index) -> None:
		position = Position(self.empty)
		side = position.side[color]
		piece = Rook(color)
		position[index] = piece

		if delete:
			del position[index]

		else:
			position[index] = None

		assert position[index] is None
		assert len(position.white) == len(position.black) == 0
		assert piece.index is None
		assert piece.side is side
		assert piece.position is position
		assert len(position) == 64

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_self_assignment_preserves_binding_and_roster(self, color, index) -> None:
		position = Position(self.empty)
		side = position.side[color]
		piece = Bishop(color)
		position[index] = piece
		position[index] = piece
		assert position[index] is piece
		assert side == {piece}
		assert len(side.other) == 0
		assert piece.index is index
		assert piece.position is position
		assert len(position) == 64

	@pytest.mark.parametrize("key", EngineSetup.symbol_keys)
	@pytest.mark.parametrize("symbol", EngineSetup.symbols)
	def test_symbol_assignment_updates_rosters(self, key, symbol) -> None:
		position = Position(self.empty)
		outgoing = Pawn(True)
		position[key] = outgoing
		position.set(key, symbol)
		assert position.get(key) == symbol
		assert outgoing.index is None
		assert outgoing.side is position.black
		assert outgoing.position is position
		assert len(position) == 64
		piece = position[key]

		if symbol == "-":
			assert piece is None
			assert len(position.white) == len(position.black) == 0

		else:
			assert piece is not None
			assert piece.index is Index(key)
			assert piece.position is position
			assert piece.color is symbol.islower()
			assert piece.side == {piece}
			assert len(piece.side.other) == 0

	@pytest.mark.parametrize("index", EngineSetup.invalid_indices)
	def test_invalid_assignment_preserves_occupancy_and_rosters(self, index) -> None:
		position = Position(self.empty)
		white = Pawn(False)
		black = Pawn(True)
		incoming = Knight(False)
		position[Index.A8] = white
		position[Index.H1] = black
		before = tuple(position)

		with pytest.raises(ValueError):
			position[index] = incoming

		assert tuple(position) == before
		assert position.white == {white}
		assert position.black == {black}
		assert white.index is Index.A8
		assert black.index is Index.H1
		assert incoming.index is None
		assert not hasattr(incoming, "position")
