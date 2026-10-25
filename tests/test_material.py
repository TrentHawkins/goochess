from __future__ import annotations


import pytest

from goochess.algebra import Capt, EnPassant, Move, Rush
from goochess.engine import Position
from goochess.geometry import Index
from goochess.material import Bishop, Ghost, King, Knight, Officer, Pawn, Piece, Queen, Rook, Roster
from goochess.structs import collection


class MaterialSetup:

	colors = (False, True)
	kinds = (Pawn, Knight, Bishop, Rook, Queen, King)
	empty = "8/8/8/8/8/8/8/8"

	@staticmethod
	def position() -> Position:
		return Position(MaterialSetup.empty)

	@staticmethod
	def place[T: Piece](position: Position, kind: type[T], index: Index, color: bool) -> T:
		piece = kind(color)
		position[index] = piece

		return piece

	@staticmethod
	def targets(piece: Piece) -> dict[Index, type]:
		return {Index(int(step)): type(step) for step in piece.targets}


class TestPiece(MaterialSetup):

	canonical = (Pawn, Queen, Rook, Knight, Bishop, King)
	invalid_symbols = ("", "-", "X", "PP", "1")
	invalid_targets = (-1, 64)
	moved_states = (False, True)

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_initial_state(self, color) -> None:
		piece = Piece(color)
		assert piece.color is color
		assert piece.index is None
		assert not hasattr(piece, "position")
		assert not piece.moved
		assert piece.value == 0
		assert repr(piece) == "-"
		assert piece.targets == piece.squares == collection()

	@pytest.mark.parametrize("kind", canonical)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_fromnotation(self, kind, color) -> None:
		symbol = kind.black if color else kind.white
		piece = Piece.fromnotation(symbol)
		assert type(piece) is kind
		assert piece.color is color
		assert not hasattr(piece, "position")
		assert piece.index is None
		assert not piece.moved
		assert piece.targets == collection()
		assert repr(piece) == symbol

	@pytest.mark.parametrize("symbol", invalid_symbols)
	def test_unknown_symbol(self, symbol) -> None:
		with pytest.raises(KeyError):
			Piece.fromnotation(symbol)

	def test_side_is_derived_and_read_only(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		assert piece.position is position
		assert piece.side is position.side[piece.color] is position.white

		with pytest.raises(AttributeError):
			setattr(piece, "side", position.black)

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
		assert not hasattr(piece, "position")
		assert piece.targets == piece.squares == collection()

	def test_piece_lifecycles_are_independent(self) -> None:
		position = self.position()
		first = Piece.fromnotation("P")
		second = Piece.fromnotation("P")
		position[Index.A2] = first
		first.moved = True
		assert second.index is None
		assert not hasattr(second, "position")
		assert second not in position.white
		assert not second.moved
		position[Index.H2] = second
		del position[Index.A2]
		assert first.index is None
		assert first.side is position.white
		assert first.position is position
		assert first not in position.white
		assert second.index is Index.H2
		assert not second.moved

	@pytest.mark.parametrize("kind", MaterialSetup.kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_removed_has_no_targets(self, kind, color) -> None:
		position = self.position()
		piece = self.place(position, kind, Index.D4, color)
		del position[Index.D4]
		assert piece.index is None
		assert piece.side is position.side[color]
		assert piece.position is position
		assert piece not in piece.side
		assert piece.targets == piece.squares == collection()

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_relocation_and_restoration_preserve_movement_flag(self, color, moved) -> None:
		position = self.position()
		source, target = Index.D4, Index.D5
		piece = self.place(position, Pawn, source, color)
		piece.moved = moved
		other = self.place(position, Knight, target, not color)
		before = tuple(position)
		assert piece(target) is piece
		assert position[source] is None  # pylint: disable = invalid-sequence-index
		assert position[target] is piece  # pylint: disable = invalid-sequence-index
		assert piece.index is target
		assert piece in piece.side
		assert piece.moved is moved
		assert other.index is None
		assert other not in other.side
		assert piece(source, other) is piece
		assert tuple(position) == before
		assert piece.index is source
		assert piece in piece.side
		assert piece.moved is moved
		assert other.index is target
		assert other in other.side

	@pytest.mark.parametrize("target", invalid_targets)
	def test_invalid_relocation_keeps_source_unchanged(self, target) -> None:
		position = self.position()
		source = Index.E2
		piece = self.place(position, Pawn, source, False)
		before = tuple(position)

		with pytest.raises(ValueError):
			piece(target)

		assert tuple(position) == before
		assert piece.index is source
		assert piece in piece.side
		assert not piece.moved

	@pytest.mark.parametrize("placed", (False, True))
	def test_detached_piece_cannot_be_relocated(self, placed) -> None:
		position = self.position()
		piece = Pawn(False)

		if placed:
			source = Index.E2
			position[source] = piece
			del position[source]

		before = tuple(position)

		with pytest.raises(AssertionError):
			piece(Index.E3)

		assert tuple(position) == before
		assert piece.index is None
		assert piece not in position.white
		assert not piece.moved


class TestGhost(MaterialSetup):

	placements = ((False, Index.E4, Index.E3), (True, Index.E5, Index.E6))

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_initial_state_and_pawn_reference(self, color) -> None:
		pawn = Pawn(color)
		pawn.moved = True
		ghost = Ghost(pawn)
		assert ghost.rusher is pawn
		assert ghost.color is pawn.color
		assert ghost.index is None
		assert not hasattr(ghost, "position")
		assert not ghost.moved
		assert repr(ghost) == "-"
		assert ghost.targets == ghost.squares == collection()

	@pytest.mark.parametrize("color, source, target", placements)
	def test_placement_and_removal_preserve_pawn_reference(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		ghost = Ghost(pawn)
		position[target] = ghost
		assert ghost.side is pawn.side
		assert ghost in pawn.side
		del position[target]
		assert ghost.index is None
		assert ghost.rusher is pawn
		assert ghost not in pawn.side
		assert ghost.targets == ghost.squares == collection()
		assert position[source] is pawn
		assert pawn.index is source
		assert pawn in pawn.side

	def test_requires_pawn(self) -> None:
		with pytest.raises(AssertionError):
			Ghost(Knight(False))  # pyright: ignore[reportArgumentType]


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
		position = self.position()
		piece = self.place(position, kind, Index.D4, color)
		assert self.targets(piece) == {index: Move for index in self.center[kind]}
		assert piece.index is Index.D4
		assert position[Index.D4] is piece  # pylint: disable = invalid-sequence-index

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.position(), kind, source, color)
		assert self.targets(piece) == {index: Move for index in expected}

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_destination(self, kind, color, friendly) -> None:
		position = self.position()
		piece = self.place(position, kind, Index.D4, color)
		target = self.blockers[kind]
		self.place(position, Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: Move for index in self.center[kind]}

		if friendly:
			del expected[target]

		else:
			expected[target] = Capt

		assert self.targets(piece) == expected

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_knight_jumps_over_occupied_square(self, color) -> None:
		position = self.position()
		piece = self.place(position, Knight, Index.D4, color)
		self.place(position, Pawn, Index.E4, color)
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
		piece = self.place(self.position(), kind, Index.D4, color)
		assert self.targets(piece) == {index: Move for index in self.center[kind]}

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.position(), kind, source, color)
		assert self.targets(piece) == {index: Move for index in expected}

	@pytest.mark.parametrize("kind, line", lines)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("distance", (0, 1))
	def test_stops_at_first_occupied_square(self, kind, line, color, friendly, distance) -> None:
		position = self.position()
		piece = self.place(position, kind, Index.D4, color)
		target = line[distance]
		self.place(position, Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: Move for index in self.center[kind] - set(line[distance + 1:])}

		if friendly:
			del expected[target]

		else:
			expected[target] = Capt

		assert self.targets(piece) == expected


class TestKing(MaterialSetup):

	pawn_attacks = (
		(False, Index.D4, Index.C5, Index.D5),
		(True, Index.D5, Index.C4, Index.D4),
	)

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_unplaced_king_is_not_safe(self, color) -> None:
		assert not King(color).safe

	@pytest.mark.parametrize("color, square, diagonal, forward", pawn_attacks)
	def test_opposing_pawn_attacks_diagonally(self, color, square, diagonal, forward) -> None:
		position = self.position()
		king = self.place(position, King, square, color)
		assert king.safe
		self.place(position, Pawn, forward, not color)
		assert king.safe
		del position[forward]
		self.place(position, Pawn, diagonal, not color)
		assert not king.safe

	def test_pinned_opponent_still_attacks(self) -> None:
		position = Position("4k3/8/4n3/8/5K2/8/8/4R3")
		king = position.white.king
		assert king is not None
		assert not king.safe


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
	en_passant = (
		(False, "k7/8/8/r4pPK/8/8/8/8", Index.G5, Index.F5, Index.F6, Index.A5),
		(True, "8/8/8/8/R4Ppk/8/8/K7", Index.G4, Index.F4, Index.F3, Index.A4),
	)

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_forward_moves(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		assert self.targets(pawn) == {single: Move, double: Rush}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_moved_pawn_has_no_double_step(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		pawn.moved = True
		assert self.targets(pawn) == {single: Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_forward_square_blocks_both_steps(self, color, source, single, double, diagonals, friendly) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, single, pawn.color if friendly else not pawn.color)
		assert pawn.targets == collection()

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_double_destination_preserves_single_step(self, color, source, single, double, diagonals, friendly) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, double, pawn.color if friendly else not pawn.color)
		assert self.targets(pawn) == {single: Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("direction", (0, 1))
	def test_diagonal_capture(self, color, source, single, double, diagonals, friendly, direction) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		target = diagonals[direction]
		self.place(position, Pawn, target, pawn.color if friendly else not pawn.color)
		expected = {single: Move, double: Rush}

		if not friendly:
			expected[target] = Capt

		assert self.targets(pawn) == expected

	@pytest.mark.parametrize("color, source, single, double, capture", edges)
	def test_edge_keeps_inward_capture(self, color, source, single, double, capture) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: Move, double: Rush, capture: Capt}

	@pytest.mark.parametrize("color, source, single, capture", penultimate)
	def test_final_step_keeps_capture_after_double_step_leaves_board(self, color, source, single, capture) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: Move, capture: Capt}

	@pytest.mark.parametrize("color, source", terminal)
	def test_terminal_rank_has_no_targets(self, color, source) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		assert pawn.targets == collection()

	@pytest.mark.parametrize("color, placement, source, middle, target, attacker", en_passant)
	@pytest.mark.parametrize("attacked", (False, True))
	def test_en_passant_king_safety_removes_both_pawns(self, color, placement, source,
		middle, target, attacker, attacked,
	) -> None:
		position = Position(placement)
		pawn = position[source]
		assert isinstance(pawn, Pawn)
		victim = position[middle]
		assert isinstance(victim, Pawn)
		ghost = Ghost(victim)
		position[target] = ghost

		if not attacked:
			del position[attacker]

		king = pawn.side.king
		assert king is not None and king.safe
		before = tuple(position), frozenset(position.white), frozenset(position.black)
		assert self.targets(pawn)[target] is EnPassant
		assert (target in pawn.squares) is not attacked
		assert (tuple(position), frozenset(position.white), frozenset(position.black)) == before
		assert pawn.index is source
		assert victim.index is middle
		assert ghost.index is target
		assert not pawn.moved
		assert king.safe

	@pytest.mark.parametrize("color, placement, source, middle, target, attacker", en_passant)
	def test_ghost_without_capturable_pawn_is_not_a_target(self, color, placement,
		source, middle, target, attacker,
	) -> None:
		position = Position(placement)
		pawn = position[source]
		assert isinstance(pawn, Pawn)
		victim = position[middle]
		assert isinstance(victim, Pawn)
		position[target] = Ghost(victim)
		del position[middle]
		assert target not in self.targets(pawn)
		assert target not in pawn.squares
