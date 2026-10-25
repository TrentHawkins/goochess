from __future__ import annotations


import pickle

import pytest

from goochess.algebra import Capt, Check, Checkmate, EnPassant, Move, Promotion, PromotionCapt, PromotionMove, Rush
from goochess.engine import Position
from goochess.geometry import Index
from goochess.material import Ghost, Knight, Officer, Pawn, Piece


class AlgebraSetup:

	colors = (False, True)
	choices = tuple(Officer)
	quiet_cases = (
		(False, Index.A7, Index.A8, "a8"),
		(True, Index.H2, Index.H1, "h1"),
	)
	capture_cases = (
		(False, Index.B7, Index.A8, "bxa8"),
		(True, Index.G2, Index.H1, "gxh1"),
	)
	other_ranks = (
		(False, Index.A6, Index.A7),
		(True, Index.H3, Index.H2),
		(False, Index.A2, Index.A1),
		(True, Index.H7, Index.H8),
	)

	@staticmethod
	def position() -> Position:
		return Position("8/8/8/8/8/8/8/8")

	@staticmethod
	def place[T: Piece](position: Position, kind: type[T], square: Index,
		color: bool,
	) -> T:
		piece = kind(color)
		position[square] = piece

		return piece

	@staticmethod
	def state(position: Position):
		pieces = position.white | position.black

		return (
			tuple(position), frozenset(position.white), frozenset(position.black),
			frozenset((piece, piece.index, piece.moved) for piece in pieces),
		)


class TestMove(AlgebraSetup):

	notations = (
		(Pawn, False, Index.E2, Index.E3, "e3"),
		(Pawn, True, Index.E7, Index.E6, "e6"),
		(Knight, False, Index.B1, Index.C3, "Nc3"),
		(Knight, True, Index.B8, Index.C6, "Nc6"),
	)
	invalid_targets = (-1, 64)
	moved_states = (False, True)
	changed_sources = (None, Index.E3)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_source_target_and_notation(self, kind, color, source, target, notation) -> None:
		piece = self.place(self.position(), kind, source, color)
		move = Move(target, piece)
		assert move.piece is piece
		assert move.source is source
		assert move.target is target
		assert move.other is None
		assert repr(move) == notation
		assert bool(move)

	def test_requires_placed_piece(self) -> None:
		piece = Pawn(False)

		with pytest.raises(AssertionError):
			Move(Index.E3, piece)

	@pytest.mark.parametrize("target", invalid_targets)
	def test_target_bounds(self, target) -> None:
		piece = self.place(self.position(), Pawn, Index.E2, False)

		with pytest.raises(ValueError):
			Move(target, piece)

	def test_source_is_snapshot(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E4, piece)
		del position[Index.E2]
		position[Index.E3] = piece
		assert piece.index is Index.E3
		assert move.source is Index.E2

	def test_destination_occupancy_is_live(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E3, piece)
		assert bool(move)
		self.place(position, Knight, Index.E3, not piece.color)
		assert not move
		assert move.other is None
		del position[Index.E3]
		assert bool(move)

	def test_equality_and_hash_use_target(self) -> None:
		position = self.position()
		first = self.place(position, Pawn, Index.E2, False)
		second = self.place(position, Knight, Index.F6, not first.color)
		move = Move(Index.E4, first)
		capture = Capt(Index.E4, second)
		assert move == capture == Index.E4
		assert hash(move) == hash(capture) == hash(Index.E4)
		assert len({move, capture}) == 1
		assert move != Move(Index.E3, first)

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_execution_updates_placement_and_moved_flag(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, color)
		piece.moved = moved
		move = Move(Index.E3, piece)
		assert move() is move
		assert position[move.source] is None
		assert position[move.target] is piece
		assert piece.index is move.target
		assert piece in piece.side
		assert piece.moved
		assert move.source is Index.E2
		assert move.other is None

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_context_restores_placement_without_changing_moved_flag(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, color)
		piece.moved = moved
		move = Move(Index.E3, piece)
		before = self.state(position)

		with move as active:
			assert active is move
			assert position[move.source] is None
			assert position[move.target] is piece
			assert piece.index is move.target
			assert piece in piece.side
			assert piece.moved is moved

		assert self.state(position) == before

	def test_context_restores_after_exception(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E3, piece)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with move as active:
				assert active is move
				assert piece.index is move.target

				raise LookupError("simulation failed")

		assert self.state(position) == before

	def test_context_cannot_overlap_itself(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E3, piece)
		before = self.state(position)

		with move:
			active = self.state(position)

			with pytest.raises(AssertionError):
				with move:
					...

			assert self.state(position) == active

		assert self.state(position) == before

	@pytest.mark.parametrize("source", changed_sources)
	def test_rejects_changed_source_without_mutation(self, source) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E4, piece)
		del position[move.source]

		if source is not None:
			position[source] = piece

		before = self.state(position)

		with pytest.raises(AssertionError):
			with move:
				...

		assert self.state(position) == before
		assert piece.index is source
		assert not piece.moved

	def test_rejects_changed_destination_without_mutation(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E2, False)
		move = Move(Index.E3, piece)
		self.place(position, Knight, move.target, True)
		before = self.state(position)

		with pytest.raises(AssertionError):
			with move:
				...

		assert self.state(position) == before
		assert move.other is None


class TestCapt(AlgebraSetup):

	notations = (
		(Pawn, False, Index.E4, Index.D5, "exd5"),
		(Pawn, True, Index.E5, Index.D4, "exd4"),
		(Knight, False, Index.B1, Index.C3, "Nxc3"),
		(Knight, True, Index.B8, Index.C6, "Nxc6"),
	)
	moved_states = (False, True)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_enemy_capture_and_notation(self, kind, color, source, target, notation) -> None:
		position = self.position()
		piece = self.place(position, kind, source, color)
		enemy = self.place(position, Knight, target, not piece.color)
		capture = Capt(target, piece)
		assert bool(capture)
		assert capture.piece is piece
		assert capture.source is source
		assert capture.target is target
		assert capture.other is enemy
		assert repr(capture) == notation

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	def test_requires_enemy_and_preserves_other_snapshot(self, color) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E4, color)
		enemy = self.place(position, Knight, Index.D5, not piece.color)
		assert enemy.color is not piece.color
		capture = Capt(Index.D5, piece)
		assert bool(capture)
		del position[Index.D5]
		assert not capture
		friendly = self.place(position, Knight, Index.D5, piece.color)
		assert friendly.color is piece.color
		assert not capture
		self.place(position, Knight, Index.D5, not piece.color)
		assert bool(capture)
		assert capture.other is enemy

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_capture_context_is_reusable(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E4, color)
		piece.moved = moved
		enemy = self.place(position, Knight, Index.D5, not color)
		capture = Capt(Index.D5, piece)
		before = self.state(position)

		for _ in range(2):
			with capture as active:
				assert active is capture
				assert position[capture.source] is None
				assert position[capture.target] is piece
				assert piece.index is capture.target
				assert piece.moved is moved
				assert enemy.index is None
				assert enemy not in enemy.side
				assert capture.other is enemy

			assert self.state(position) == before
			assert capture.source is Index.E4
			assert capture.other is enemy

	def test_rejects_replacement_of_captured_piece(self) -> None:
		position = self.position()
		piece = self.place(position, Pawn, Index.E4, False)
		enemy = self.place(position, Knight, Index.D5, True)
		capture = Capt(Index.D5, piece)
		self.place(position, Knight, capture.target, True)
		before = self.state(position)

		with pytest.raises(AssertionError):
			with capture:
				...

		assert self.state(position) == before
		assert capture.other is enemy


class TestRush(AlgebraSetup):

	cases = (
		(False, Index.A2, Index.A3, Index.A4),
		(True, Index.H7, Index.H6, Index.H5),
	)
	states = tuple((moved, middle, target) for moved in (False, True) for middle in (False, True) for target in (False, True))

	@pytest.mark.parametrize("color, source, middle, target", cases)
	@pytest.mark.parametrize("moved, middle_occupied, target_occupied", states)
	def test_requires_unmoved_piece_and_clear_path(self, color, source, middle, target,
		moved, middle_occupied, target_occupied,
	) -> None:
		position = self.position()
		piece = self.place(position, Pawn, source, color)
		piece.moved = moved

		if middle_occupied:
			self.place(position, Knight, middle, not piece.color)

		if target_occupied:
			self.place(position, Knight, target, not piece.color)

		rush = Rush(target, piece)
		assert rush.middle is middle
		assert bool(rush) is (not moved and not middle_occupied and not target_occupied)


class TestCheck(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.position(), Knight, Index.B1, False)
		check = Check(Index.C3, piece)
		assert repr(check) == "Nc3+"
		assert check.source is Index.B1
		assert check.target is Index.C3
		assert bool(check)


class TestCheckmate(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.position(), Knight, Index.B1, False)
		checkmate = Checkmate(Index.C3, piece)
		assert repr(checkmate) == "Nc3#"
		assert checkmate.source is Index.B1
		assert checkmate.target is Index.C3
		assert bool(checkmate)


class TestPromotion(AlgebraSetup):

	variants = ((Move, PromotionMove), (Capt, PromotionCapt))
	unsupported = (Check, (2, 8))
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("base, expected", variants)
	def test_subscription_selects_named_variant(self, base, expected) -> None:
		assert Promotion[base] is expected
		assert Promotion[base] is Promotion[base]
		assert issubclass(expected, Promotion)
		assert issubclass(expected, base)

	@pytest.mark.parametrize("base, expected", variants)
	def test_named_variant_class_serialization(self, base, expected) -> None:
		for protocol in self.pickle_protocols:
			assert pickle.loads(pickle.dumps(Promotion[base], protocol = protocol)) is expected

	@pytest.mark.parametrize("item", unsupported)
	def test_unsupported_subscription(self, item) -> None:
		with pytest.raises(TypeError):
			_ = Promotion[item]

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	def test_validity_before_selection(self, color, source, target, notation) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		promotion = Promotion[Move](target, pawn)
		assert bool(promotion)
		assert promotion.source is source
		assert promotion.target is target
		assert promotion.piece is pawn

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_selected_choice(self, color, source, target, notation, choice) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		promotion.to = choice
		assert promotion.to is choice
		assert repr(promotion) == notation + "=" + choice.name
		assert bool(promotion)

	@pytest.mark.parametrize("color, source, target", AlgebraSetup.other_ranks)
	def test_requires_penultimate_source_rank(self, color, source, target) -> None:
		pawn = self.place(self.position(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		assert not promotion
		promotion.to = Officer.N
		assert not promotion

	def test_requires_pawn(self) -> None:
		knight = self.place(self.position(), Knight, Index.C7, False)
		promotion = Promotion(Index.A8, knight)
		assert not promotion

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_requires_empty_destination(self, color, source, target, notation, friendly) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Knight, target, pawn.color if friendly else not pawn.color)
		promotion = Promotion(target, pawn)
		promotion.to = Officer.N
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.position(), Pawn, Index.A7, False)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert bool(promotion)
		assert promotion.to is Officer.N
		assert repr(promotion) == "a8=N"
		assert promotion.to is Officer.N

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.position(), Pawn, Index.A7, False)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert promotion.to.value is Knight


class TestPromotionCapt(AlgebraSetup):

	CapturePromotion = Promotion[Capt]

	illegal_ranks = (
		(False, Index.B6, Index.A7),
		(True, Index.G3, Index.H2),
	)

	def test_choices_are_independent(self) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, Index.B7, False)
		self.place(position, Knight, Index.A8, not pawn.color)
		first = self.CapturePromotion(Index.A8, pawn)
		second = self.CapturePromotion(Index.A8, pawn)
		first.to = Officer.N
		second.to = Officer.Q
		assert repr(first) == "bxa8=N"
		assert repr(second) == "bxa8=Q"
		first.to = Officer.R
		assert repr(first) == "bxa8=R"
		assert second.to is Officer.Q
		assert bool(first) and bool(second)

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_capture_with_selected_choice(self, color, source, target, notation, choice) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		enemy = self.place(position, Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		promotion.to = choice
		assert bool(promotion)
		assert promotion.other is enemy
		assert repr(promotion) == notation + "=" + choice.name

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	def test_capture_requires_enemy(self, color, source, target, notation) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
		self.place(position, Knight, target, pawn.color)
		assert not promotion
		self.place(position, Knight, target, not pawn.color)
		assert bool(promotion)
		promotion.to = Officer.Q
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("color, source, target", illegal_ranks)
	def test_capture_requires_penultimate_source_rank(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion


class TestEnPassant(AlgebraSetup):

	valid_moves = (
		(False, Index.E5, Index.D5, Index.D6),
		(True, Index.E4, Index.D4, Index.D3),
	)
	other_ranks = (
		(False, Index.E1, Index.D2),
		(False, Index.E2, Index.D3),
		(False, Index.E4, Index.D5),
		(True, Index.E7, Index.D6),
		(True, Index.E6, Index.D5),
		(True, Index.E5, Index.D4),
	)
	occupants = (
		(None, False, False),
		(Ghost, True, False),
		(Pawn, False, False),
		(Knight, False, False),
		(Ghost, False, True),
	)
	victims = (
		(None, False, False),
		(Pawn, True, False),
		(Knight, False, False),
		(Pawn, False, True),
	)
	wrong_targets = (
		(False, Index.E5, Index.D5, Index.E6),
		(False, Index.E5, Index.D5, Index.C6),
		(False, Index.E5, Index.D5, Index.D7),
		(True, Index.E4, Index.D4, Index.E3),
		(True, Index.E4, Index.D4, Index.C3),
		(True, Index.E4, Index.D4, Index.D2),
	)
	moved_states = (False, True)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_en_passant_rank(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		victim = self.place(position, Pawn, middle, not color)
		ghost = self.place(position, Ghost, target, not pawn.color)
		capture = EnPassant(target, pawn)
		assert bool(capture)
		assert capture.source is source
		assert capture.target is target
		assert capture.other is ghost
		assert capture.middle is middle
		assert capture.victim is victim

	@pytest.mark.parametrize("color, source, target", other_ranks)
	def test_requires_en_passant_rank(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Ghost, target, not pawn.color)
		assert not EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", occupants)
	def test_requires_enemy_ghost(self, color, source, middle, target, kind, friendly, expected) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, middle, not color)

		if kind is not None:
			self.place(position, kind, target, pawn.color if friendly else not pawn.color)

		assert bool(EnPassant(target, pawn)) is expected

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", victims)
	def test_requires_enemy_pawn_beside_source(self, color, source, middle, target, kind, friendly, expected) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Ghost, target, not color)

		if kind is not None:
			self.place(position, kind, middle, color if friendly else not color)

		assert bool(EnPassant(target, pawn)) is expected

	@pytest.mark.parametrize("color, source, middle, target", wrong_targets)
	def test_requires_one_forward_diagonal(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, middle, not color)
		self.place(position, Ghost, target, not color)
		assert not EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_requires_capturing_pawn(self, color, source, middle, target) -> None:
		position = self.position()
		knight = self.place(position, Knight, source, color)
		self.place(position, Pawn, middle, not color)
		self.place(position, Ghost, target, not color)
		assert not EnPassant(target, knight)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("moved", moved_states)
	def test_context_restores_all_three_squares_and_is_reusable(self, color, source, middle, target, moved) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		pawn.moved = moved
		victim = self.place(position, Pawn, middle, not color)
		victim.moved = True
		ghost = self.place(position, Ghost, target, not color)
		capture = EnPassant(target, pawn)
		before = self.state(position)

		for _ in range(2):
			with capture as active:
				assert active is capture
				assert position[source] is position[middle] is None
				assert position[target] is pawn
				assert pawn.index is target
				assert pawn.moved is moved
				assert victim.index is ghost.index is None
				assert victim not in position.side[not color]
				assert ghost not in position.side[not color]
				assert victim.moved

			assert self.state(position) == before
			assert capture.other is ghost
			assert capture.victim is victim

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_context_restores_after_exception(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		self.place(position, Pawn, middle, not color)
		self.place(position, Ghost, target, not color)
		capture = EnPassant(target, pawn)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with capture:
				assert position[middle] is None

				raise LookupError("simulation failed")

		assert self.state(position) == before

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_execution_removes_victim_and_ghost(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		victim = self.place(position, Pawn, middle, not color)
		ghost = self.place(position, Ghost, target, not color)
		capture = EnPassant(target, pawn)
		assert capture() is capture
		assert position[source] is position[middle] is None
		assert position[target] is pawn
		assert pawn.index is target
		assert pawn in position.side[color]
		assert pawn.moved
		assert victim.index is ghost.index is None
		assert victim not in position.side[not color]
		assert ghost not in position.side[not color]

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_live_victim_validation_and_snapshot_guard(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, Pawn, source, color)
		victim = self.place(position, Pawn, middle, not color)
		self.place(position, Ghost, target, not color)
		capture = EnPassant(target, pawn)
		del position[middle]
		assert not capture
		self.place(position, Pawn, middle, not color)
		assert bool(capture)
		assert capture.victim is victim
		before = self.state(position)

		with pytest.raises(AssertionError):
			with capture:
				...

		assert self.state(position) == before
