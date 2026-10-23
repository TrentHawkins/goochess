from __future__ import annotations


import pytest

from goochess.algebra import Capt, Move, Rush
from goochess.engine import Game
from goochess.geometry import Index
from goochess.material import Bishop, Ghost, King, Knight, Officer, Pawn, Piece, Queen, Rook, Roster
from goochess.mathematics import indices


class MaterialSetup:

	colors = (False, True)
	kinds = (Pawn, Knight, Bishop, Rook, Queen, King, Ghost)
	empty = "8/8/8/8/8/8/8/8"

	@staticmethod
	def game() -> Game:
		return Game(MaterialSetup.empty)

	@staticmethod
	def place[T: Piece](game: Game, kind: type[T], index: Index, color: bool) -> T:
		piece = kind(color)
		game[index] = piece

		return piece

	@staticmethod
	def targets(piece: Piece) -> dict[Index, type]:
		return {Index(int(step)): type(step) for step in piece.targets}


class TestPiece(MaterialSetup):

	canonical = (Pawn, Queen, Rook, Knight, Bishop, King)
	invalid_symbols = ("", "-", "X", "PP", "1")

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_initial_state(self, color) -> None:
		piece = Piece(color)
		assert piece.color is color
		assert piece.index is None
		assert not hasattr(piece, "game")
		assert not piece.moved
		assert piece.value == 0
		assert repr(piece) == "-"
		assert piece.targets == piece.squares == indices()

	@pytest.mark.parametrize("kind", canonical)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_fromnotation(self, kind, color) -> None:
		symbol = kind.black if color else kind.white
		piece = Piece.fromnotation(symbol)
		assert type(piece) is kind
		assert piece.color is color
		assert not hasattr(piece, "game")
		assert piece.index is None
		assert not piece.moved
		assert piece.targets == indices()
		assert repr(piece) == symbol

	@pytest.mark.parametrize("symbol", invalid_symbols)
	def test_unknown_symbol(self, symbol) -> None:
		with pytest.raises(KeyError):
			Piece.fromnotation(symbol)

	def test_side_is_derived_and_read_only(self) -> None:
		game = self.game()
		piece = self.place(game, Pawn, Index.E2, False)
		assert piece.game is game
		assert piece.side is game.side[piece.color] is game.white

		with pytest.raises(AttributeError):
			setattr(piece, "side", game.black)

	def test_identity_and_hash(self) -> None:
		first = Pawn(False)
		second = Pawn(False)
		assert first == first
		assert first != second
		assert len({first, second}) == 2
		assert {first: "first", second: "second"}[first] == "first"

	@pytest.mark.parametrize("kind", MaterialSetup.kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_unplaced_has_no_targets(self, kind, color) -> None:
		piece = kind(color)
		assert piece.index is None
		assert not hasattr(piece, "game")
		assert piece.targets == piece.squares == indices()

	def test_piece_lifecycles_are_independent(self) -> None:
		game = self.game()
		first = Piece.fromnotation("P")
		second = Piece.fromnotation("P")
		game[Index.A2] = first
		first.moved = True
		assert second.index is None
		assert not hasattr(second, "game")
		assert second not in game.white
		assert not second.moved
		game[Index.H2] = second
		del game[Index.A2]
		assert first.index is None
		assert first.side is game.white
		assert first.game is game
		assert first not in game.white
		assert second.index is Index.H2
		assert not second.moved

	@pytest.mark.parametrize("kind", MaterialSetup.kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_removed_has_no_targets(self, kind, color) -> None:
		game = self.game()
		piece = self.place(game, kind, Index.D4, color)
		del game[Index.D4]
		assert piece.index is None
		assert piece.side is game.side[color]
		assert piece.game is game
		assert piece not in piece.side
		assert piece.targets == piece.squares == indices()


class TestRoster:

	members = (("P", Pawn), ("Q", Queen), ("R", Rook), ("N", Knight), ("B", Bishop), ("K", King))

	@pytest.mark.parametrize("symbol, kind", members)
	def test_class_values(self, symbol, kind) -> None:
		assert Roster[symbol].value is kind

	def test_contains_only_canonical_pieces(self) -> None:
		assert set(Roster.__members__) == {symbol for symbol, _ in self.members}
		assert Ghost not in {member.value for member in Roster}


class TestOfficer:

	members = (("Q", Queen), ("R", Rook), ("N", Knight), ("B", Bishop))

	@pytest.mark.parametrize("symbol, kind", members)
	def test_class_values(self, symbol, kind) -> None:
		assert Officer[symbol].value is kind

	def test_choice_order(self) -> None:
		assert tuple(member.name for member in Officer) == tuple(symbol for symbol, _ in self.members)


class TestMelee(MaterialSetup):

	kinds = (Knight, King)
	center = {
		Knight: frozenset((Index.B3, Index.B5, Index.C2, Index.C6, Index.E2, Index.E6, Index.F3, Index.F5)),
		King: frozenset((Index.C3, Index.D3, Index.E3, Index.C4, Index.E4, Index.C5, Index.D5, Index.E5)),
	}
	blockers = {Knight: Index.F5, King: Index.E5}
	corners = (
		(Knight, Index.A1, {Index.B3, Index.C2}),
		(Knight, Index.A8, {Index.B6, Index.C7}),
		(Knight, Index.H1, {Index.F2, Index.G3}),
		(Knight, Index.H8, {Index.F7, Index.G6}),
		(King, Index.A1, {Index.A2, Index.B1, Index.B2}),
		(King, Index.A8, {Index.A7, Index.B7, Index.B8}),
		(King, Index.H1, {Index.G1, Index.G2, Index.H2}),
		(King, Index.H8, {Index.G7, Index.G8, Index.H7}),
	)

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_empty_board(self, kind, color) -> None:
		game = self.game()
		piece = self.place(game, kind, Index.D4, color)
		assert self.targets(piece) == {index: Move for index in self.center[kind]}
		assert piece.index is Index.D4
		assert game[Index.D4] is piece  # pylint: disable = invalid-sequence-index

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.game(), kind, source, color)
		assert self.targets(piece) == {index: Move for index in expected}

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_destination(self, kind, color, friendly) -> None:
		game = self.game()
		piece = self.place(game, kind, Index.D4, color)
		target = self.blockers[kind]
		self.place(game, Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: Move for index in self.center[kind]}

		if friendly:
			del expected[target]

		else:
			expected[target] = Capt

		assert self.targets(piece) == expected

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_knight_jumps_over_occupied_square(self, color) -> None:
		game = self.game()
		piece = self.place(game, Knight, Index.D4, color)
		self.place(game, Pawn, Index.E4, color)
		assert self.targets(piece) == {index: Move for index in self.center[Knight]}


class TestRanged(MaterialSetup):

	rook_center = frozenset((Index.D1, Index.D2, Index.D3, Index.D5, Index.D6, Index.D7, Index.D8,
		Index.A4, Index.B4, Index.C4, Index.E4, Index.F4, Index.G4, Index.H4))
	bishop_center = frozenset((Index.A1, Index.B2, Index.C3, Index.E5, Index.F6, Index.G7, Index.H8,
		Index.A7, Index.B6, Index.C5, Index.E3, Index.F2, Index.G1))
	center = {Rook: rook_center, Bishop: bishop_center, Queen: rook_center | bishop_center}
	lines = (
		(Rook, (Index.E4, Index.F4, Index.G4, Index.H4)),
		(Bishop, (Index.E5, Index.F6, Index.G7, Index.H8)),
		(Queen, (Index.E4, Index.F4, Index.G4, Index.H4)),
	)
	rook_a1 = frozenset((Index.A2, Index.A3, Index.A4, Index.A5, Index.A6, Index.A7, Index.A8,
		Index.B1, Index.C1, Index.D1, Index.E1, Index.F1, Index.G1, Index.H1))
	bishop_a1 = frozenset((Index.B2, Index.C3, Index.D4, Index.E5, Index.F6, Index.G7, Index.H8))
	rook_a8 = frozenset((Index.A1, Index.A2, Index.A3, Index.A4, Index.A5, Index.A6, Index.A7,
		Index.B8, Index.C8, Index.D8, Index.E8, Index.F8, Index.G8, Index.H8))
	bishop_a8 = frozenset((Index.B7, Index.C6, Index.D5, Index.E4, Index.F3, Index.G2, Index.H1))
	corners = (
		(Rook, Index.A1, rook_a1),
		(Bishop, Index.A1, bishop_a1),
		(Queen, Index.A1, rook_a1 | bishop_a1),
		(Rook, Index.A8, rook_a8),
		(Bishop, Index.A8, bishop_a8),
		(Queen, Index.A8, rook_a8 | bishop_a8),
	)

	@pytest.mark.parametrize("kind", (Rook, Bishop, Queen))
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_empty_board(self, kind, color) -> None:
		piece = self.place(self.game(), kind, Index.D4, color)
		assert self.targets(piece) == {index: Move for index in self.center[kind]}

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.game(), kind, source, color)
		assert self.targets(piece) == {index: Move for index in expected}

	@pytest.mark.parametrize("kind, line", lines)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("distance", (0, 1))
	def test_stops_at_first_occupied_square(self, kind, line, color, friendly, distance) -> None:
		game = self.game()
		piece = self.place(game, kind, Index.D4, color)
		target = line[distance]
		self.place(game, Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: Move for index in self.center[kind] - set(line[distance + 1:])}

		if friendly:
			del expected[target]

		else:
			expected[target] = Capt

		assert self.targets(piece) == expected


class TestPawn(MaterialSetup):

	cases = (
		(False, Index.E2, Index.E3, Index.E4, (Index.D3, Index.F3)),
		(True, Index.E7, Index.E6, Index.E5, (Index.D6, Index.F6)),
	)
	edges = (
		(False, Index.A2, Index.A3, Index.A4, Index.B3),
		(False, Index.H2, Index.H3, Index.H4, Index.G3),
		(True, Index.A7, Index.A6, Index.A5, Index.B6),
		(True, Index.H7, Index.H6, Index.H5, Index.G6),
	)
	penultimate = (
		(False, Index.E7, Index.E8, Index.D8),
		(True, Index.E2, Index.E1, Index.D1),
	)
	terminal = ((False, Index.A8), (True, Index.A1))

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_forward_moves(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.game(), Pawn, source, color)
		assert self.targets(pawn) == {single: Move, double: Rush}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_moved_pawn_has_no_double_step(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.game(), Pawn, source, color)
		pawn.moved = True
		assert self.targets(pawn) == {single: Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_forward_square_blocks_both_steps(self, color, source, single, double, diagonals, friendly) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Pawn, single, pawn.color if friendly else not pawn.color)
		assert pawn.targets == indices()

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_double_destination_preserves_single_step(self, color, source, single, double, diagonals, friendly) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Pawn, double, pawn.color if friendly else not pawn.color)
		assert self.targets(pawn) == {single: Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("direction", (0, 1))
	def test_diagonal_capture(self, color, source, single, double, diagonals, friendly, direction) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		target = diagonals[direction]
		self.place(game, Pawn, target, pawn.color if friendly else not pawn.color)
		expected = {single: Move, double: Rush}

		if not friendly:
			expected[target] = Capt

		assert self.targets(pawn) == expected

	@pytest.mark.parametrize("color, source, single, double, capture", edges)
	def test_edge_keeps_inward_capture(self, color, source, single, double, capture) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: Move, double: Rush, capture: Capt}

	@pytest.mark.parametrize("color, source, single, capture", penultimate)
	def test_final_step_keeps_capture_after_double_step_leaves_board(self, color, source, single, capture) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: Move, capture: Capt}

	@pytest.mark.parametrize("color, source", terminal)
	def test_terminal_rank_has_no_targets(self, color, source) -> None:
		pawn = self.place(self.game(), Pawn, source, color)
		assert pawn.targets == indices()
