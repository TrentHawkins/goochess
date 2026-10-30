from __future__ import annotations


import pytest

from goochess import algebra
from goochess import engine
from goochess import geometry
from goochess import material
from goochess import structs


class EngineSetup:

	colors = (False, True)
	side_names = ("white", "black")
	empty = "8/8/8/8/8/8/8/8"
	empty_fen = empty + " w - - 0 1"
	initial = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
	castling = "r3k2r/8/8/8/8/8/8/R3K2R"
	asymmetric = "r1b1k2q/1p4n1/8/6N1/2B5/7P/4KQ2/R7"
	positions = (
		(empty, "-" * 64),
		(initial, "rnbqkbnr" + "pppppppp" + "-" * 32 + "PPPPPPPP" + "RNBQKBNR"),
		(asymmetric, "r-b-k--q" + "-p----n-" + "--------" + "------N-" + "--B-----" + "-------P" + "----KQ--" + "R-------"),
	)
	indices = (geometry.Index.A8, geometry.Index.B8, geometry.Index.H1)
	symbol_keys = (0, geometry.Index.B8, 63)
	symbols = "-PNBRQKpnbrqk"
	invalid_indices = (-1, -64, 64)


class TestBoard(EngineSetup):

	asymmetric_pieces = {
		geometry.Index.A8: (material.Rook, True),
		geometry.Index.C8: (material.Bishop, True),
		geometry.Index.E8: (material.King, True),
		geometry.Index.H8: (material.Queen, True),
		geometry.Index.B7: (material.Pawn, True),
		geometry.Index.G7: (material.Knight, True),
		geometry.Index.G5: (material.Knight, False),
		geometry.Index.C4: (material.Bishop, False),
		geometry.Index.H3: (material.Pawn, False),
		geometry.Index.E2: (material.King, False),
		geometry.Index.F2: (material.Queen, False),
		geometry.Index.A1: (material.Rook, False),
	}

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip(self, placement, flat) -> None:
		board = engine.Board(placement)
		assert len(board) == 64
		assert repr(board) == placement
		assert tuple("-" if piece is None else repr(piece) for piece in board) == tuple(flat)
		assert not hasattr(board, "side")

		for index, symbol in zip(geometry.Index, flat, strict = True):
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
		board = engine.Board(self.asymmetric)
		assert {index for index in geometry.Index if board[index] is not None} == set(self.asymmetric_pieces)

		for index, (kind, color) in self.asymmetric_pieces.items():
			piece = board[index]
			assert piece is not None
			assert type(piece) is kind
			assert piece.color is color

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_assignment_and_replacement(self, color) -> None:
		board = engine.Board(self.empty)
		outgoing = material.Pawn(not color)
		incoming = material.Knight(color)
		board[geometry.Index.E4] = outgoing
		assert outgoing.index is geometry.Index.E4
		board[geometry.Index.E4] = incoming
		assert board[geometry.Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert incoming.index is geometry.Index.E4
		assert not hasattr(outgoing, "position")
		assert not hasattr(incoming, "position")
		assert len(board) == 64

	@pytest.mark.parametrize("delete", (False, True))
	def test_removal_preserves_board_size(self, delete) -> None:
		board = engine.Board(self.empty)
		piece = material.Pawn(False)
		board[geometry.Index.E4] = piece

		if delete:
			del board[geometry.Index.E4]

		else:
			board[geometry.Index.E4] = None

		assert board[geometry.Index.E4] is None  # pylint: disable = invalid-sequence-index
		assert piece.index is None
		assert len(board) == 64

	@pytest.mark.parametrize("symbol", EngineSetup.symbols)
	def test_symbol_assignment(self, symbol) -> None:
		board = engine.Board(self.empty)
		board.set(geometry.Index.E4, symbol)
		assert board.get(geometry.Index.E4) == symbol
		piece = board[geometry.Index.E4]  # pylint: disable = invalid-sequence-index

		if symbol == "-":
			assert piece is None

		else:
			assert piece is not None
			assert piece.index is geometry.Index.E4
			assert piece.color is symbol.islower()
			assert not hasattr(piece, "position")

	def test_notation_tracks_mutation(self) -> None:
		board = engine.Board(self.empty)
		board.set(geometry.Index.A8, "r")
		board[geometry.Index.H1] = material.King(False)
		assert repr(board) == "r7/8/8/8/8/8/8/7K"
		del board[geometry.Index.A8]
		assert repr(board) == "8/8/8/8/8/8/8/7K"

	@pytest.mark.parametrize("index", EngineSetup.invalid_indices)
	def test_invalid_assignment_preserves_placement(self, index) -> None:
		board = engine.Board(self.initial)
		incoming = material.Knight(False)
		before = tuple(board)

		with pytest.raises(ValueError):
			board[index] = incoming

		assert tuple(board) == before
		assert incoming.index is None
		assert not hasattr(incoming, "position")

	def test_binding_wraps_placement(self) -> None:
		board = engine.Board(self.empty)
		outgoing = material.Pawn(False)
		incoming = material.Knight(True)
		board[geometry.Index.E4] = outgoing

		with board.binding(geometry.Index.E4, incoming) as bound:
			assert bound is None
			assert board[geometry.Index.E4] is outgoing  # pylint: disable = invalid-sequence-index
			assert outgoing.index is None
			assert incoming.index is None
			list.__setitem__(board, geometry.Index.E4, incoming)

		assert board[geometry.Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert incoming.index is geometry.Index.E4
		assert not hasattr(incoming, "position")


class TestSide(EngineSetup):

	counts = (0, 1, 2)
	contexts = (("white", False, "P"), ("black", True, "p"))
	target_cases = (
		(False, geometry.Index.B1, geometry.Index.E2, geometry.Index.H8, (geometry.Index.A3, geometry.Index.C3, geometry.Index.D2, geometry.Index.E3, geometry.Index.E4)),
		(True, geometry.Index.B8, geometry.Index.E7, geometry.Index.H1, (geometry.Index.A6, geometry.Index.C6, geometry.Index.D7, geometry.Index.E6, geometry.Index.E5)),
	)

	@pytest.mark.parametrize("count", counts)
	def test_construction_with_position(self, count) -> None:
		position = engine.Position(self.empty_fen)
		pieces = tuple(material.Pawn(False) for _ in range(count))
		side = engine.Side(position, *pieces)
		assert set(side) == set(pieces)
		assert side.position is position

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_empty_sides_have_distinct_roles(self, side_name, color, symbol) -> None:
		position = engine.Position(self.empty_fen)
		side = getattr(position, side_name)
		assert len(position.white) == len(position.black) == 0
		assert position.white == position.black
		assert position.white is not position.black
		assert side.position is position
		assert bool(side) is color
		assert side.other is position.side[not color]
		assert side.other.other is side
		assert repr(material.Pawn(color)) == symbol

	@pytest.mark.parametrize("side_name, color, symbol", contexts)
	def test_truth_is_independent_of_roster_size(self, side_name, color, symbol) -> None:
		position = engine.Position(self.empty_fen)
		side = getattr(position, side_name)
		pawn = material.Pawn(color)
		assert len(side) == 0
		assert bool(side) is color
		position[geometry.Index.A2] = pawn
		assert len(side) == 1
		assert bool(side) is color
		assert bool(side.other) is (not color)
		assert pawn.side is side
		assert repr(pawn) == symbol
		del position[geometry.Index.A2]
		assert len(side) == 0
		assert bool(side) is color

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_distinct_same_color_pieces(self, color) -> None:
		position = engine.Position(self.empty_fen)
		first = material.Pawn(color)
		second = material.Pawn(color)
		position[geometry.Index.A2] = first
		position[geometry.Index.H2] = second
		assert first is not second
		assert first != second
		assert len(position.side[color]) == 2
		assert position.side[color] == {first, second}

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_empty_roster_has_no_targets(self, color) -> None:
		side = engine.Position(self.empty_fen).side[color]
		assert side.targets == structs.collection()
		assert isinstance(side.targets, structs.collection)

	@pytest.mark.parametrize("color, knight_square, pawn_square, opponent_square, expected", target_cases)
	def test_targets_combine_own_pieces(self, color, knight_square, pawn_square, opponent_square, expected) -> None:
		position = engine.Position(self.empty_fen)
		position[knight_square] = material.Knight(color)
		position[pawn_square] = material.Pawn(color)
		position[opponent_square] = material.Knight(not color)
		targets = position.side[color].targets
		assert isinstance(targets, structs.collection)
		assert all(isinstance(step, algebra.Move) for step in targets)
		assert targets == structs.collection(*expected)

	@pytest.mark.parametrize("color", EngineSetup.colors)
	def test_targets_restore_after_capture_simulation(self, color) -> None:
		position = engine.Position(self.empty_fen)
		piece = material.Knight(color)
		other = material.Pawn(not color)
		position[geometry.Index.C3] = piece
		position[geometry.Index.D5] = other
		side = piece.side
		before = side.targets, side.other.targets

		with algebra.Capt(geometry.Index.D5, piece).simulated:
			assert side == {piece}
			assert len(side.other) == 0
			assert side.other.targets == structs.collection()
			assert side.targets != before[0]

		assert side == {piece}
		assert side.other == {other}
		assert (side.targets, side.other.targets) == before


class TestPosition(EngineSetup):

	roster_positions = ((EngineSetup.empty, 0), (EngineSetup.initial, 16), (EngineSetup.asymmetric, 6))
	king_positions = ((EngineSetup.initial, geometry.Index.E1, geometry.Index.E8), (EngineSetup.asymmetric, geometry.Index.E2, geometry.Index.E8))

	castling_fields = ("-", "K", "Q", "k", "q", "KQ", "Kk", "Kq", "Qk", "Qq", "kq", "KQk", "KQq", "Kkq", "Qkq", "KQkq")
	partners = (
		("K", False, material.King.ᐅ, geometry.Index.H1),
		("Q", False, material.King.ᐊ, geometry.Index.A1),
		("k", True, material.King.ᐅ, geometry.Index.H8),
		("q", True, material.King.ᐊ, geometry.Index.A8),
	)
	departures = (
		(geometry.Index.E1, geometry.Index.E2),
		(geometry.Index.E8, geometry.Index.E7),
		(geometry.Index.A1, geometry.Index.A2),
		(geometry.Index.H1, geometry.Index.H2),
		(geometry.Index.A8, geometry.Index.A7),
		(geometry.Index.H8, geometry.Index.H7),
	)
	partner_faults = ("missing_king", "missing_rook", "wrong_type", "wrong_color")

	def test_full_fen_extracts_placement_and_castling_field(self) -> None:
		position = engine.Position(f"{self.castling} b Kq - 17 42")
		assert repr(position) == self.castling
		assert position.white.king is not None and position.black.king is not None
		assert position.white.king.rooks == {material.King.ᐅ: position[geometry.Index.H1]}  # pylint: disable = invalid-sequence-index
		assert position.black.king.rooks == {material.King.ᐊ: position[geometry.Index.A8]}  # pylint: disable = invalid-sequence-index

	def test_placement_alone_is_not_full_fen(self) -> None:
		with pytest.raises(ValueError):
			engine.Position(self.empty)

	@pytest.mark.parametrize("placement", (EngineSetup.empty, EngineSetup.initial, EngineSetup.castling))
	def test_empty_castling_field_does_not_bind_partners(self, placement) -> None:
		position = engine.Position(f"{placement} w - - 0 1")

		for side in position.side:
			assert not hasattr(side, "castle_short") and not hasattr(side, "castle_long")

			if side.king is not None:
				assert side.king.rooks == {}

	@pytest.mark.parametrize("castling", castling_fields)
	def test_castling_field_binds_declared_rooks(self, castling) -> None:
		position = engine.Position(f"{self.castling} w {castling} - 0 1")

		for color in self.colors:
			king = position.side[color].king
			assert king is not None
			expected = {offset: position[square] for token, owner, offset, square in self.partners if token in castling and owner is color}
			assert king.rooks == expected

			for offset, rook in expected.items():
				assert king.rooks[offset] is rook
				assert isinstance(rook, material.Rook)
				assert rook.color is color

	def test_castling_partners_are_owned_per_king_and_position(self) -> None:
		first = engine.Position(f"{self.castling} w K - 0 1")
		second = engine.Position(f"{self.castling} w Qkq - 0 1")
		white = first.white.king
		black = first.black.king
		assert white is not None and black is not None
		assert white.rooks == {material.King.ᐅ: first[geometry.Index.H1]}  # pylint: disable = invalid-sequence-index
		assert black.rooks == {}
		assert second.white.king is not None and second.black.king is not None
		assert set(second.white.king.rooks) == {material.King.ᐊ}
		assert set(second.black.king.rooks) == {material.King.ᐊ, material.King.ᐅ}
		assert len({id(king.rooks) for king in (white, black, second.white.king, second.black.king)}) == 4

	@pytest.mark.parametrize("token, color, offset, square", partners)
	@pytest.mark.parametrize("fault", partner_faults)
	def test_declared_castling_requires_matching_participants(self, token, color, offset, square, fault) -> None:
		board = engine.Board(self.castling)

		if fault == "missing_king":
			del board[geometry.Index.E8 if color else geometry.Index.E1]

		elif fault == "missing_rook":
			del board[square]

		elif fault == "wrong_type":
			board[square] = material.Knight(color)

		else:
			board[square] = material.Rook(not color)

		with pytest.raises(AssertionError):
			engine.Position(f"{board!r} w {token} - 0 1")

	def test_castling_field_rejects_unknown_token(self) -> None:
		with pytest.raises(AssertionError):
			engine.Position(f"{self.castling} w X - 0 1")

	@pytest.mark.parametrize("source, target", departures)
	def test_piece_departures_preserve_castling_partners(self, source, target) -> None:
		position = engine.Position(f"{self.castling} w KQkq - 0 1")
		piece = position[source]
		assert piece is not None
		partners = tuple((side.king, dict(side.king.rooks)) for side in position.side if side.king is not None)

		with algebra.Move(target, piece).simulated:
			assert piece.moved
			assert all(king.rooks == rooks for king, rooks in partners)

		assert not piece.moved
		algebra.Move(target, piece).apply()
		algebra.Move(source, piece).apply()
		assert piece.moved
		assert all(king.rooks == rooks for king, rooks in partners)

	@pytest.mark.parametrize("token, color, offset, square", partners)
	def test_capture_preserves_original_castling_partner(self, token, color, offset, square) -> None:
		position = engine.Position(f"{self.castling} w {token} - 0 1")
		king = position.side[color].king
		assert king is not None
		rook = king.rooks[offset]
		attacker = material.Rook(not color)
		direction = geometry.Compass.south if color else geometry.Compass.north
		position[square + direction] = attacker

		with algebra.Capt(square, attacker).simulated:
			assert rook.index is None
			assert rook not in king.side
			assert king.rooks[offset] is rook

		assert position[square] is rook
		algebra.Capt(square, attacker).apply()
		assert rook.index is None
		assert king.rooks[offset] is rook
		position[square] = material.Rook(color)
		assert king.rooks[offset] is rook
		assert position[square] is not rook

	@pytest.mark.parametrize("token, color, offset, square", partners)
	def test_placement_edits_preserve_castling_partner_identity(self, token, color, offset, square) -> None:
		position = engine.Position(f"{self.castling} w {token} - 0 1")
		king = position.side[color].king
		assert king is not None
		rook = king.rooks[offset]
		position[square] = position[square]
		assert king.rooks[offset] is rook
		position[square] = material.Knight(color)
		assert king.rooks[offset] is rook
		assert rook.index is None
		del position[square]
		assert king.rooks[offset] is rook

	def test_binding_wraps_placement_and_rosters(self) -> None:
		position = engine.Position(self.empty_fen)
		outgoing = material.Pawn(False)
		incoming = material.Knight(True)
		position[geometry.Index.E4] = outgoing

		with position.binding(geometry.Index.E4, incoming) as bound:
			assert bound is None
			assert position[geometry.Index.E4] is outgoing  # pylint: disable = invalid-sequence-index
			assert outgoing.index is None
			assert outgoing not in position.white
			assert incoming.index is None
			assert not hasattr(incoming, "position")
			list.__setitem__(position, geometry.Index.E4, incoming)

		assert position[geometry.Index.E4] is incoming  # pylint: disable = invalid-sequence-index
		assert outgoing.index is None
		assert len(position.white) == 0
		assert incoming.index is geometry.Index.E4
		assert incoming.position is position
		assert incoming.side is position.black
		assert position.black == {incoming}

	def test_binding_propagates_body_exception_without_attaching_incoming(self) -> None:
		position = engine.Position(self.empty_fen)
		incoming = material.Knight(True)

		with pytest.raises(RuntimeError, match = "placement failed"):
			with position.binding(geometry.Index.E4, incoming) as bound:
				assert bound is None

				raise RuntimeError("placement failed")

		assert position[geometry.Index.E4] is None  # pylint: disable = invalid-sequence-index
		assert incoming.index is None
		assert not hasattr(incoming, "position")
		assert len(position.white) == len(position.black) == 0

	@pytest.mark.parametrize("placement, flat", EngineSetup.positions)
	def test_placement_round_trip_and_position_binding(self, placement, flat) -> None:
		position = engine.Position(f"{placement} w - - 0 1")
		assert isinstance(position, engine.Board)
		assert len(position) == 64
		assert repr(position) == placement

		for index, symbol in zip(geometry.Index, flat, strict = True):
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
		first = engine.Position(self.empty_fen)
		second = engine.Position(self.empty_fen)
		piece = material.Pawn(False)
		first[geometry.Index.A2] = piece
		assert first.white == {piece}
		assert len(second.white) == 0

		for color, side_name in zip(self.colors, self.side_names, strict = True):
			assert getattr(first, side_name) is first.side[color]
			assert getattr(first, side_name) is not getattr(second, side_name)
			assert first.side[color].position is first
			assert second.side[color].position is second

	@pytest.mark.parametrize("placement, count", roster_positions)
	def test_initial_rosters_match_active_pieces(self, placement, count) -> None:
		position = engine.Position(f"{placement} w - - 0 1")
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
		position = engine.Position(f"{placement} w - - 0 1")
		assert position.white.king is position[white]
		assert position.black.king is position[black]
		assert position.white.king in position.white
		assert position.black.king in position.black

	@pytest.mark.parametrize("color", EngineSetup.colors)
	@pytest.mark.parametrize("index", EngineSetup.indices)
	def test_assignment_binds_position_and_side(self, color, index) -> None:
		position = engine.Position(self.empty_fen)
		side = position.side[color]
		piece = material.Knight(color)
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
		position = engine.Position(self.empty_fen)
		outgoing_side = position.side[outgoing_color]
		incoming_side = position.side[incoming_color]
		outgoing = material.Pawn(outgoing_color)
		incoming = material.Knight(incoming_color)
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
		position = engine.Position(self.empty_fen)
		side = position.side[color]
		piece = material.Rook(color)
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
		position = engine.Position(self.empty_fen)
		side = position.side[color]
		piece = material.Bishop(color)
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
		position = engine.Position(self.empty_fen)
		outgoing = material.Pawn(True)
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
			assert piece.index is geometry.Index(key)
			assert piece.position is position
			assert piece.color is symbol.islower()
			assert piece.side == {piece}
			assert len(piece.side.other) == 0

	@pytest.mark.parametrize("index", EngineSetup.invalid_indices)
	def test_invalid_assignment_preserves_occupancy_and_rosters(self, index) -> None:
		position = engine.Position(self.empty_fen)
		white = material.Pawn(False)
		black = material.Pawn(True)
		incoming = material.Knight(False)
		position[geometry.Index.A8] = white
		position[geometry.Index.H1] = black
		before = tuple(position)

		with pytest.raises(ValueError):
			position[index] = incoming

		assert tuple(position) == before
		assert position.white == {white}
		assert position.black == {black}
		assert white.index is geometry.Index.A8
		assert black.index is geometry.Index.H1
		assert incoming.index is None
		assert not hasattr(incoming, "position")
