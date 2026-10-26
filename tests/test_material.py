from __future__ import annotations


import pytest

from goochess import algebra
from goochess import engine
from goochess import geometry
from goochess import material
from goochess import structs


class MaterialSetup:

	colors = (False, True)
	kinds = (material.Pawn, material.Knight, material.Bishop, material.Rook, material.Queen, material.King)
	empty = "8/8/8/8/8/8/8/8"

	@staticmethod
	def position() -> engine.Position:
		return engine.Position(MaterialSetup.empty)

	@staticmethod
	def place[T: material.Piece](position: engine.Position, kind: type[T], index: geometry.Index, color: bool) -> T:
		piece = kind(color)
		position[index] = piece

		return piece

	@staticmethod
	def targets(piece: material.Piece) -> dict[geometry.Index, type]:
		return {geometry.Index(int(step)): type(step) for step in piece.targets}


class TestPiece(MaterialSetup):

	canonical = (material.Pawn, material.Queen, material.Rook, material.Knight, material.Bishop, material.King)
	invalid_symbols = ("", "-", "X", "PP", "1")
	invalid_targets = (-1, 64)
	moved_states = (False, True)

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_initial_state(self, color) -> None:
		piece = material.Piece(color)
		assert piece.color is color
		assert piece.index is None
		assert not hasattr(piece, "position")
		assert not piece.moved
		assert piece.value == 0
		assert repr(piece) == "-"
		assert piece.targets == piece.squares == structs.collection()

	@pytest.mark.parametrize("kind", canonical)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_fromnotation(self, kind, color) -> None:
		symbol = kind.black if color else kind.white
		piece = material.Piece.fromnotation(symbol)
		assert type(piece) is kind
		assert piece.color is color
		assert not hasattr(piece, "position")
		assert piece.index is None
		assert not piece.moved
		assert piece.targets == structs.collection()
		assert repr(piece) == symbol

	@pytest.mark.parametrize("symbol", invalid_symbols)
	def test_unknown_symbol(self, symbol) -> None:
		with pytest.raises(KeyError):
			material.Piece.fromnotation(symbol)

	def test_side_is_derived_and_read_only(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		assert piece.position is position
		assert piece.side is position.side[piece.color] is position.white

		with pytest.raises(AttributeError):
			setattr(piece, "side", position.black)

	def test_identity_and_hash(self) -> None:
		first = material.Pawn(False)
		second = material.Pawn(False)
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
		assert piece.targets == piece.squares == structs.collection()

	def test_piece_lifecycles_are_independent(self) -> None:
		position = self.position()
		first = material.Piece.fromnotation("P")
		second = material.Piece.fromnotation("P")
		position[geometry.Index.A2] = first
		first.moved = True
		assert second.index is None
		assert not hasattr(second, "position")
		assert second not in position.white
		assert not second.moved
		position[geometry.Index.H2] = second
		del position[geometry.Index.A2]
		assert first.index is None
		assert first.side is position.white
		assert first.position is position
		assert first not in position.white
		assert second.index is geometry.Index.H2
		assert not second.moved

	@pytest.mark.parametrize("kind", MaterialSetup.kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_removed_has_no_targets(self, kind, color) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		del position[geometry.Index.D4]
		assert piece.index is None
		assert piece.side is position.side[color]
		assert piece.position is position
		assert piece not in piece.side
		assert piece.targets == piece.squares == structs.collection()

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_relocation_marks_moved_and_restoration_restores_flag(self, color, moved) -> None:
		position = self.position()
		source, target = geometry.Index.D4, geometry.Index.D5
		piece = self.place(position, material.Pawn, source, color)
		piece.moved = moved
		other = self.place(position, material.Knight, target, not color)
		before = tuple(position)
		assert piece(target) is piece
		assert position[source] is None  # pylint: disable = invalid-sequence-index
		assert position[target] is piece  # pylint: disable = invalid-sequence-index
		assert piece.index is target
		assert piece in piece.side
		assert piece.moved
		assert other.index is None
		assert other not in other.side
		assert piece(source, kept = other, moved = moved) is piece
		assert tuple(position) == before
		assert piece.index is source
		assert piece in piece.side
		assert piece.moved is moved
		assert other.index is target
		assert other in other.side

	@pytest.mark.parametrize("target", invalid_targets)
	def test_invalid_relocation_keeps_source_unchanged(self, target) -> None:
		position = self.position()
		source = geometry.Index.E2
		piece = self.place(position, material.Pawn, source, False)
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
		piece = material.Pawn(False)

		if placed:
			source = geometry.Index.E2
			position[source] = piece
			del position[source]

		before = tuple(position)

		with pytest.raises(AssertionError):
			piece(geometry.Index.E3)

		assert tuple(position) == before
		assert piece.index is None
		assert piece not in position.white
		assert not piece.moved


class TestGhost(MaterialSetup):

	placements = ((False, geometry.Index.E4, geometry.Index.E3), (True, geometry.Index.E5, geometry.Index.E6))

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_initial_state_and_pawn_reference(self, color) -> None:
		pawn = material.Pawn(color)
		pawn.moved = True
		ghost = material.Ghost(pawn)
		assert ghost.rusher is pawn
		assert ghost.color is pawn.color
		assert ghost.index is None
		assert not hasattr(ghost, "position")
		assert not ghost.moved
		assert repr(ghost) == "-"
		assert ghost.targets == ghost.squares == structs.collection()

	@pytest.mark.parametrize("color, source, target", placements)
	def test_placement_and_removal_preserve_pawn_reference(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		ghost = material.Ghost(pawn)
		position[target] = ghost
		assert ghost.side is pawn.side
		assert ghost in pawn.side
		del position[target]
		assert ghost.index is None
		assert ghost.rusher is pawn
		assert ghost not in pawn.side
		assert ghost.targets == ghost.squares == structs.collection()
		assert position[source] is pawn
		assert pawn.index is source
		assert pawn in pawn.side

	def test_requires_pawn(self) -> None:
		with pytest.raises(AssertionError):
			material.Ghost(material.Knight(False))  # pyright: ignore[reportArgumentType]


class TestRoster:

	members = (("P", material.Pawn), ("Q", material.Queen), ("R", material.Rook), ("N", material.Knight), ("B", material.Bishop), ("K", material.King))

	@pytest.mark.parametrize("symbol, kind", members)
	def test_class_values(self, symbol, kind) -> None:
		assert material.Roster[symbol].value is kind

	def test_contains_only_canonical_pieces(self) -> None:
		assert set(material.Roster.__members__) == {symbol for symbol, _ in self.members}
		assert material.Ghost not in {member.value for member in material.Roster}


class TestOfficer:

	members = (("Q", material.Queen), ("R", material.Rook), ("N", material.Knight), ("B", material.Bishop))

	@pytest.mark.parametrize("symbol, kind", members)
	def test_class_values(self, symbol, kind) -> None:
		assert material.Officer[symbol].value is kind

	def test_choice_order(self) -> None:
		assert tuple(member.name for member in material.Officer) == tuple(symbol for symbol, _ in self.members)


class TestMelee(MaterialSetup):

	kinds = (material.Knight, material.King)
	center = {
		material.Knight: frozenset((geometry.Index.B3, geometry.Index.B5, geometry.Index.C2, geometry.Index.C6, geometry.Index.E2, geometry.Index.E6, geometry.Index.F3, geometry.Index.F5)),
		material.King: frozenset((geometry.Index.C3, geometry.Index.D3, geometry.Index.E3, geometry.Index.C4, geometry.Index.E4, geometry.Index.C5, geometry.Index.D5, geometry.Index.E5)),
	}
	blockers = {material.Knight: geometry.Index.F5, material.King: geometry.Index.E5}
	corners = (
		(material.Knight, geometry.Index.A1, {geometry.Index.B3, geometry.Index.C2}),
		(material.Knight, geometry.Index.A8, {geometry.Index.B6, geometry.Index.C7}),
		(material.Knight, geometry.Index.H1, {geometry.Index.F2, geometry.Index.G3}),
		(material.Knight, geometry.Index.H8, {geometry.Index.F7, geometry.Index.G6}),
		(material.King, geometry.Index.A1, {geometry.Index.A2, geometry.Index.B1, geometry.Index.B2}),
		(material.King, geometry.Index.A8, {geometry.Index.A7, geometry.Index.B7, geometry.Index.B8}),
		(material.King, geometry.Index.H1, {geometry.Index.G1, geometry.Index.G2, geometry.Index.H2}),
		(material.King, geometry.Index.H8, {geometry.Index.G7, geometry.Index.G8, geometry.Index.H7}),
	)

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_empty_board(self, kind, color) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		assert self.targets(piece) == {index: algebra.Move for index in self.center[kind]}
		assert piece.index is geometry.Index.D4
		assert position[geometry.Index.D4] is piece  # pylint: disable = invalid-sequence-index

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.position(), kind, source, color)
		assert self.targets(piece) == {index: algebra.Move for index in expected}

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_destination(self, kind, color, friendly) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		target = self.blockers[kind]
		self.place(position, material.Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: algebra.Move for index in self.center[kind]}

		if friendly:
			del expected[target]

		else:
			expected[target] = algebra.Capt

		assert self.targets(piece) == expected

	@pytest.mark.parametrize("kind", kinds)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("ghost_color", MaterialSetup.colors)
	def test_ghost_destination_is_a_quiet_move(self, kind, color, ghost_color) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		target = self.blockers[kind]
		ghost = material.Ghost(material.Pawn(ghost_color))
		position[target] = ghost
		assert self.targets(piece) == {index: algebra.Move for index in self.center[kind]}
		assert position[target] is ghost
		assert ghost.index is target

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_knight_jumps_over_occupied_square(self, color) -> None:
		position = self.position()
		piece = self.place(position, material.Knight, geometry.Index.D4, color)
		self.place(position, material.Pawn, geometry.Index.E4, color)
		assert self.targets(piece) == {index: algebra.Move for index in self.center[material.Knight]}


class TestRanged(MaterialSetup):

	rook_center = frozenset((geometry.Index.D1, geometry.Index.D2, geometry.Index.D3, geometry.Index.D5, geometry.Index.D6, geometry.Index.D7, geometry.Index.D8,
		geometry.Index.A4, geometry.Index.B4, geometry.Index.C4, geometry.Index.E4, geometry.Index.F4, geometry.Index.G4, geometry.Index.H4))
	bishop_center = frozenset((geometry.Index.A1, geometry.Index.B2, geometry.Index.C3, geometry.Index.E5, geometry.Index.F6, geometry.Index.G7, geometry.Index.H8,
		geometry.Index.A7, geometry.Index.B6, geometry.Index.C5, geometry.Index.E3, geometry.Index.F2, geometry.Index.G1))
	center = {material.Rook: rook_center, material.Bishop: bishop_center, material.Queen: rook_center | bishop_center}
	lines = (
		(material.Rook, (geometry.Index.E4, geometry.Index.F4, geometry.Index.G4, geometry.Index.H4)),
		(material.Bishop, (geometry.Index.E5, geometry.Index.F6, geometry.Index.G7, geometry.Index.H8)),
		(material.Queen, (geometry.Index.E4, geometry.Index.F4, geometry.Index.G4, geometry.Index.H4)),
	)
	rook_a1 = frozenset((geometry.Index.A2, geometry.Index.A3, geometry.Index.A4, geometry.Index.A5, geometry.Index.A6, geometry.Index.A7, geometry.Index.A8,
		geometry.Index.B1, geometry.Index.C1, geometry.Index.D1, geometry.Index.E1, geometry.Index.F1, geometry.Index.G1, geometry.Index.H1))
	bishop_a1 = frozenset((geometry.Index.B2, geometry.Index.C3, geometry.Index.D4, geometry.Index.E5, geometry.Index.F6, geometry.Index.G7, geometry.Index.H8))
	rook_a8 = frozenset((geometry.Index.A1, geometry.Index.A2, geometry.Index.A3, geometry.Index.A4, geometry.Index.A5, geometry.Index.A6, geometry.Index.A7,
		geometry.Index.B8, geometry.Index.C8, geometry.Index.D8, geometry.Index.E8, geometry.Index.F8, geometry.Index.G8, geometry.Index.H8))
	bishop_a8 = frozenset((geometry.Index.B7, geometry.Index.C6, geometry.Index.D5, geometry.Index.E4, geometry.Index.F3, geometry.Index.G2, geometry.Index.H1))
	corners = (
		(material.Rook, geometry.Index.A1, rook_a1),
		(material.Bishop, geometry.Index.A1, bishop_a1),
		(material.Queen, geometry.Index.A1, rook_a1 | bishop_a1),
		(material.Rook, geometry.Index.A8, rook_a8),
		(material.Bishop, geometry.Index.A8, bishop_a8),
		(material.Queen, geometry.Index.A8, rook_a8 | bishop_a8),
	)

	@pytest.mark.parametrize("kind", (material.Rook, material.Bishop, material.Queen))
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_empty_board(self, kind, color) -> None:
		piece = self.place(self.position(), kind, geometry.Index.D4, color)
		assert self.targets(piece) == {index: algebra.Move for index in self.center[kind]}

	@pytest.mark.parametrize("kind, source, expected", corners)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_corner_clipping(self, kind, source, expected, color) -> None:
		piece = self.place(self.position(), kind, source, color)
		assert self.targets(piece) == {index: algebra.Move for index in expected}

	@pytest.mark.parametrize("kind, line", lines)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("distance", (0, 1))
	def test_stops_at_first_occupied_square(self, kind, line, color, friendly, distance) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		target = line[distance]
		self.place(position, material.Pawn, target, piece.color if friendly else not piece.color)
		expected = {index: algebra.Move for index in self.center[kind] - set(line[distance + 1:])}

		if friendly:
			del expected[target]

		else:
			expected[target] = algebra.Capt

		assert self.targets(piece) == expected

	@pytest.mark.parametrize("kind, line", lines)
	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("ghost_color", MaterialSetup.colors)
	def test_ray_passes_through_ghost_to_real_capture(self, kind, line, color, ghost_color) -> None:
		position = self.position()
		piece = self.place(position, kind, geometry.Index.D4, color)
		ghost = material.Ghost(material.Pawn(ghost_color))
		position[line[0]] = ghost
		self.place(position, material.Pawn, line[2], not color)
		expected = {index: algebra.Move for index in self.center[kind] - {line[3]}}
		expected[line[2]] = algebra.Capt
		assert self.targets(piece) == expected
		assert position[line[0]] is ghost
		assert ghost.index is line[0]


class TestKing(MaterialSetup):

	pawn_attacks = (
		(False, geometry.Index.D4, geometry.Index.C5, geometry.Index.D5),
		(True, geometry.Index.D5, geometry.Index.C4, geometry.Index.D4),
	)

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	def test_unplaced_king_is_not_safe(self, color) -> None:
		assert not material.King(color).safe

	@pytest.mark.parametrize("color, square, diagonal, forward", pawn_attacks)
	def test_opposing_pawn_attacks_diagonally(self, color, square, diagonal, forward) -> None:
		position = self.position()
		king = self.place(position, material.King, square, color)
		assert king.safe
		self.place(position, material.Pawn, forward, not color)
		assert king.safe
		del position[forward]
		self.place(position, material.Pawn, diagonal, not color)
		assert not king.safe

	def test_pinned_opponent_still_attacks(self) -> None:
		position = engine.Position("4k3/8/4n3/8/5K2/8/8/4R3")
		king = position.white.king
		assert king is not None
		assert not king.safe

	@pytest.mark.parametrize("color", MaterialSetup.colors)
	@pytest.mark.parametrize("ghost_color", MaterialSetup.colors)
	def test_ghost_does_not_block_attacking_ray(self, color, ghost_color) -> None:
		position = self.position()
		king = self.place(position, material.King, geometry.Index.H4, color)
		self.place(position, material.Rook, geometry.Index.A4, not color)
		position[geometry.Index.D4] = material.Ghost(material.Pawn(ghost_color))
		assert not king.safe


class TestPawn(MaterialSetup):

	cases = (
		(False, geometry.Index.E2, geometry.Index.E3, geometry.Index.E4, (geometry.Index.D3, geometry.Index.F3)),
		(True, geometry.Index.E7, geometry.Index.E6, geometry.Index.E5, (geometry.Index.D6, geometry.Index.F6)),
	)
	edges = (
		(False, geometry.Index.A2, geometry.Index.A3, geometry.Index.A4, geometry.Index.B3),
		(False, geometry.Index.H2, geometry.Index.H3, geometry.Index.H4, geometry.Index.G3),
		(True, geometry.Index.A7, geometry.Index.A6, geometry.Index.A5, geometry.Index.B6),
		(True, geometry.Index.H7, geometry.Index.H6, geometry.Index.H5, geometry.Index.G6),
	)
	penultimate = (
		(False, geometry.Index.E7, geometry.Index.E8, geometry.Index.D8),
		(True, geometry.Index.E2, geometry.Index.E1, geometry.Index.D1),
	)
	terminal = ((False, geometry.Index.A8), (True, geometry.Index.A1))
	en_passant = (
		(False, "k7/8/8/r4pPK/8/8/8/8", geometry.Index.G5, geometry.Index.F5, geometry.Index.F6, geometry.Index.A5),
		(True, "8/8/8/8/R4Ppk/8/8/K7", geometry.Index.G4, geometry.Index.F4, geometry.Index.F3, geometry.Index.A4),
	)

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_forward_moves(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		assert self.targets(pawn) == {single: algebra.Move, double: algebra.Rush}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	def test_moved_pawn_has_no_double_step(self, color, source, single, double, diagonals) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		pawn.moved = True
		assert self.targets(pawn) == {single: algebra.Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_forward_square_blocks_both_steps(self, color, source, single, double, diagonals, friendly) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Pawn, single, pawn.color if friendly else not pawn.color)
		assert pawn.targets == structs.collection()

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_occupied_double_destination_preserves_single_step(self, color, source, single, double, diagonals, friendly) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Pawn, double, pawn.color if friendly else not pawn.color)
		assert self.targets(pawn) == {single: algebra.Move}

	@pytest.mark.parametrize("color, source, single, double, diagonals", cases)
	@pytest.mark.parametrize("friendly", (True, False))
	@pytest.mark.parametrize("direction", (0, 1))
	def test_diagonal_capture(self, color, source, single, double, diagonals, friendly, direction) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		target = diagonals[direction]
		self.place(position, material.Pawn, target, pawn.color if friendly else not pawn.color)
		expected = {single: algebra.Move, double: algebra.Rush}

		if not friendly:
			expected[target] = algebra.Capt

		assert self.targets(pawn) == expected

	@pytest.mark.parametrize("color, source, single, double, capture", edges)
	def test_edge_keeps_inward_capture(self, color, source, single, double, capture) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: algebra.Move, double: algebra.Rush, capture: algebra.Capt}

	@pytest.mark.parametrize("color, source, single, capture", penultimate)
	def test_final_step_keeps_capture_after_double_step_leaves_board(self, color, source, single, capture) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Pawn, capture, not pawn.color)
		assert self.targets(pawn) == {single: algebra.Move, capture: algebra.Capt}

	@pytest.mark.parametrize("color, source", terminal)
	def test_terminal_rank_has_no_targets(self, color, source) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		assert pawn.targets == structs.collection()

	@pytest.mark.parametrize("color, placement, source, middle, target, attacker", en_passant)
	@pytest.mark.parametrize("attacked", (False, True))
	def test_en_passant_king_safety_removes_both_pawns(self, color, placement, source,
		middle, target, attacker, attacked,
	) -> None:
		position = engine.Position(placement)
		pawn = position[source]
		assert isinstance(pawn, material.Pawn)
		victim = position[middle]
		assert isinstance(victim, material.Pawn)
		ghost = material.Ghost(victim)
		position[target] = ghost

		if not attacked:
			del position[attacker]

		king = pawn.side.king
		assert king is not None and king.safe
		before = tuple(position), frozenset(position.white), frozenset(position.black)
		assert self.targets(pawn)[target] is algebra.EnPassant
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
		position = engine.Position(placement)
		pawn = position[source]
		assert isinstance(pawn, material.Pawn)
		victim = position[middle]
		assert isinstance(victim, material.Pawn)
		position[target] = material.Ghost(victim)
		del position[middle]
		assert target not in self.targets(pawn)
		assert target not in pawn.squares
