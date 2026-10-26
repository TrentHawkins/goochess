from __future__ import annotations


import pickle
import typing

import pytest

from goochess import algebra
from goochess import engine
from goochess import geometry
from goochess import material


class AlgebraSetup:

	colors = (False, True)
	choices = tuple(material.Officer)
	quiet_cases = (
		(False, geometry.Index.A7, geometry.Index.A8, "a8"),
		(True, geometry.Index.H2, geometry.Index.H1, "h1"),
	)
	capture_cases = (
		(False, geometry.Index.B7, geometry.Index.A8, "bxa8"),
		(True, geometry.Index.G2, geometry.Index.H1, "gxh1"),
	)
	other_ranks = (
		(False, geometry.Index.A6, geometry.Index.A7),
		(True, geometry.Index.H3, geometry.Index.H2),
		(False, geometry.Index.A2, geometry.Index.A1),
		(True, geometry.Index.H7, geometry.Index.H8),
	)

	@staticmethod
	def position() -> engine.Position:
		return engine.Position("8/8/8/8/8/8/8/8")

	@staticmethod
	def place[T: material.Piece](position: engine.Position, kind: type[T], square: geometry.Index,
		color: bool,
	) -> T:
		piece = kind(color)
		position[square] = piece

		return piece

	@staticmethod
	def place_ghost(position: engine.Position, square: geometry.Index, pawn: material.Pawn) -> material.Ghost:
		ghost = material.Ghost(pawn)
		position[square] = ghost

		return ghost

	@staticmethod
	def state(position: engine.Position):
		pieces = position.white | position.black

		return (
			tuple(position), frozenset(position.white), frozenset(position.black),
			frozenset((piece, piece.index, piece.moved) for piece in pieces),
		)


class TestMove(AlgebraSetup):

	class RecordedMove(algebra.Move):

		def __init__(self, target: int, piece: material.Piece) -> None:
			super().__init__(target, piece)
			self.events: list[str] = []

		def apply(self) -> typing.Self:
			self.events.append("apply")

			return super().apply()

		def undo(self, *, moved: bool) -> typing.Self:
			self.events.append("undo")

			return super().undo(moved = moved)

	notations = (
		(material.Pawn, False, geometry.Index.E2, geometry.Index.E3, "e3"),
		(material.Pawn, True, geometry.Index.E7, geometry.Index.E6, "e6"),
		(material.Knight, False, geometry.Index.B1, geometry.Index.C3, "Nc3"),
		(material.Knight, True, geometry.Index.B8, geometry.Index.C6, "Nc6"),
	)
	invalid_targets = (-1, 64)
	moved_states = (False, True)
	changed_sources = (None, geometry.Index.E3)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_source_target_and_notation(self, kind, color, source, target, notation) -> None:
		piece = self.place(self.position(), kind, source, color)
		move = algebra.Move(target, piece)
		assert move.piece is piece
		assert move.position is piece.position
		assert move.source is source
		assert move.target is target
		assert move.other is None
		assert repr(move) == notation
		assert bool(move)

	def test_requires_placed_piece(self) -> None:
		piece = material.Pawn(False)

		with pytest.raises(AssertionError):
			algebra.Move(geometry.Index.E3, piece)

	@pytest.mark.parametrize("target", invalid_targets)
	def test_target_bounds(self, target) -> None:
		piece = self.place(self.position(), material.Pawn, geometry.Index.E2, False)

		with pytest.raises(ValueError):
			algebra.Move(target, piece)

	def test_source_is_snapshot(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E4, piece)
		del position[geometry.Index.E2]
		position[geometry.Index.E3] = piece
		assert piece.index is geometry.Index.E3
		assert move.source is geometry.Index.E2

	def test_destination_occupancy_is_live(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E3, piece)
		assert bool(move)
		self.place(position, material.Knight, geometry.Index.E3, not piece.color)
		assert not move
		assert move.other is None
		del position[geometry.Index.E3]
		assert bool(move)

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("ghost_color", AlgebraSetup.colors)
	def test_ghost_is_transparent_and_restored(self, color, ghost_color) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, color)
		rusher = self.place(position, material.Pawn, geometry.Index.H5, ghost_color)
		ghost = self.place_ghost(position, geometry.Index.E3, rusher)
		move = algebra.Move(geometry.Index.E3, piece)
		before = self.state(position)
		assert bool(move)
		assert move.other is ghost

		with move.simulated:
			assert position[move.target] is piece
			assert ghost.index is None
			assert ghost not in ghost.side
			assert rusher.index is geometry.Index.H5

		assert self.state(position) == before
		assert position[move.target] is ghost
		assert move.other is ghost

	def test_equality_and_hash_use_target(self) -> None:
		position = self.position()
		first = self.place(position, material.Pawn, geometry.Index.E2, False)
		second = self.place(position, material.Knight, geometry.Index.F6, not first.color)
		move = algebra.Move(geometry.Index.E4, first)
		capture = algebra.Capt(geometry.Index.E4, second)
		assert move == capture == geometry.Index.E4
		assert hash(move) == hash(capture) == hash(geometry.Index.E4)
		assert len({move, capture}) == 1
		assert move != algebra.Move(geometry.Index.E3, first)

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_execution_updates_placement_and_moved_flag(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, color)
		piece.moved = moved
		move = algebra.Move(geometry.Index.E3, piece)
		assert move.apply() is move
		assert position[move.source] is None
		assert position[move.target] is piece
		assert piece.index is move.target
		assert piece in piece.side
		assert piece.moved
		assert move.source is geometry.Index.E2
		assert move.other is None

	@pytest.mark.parametrize("moved", moved_states)
	def test_apply_and_undo_hooks_restore_state(self, moved) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		piece.moved = moved
		move = self.RecordedMove(geometry.Index.E3, piece)
		before = self.state(position)
		assert move.apply() is move
		assert move.events == ["apply"]
		assert piece.index is move.target
		assert piece.moved
		assert move.undo(moved = moved) is move
		assert move.events == ["apply", "undo"]
		assert self.state(position) == before

	@pytest.mark.parametrize("moved", moved_states)
	def test_simulation_uses_hooks_once_and_restores_after_exception(self, moved) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		piece.moved = moved
		move = self.RecordedMove(geometry.Index.E3, piece)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with move.simulated as active:
				assert active is move
				assert move.events == ["apply"]
				assert piece.index is move.target
				assert piece.moved

				raise LookupError("simulation failed")

		assert move.events == ["apply", "undo"]
		assert self.state(position) == before

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_context_marks_moved_and_restores_flag(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, color)
		move = algebra.Move(geometry.Index.E3, piece)
		piece.moved = moved
		before = self.state(position)

		with move.simulated as active:
			assert active is move
			assert position[move.source] is None
			assert position[move.target] is piece
			assert piece.index is move.target
			assert piece in piece.side
			assert piece.moved

		assert self.state(position) == before

	def test_context_restores_after_exception(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E3, piece)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with move.simulated as active:
				assert active is move
				assert piece.index is move.target
				assert piece.moved

				raise LookupError("simulation failed")

		assert self.state(position) == before

	def test_context_cannot_overlap_itself(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E3, piece)
		before = self.state(position)

		with move.simulated:
			active = self.state(position)

			with pytest.raises(AssertionError):
				with move.simulated:
					...

			assert self.state(position) == active

		assert self.state(position) == before

	@pytest.mark.parametrize("source", changed_sources)
	def test_rejects_changed_source_without_mutation(self, source) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E4, piece)
		del position[move.source]

		if source is not None:
			position[source] = piece

		before = self.state(position)

		with pytest.raises(AssertionError):
			with move.simulated:
				...

		assert self.state(position) == before
		assert piece.index is source
		assert not piece.moved

	def test_rejects_changed_destination_without_mutation(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E2, False)
		move = algebra.Move(geometry.Index.E3, piece)
		self.place(position, material.Knight, move.target, True)
		before = self.state(position)

		with pytest.raises(AssertionError):
			with move.simulated:
				...

		assert self.state(position) == before
		assert move.other is None


class TestPawn(AlgebraSetup):

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	def test_accepts_placed_pawn_without_mutation(self, color) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, geometry.Index.E2, color)
		before = self.state(position)
		move = algebra.Pawn(geometry.Index.E3, pawn)
		assert move.piece is pawn
		assert move.source is geometry.Index.E2
		assert move.target is geometry.Index.E3
		assert self.state(position) == before

	def test_rejects_other_piece_without_mutation(self) -> None:
		position = self.position()
		knight = self.place(position, material.Knight, geometry.Index.B1, False)
		before = self.state(position)

		with pytest.raises(AssertionError):
			algebra.Pawn(geometry.Index.C3, knight)  # pyright: ignore[reportArgumentType]

		assert self.state(position) == before


class TestCapt(AlgebraSetup):

	notations = (
		(material.Pawn, False, geometry.Index.E4, geometry.Index.D5, "exd5"),
		(material.Pawn, True, geometry.Index.E5, geometry.Index.D4, "exd4"),
		(material.Knight, False, geometry.Index.B1, geometry.Index.C3, "Nxc3"),
		(material.Knight, True, geometry.Index.B8, geometry.Index.C6, "Nxc6"),
	)
	moved_states = (False, True)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_enemy_capture_and_notation(self, kind, color, source, target, notation) -> None:
		position = self.position()
		piece = self.place(position, kind, source, color)
		enemy = self.place(position, material.Knight, target, not piece.color)
		capture = algebra.Capt(target, piece)
		assert bool(capture)
		assert capture.piece is piece
		assert capture.source is source
		assert capture.target is target
		assert capture.other is enemy
		assert repr(capture) == notation

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	def test_requires_enemy_and_preserves_other_snapshot(self, color) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E4, color)
		enemy = self.place(position, material.Knight, geometry.Index.D5, not piece.color)
		assert enemy.color is not piece.color
		capture = algebra.Capt(geometry.Index.D5, piece)
		assert bool(capture)
		del position[geometry.Index.D5]
		assert not capture
		friendly = self.place(position, material.Knight, geometry.Index.D5, piece.color)
		assert friendly.color is piece.color
		assert not capture
		self.place(position, material.Knight, geometry.Index.D5, not piece.color)
		assert bool(capture)
		assert capture.other is enemy

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("ghost_color", AlgebraSetup.colors)
	def test_ghost_cannot_be_captured_normally(self, color, ghost_color) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E4, color)
		rusher = self.place(position, material.Pawn, geometry.Index.D4, ghost_color)
		ghost = self.place_ghost(position, geometry.Index.D5, rusher)
		capture = algebra.Capt(geometry.Index.D5, piece)
		before = self.state(position)
		assert not capture
		assert capture.other is ghost
		assert self.state(position) == before

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	@pytest.mark.parametrize("moved", moved_states)
	def test_capture_context_is_reusable(self, color, moved) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E4, color)
		piece.moved = moved
		enemy = self.place(position, material.Knight, geometry.Index.D5, not color)
		capture = algebra.Capt(geometry.Index.D5, piece)
		before = self.state(position)

		for _ in range(2):
			with capture.simulated as active:
				assert active is capture
				assert position[capture.source] is None
				assert position[capture.target] is piece
				assert piece.index is capture.target
				assert piece.moved
				assert enemy.index is None
				assert enemy not in enemy.side
				assert capture.other is enemy

			assert self.state(position) == before
			assert capture.source is geometry.Index.E4
			assert capture.other is enemy

	def test_rejects_replacement_of_captured_piece(self) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, geometry.Index.E4, False)
		enemy = self.place(position, material.Knight, geometry.Index.D5, True)
		capture = algebra.Capt(geometry.Index.D5, piece)
		self.place(position, material.Knight, capture.target, True)
		before = self.state(position)

		with pytest.raises(AssertionError):
			with capture.simulated:
				...

		assert self.state(position) == before
		assert capture.other is enemy


class TestRush(AlgebraSetup):

	cases = (
		(False, geometry.Index.A2, geometry.Index.A3, geometry.Index.A4),
		(True, geometry.Index.H7, geometry.Index.H6, geometry.Index.H5),
	)
	states = tuple((moved, middle, target) for moved in (False, True) for middle in (False, True) for target in (False, True))

	def test_requires_pawn_before_execution(self) -> None:
		position = self.position()
		knight = self.place(position, material.Knight, geometry.Index.E2, False)
		before = self.state(position)

		with pytest.raises(AssertionError):
			algebra.Rush(geometry.Index.E4, knight)  # pyright: ignore[reportArgumentType]

		assert self.state(position) == before

	@pytest.mark.parametrize("color, source, middle, target", cases)
	@pytest.mark.parametrize("moved, middle_occupied, target_occupied", states)
	def test_requires_unmoved_piece_and_clear_path(self, color, source, middle, target,
		moved, middle_occupied, target_occupied,
	) -> None:
		position = self.position()
		piece = self.place(position, material.Pawn, source, color)
		piece.moved = moved

		if middle_occupied:
			self.place(position, material.Knight, middle, not piece.color)

		if target_occupied:
			self.place(position, material.Knight, target, not piece.color)

		rush = algebra.Rush(target, piece)
		assert rush.middle is middle
		assert bool(rush) is (not moved and not middle_occupied and not target_occupied)

	@pytest.mark.parametrize("color, source, middle, target", cases)
	def test_simulation_creates_and_cleans_up_ghost(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		rush = algebra.Rush(target, pawn)
		before = self.state(position)

		for _ in range(2):
			with rush.simulated as active:
				assert active is rush
				assert position[source] is None
				assert position[target] is pawn
				assert pawn.index is target
				assert pawn.moved
				ghost = position[middle]
				assert isinstance(ghost, material.Ghost)
				assert ghost.rusher is pawn
				assert ghost.color is color
				assert ghost.index is middle
				assert ghost in pawn.side

			assert self.state(position) == before
			assert ghost.index is None
			assert ghost not in pawn.side

	@pytest.mark.parametrize("color, source, middle, target", cases)
	def test_simulation_cleans_up_ghost_after_exception(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		rush = algebra.Rush(target, pawn)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with rush.simulated:
				assert isinstance(position[middle], material.Ghost)

				raise LookupError("simulation failed")

		assert self.state(position) == before

	@pytest.mark.parametrize("color, source, middle, target", cases)
	def test_execution_keeps_ghost(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		rush = algebra.Rush(target, pawn)
		assert rush.apply() is rush
		assert position[source] is None
		assert position[target] is pawn
		assert pawn.index is target
		assert pawn.moved
		ghost = position[middle]
		assert isinstance(ghost, material.Ghost)
		assert ghost.rusher is pawn
		assert ghost.color is color
		assert ghost.index is middle
		assert ghost in pawn.side

	@pytest.mark.parametrize("color, source, middle, target", cases)
	def test_rejected_simulation_does_not_create_ghost(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		rush = algebra.Rush(target, pawn)
		self.place(position, material.Knight, target, not color)
		before = self.state(position)

		with pytest.raises(AssertionError):
			with rush.simulated:
				...

		assert self.state(position) == before
		assert position[middle] is None


class TestCheck(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.position(), material.Knight, geometry.Index.B1, False)
		check = algebra.Check(geometry.Index.C3, piece)
		assert repr(check) == "Nc3+"
		assert check.source is geometry.Index.B1
		assert check.target is geometry.Index.C3
		assert bool(check)


class TestCheckmate(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.position(), material.Knight, geometry.Index.B1, False)
		checkmate = algebra.Checkmate(geometry.Index.C3, piece)
		assert repr(checkmate) == "Nc3#"
		assert checkmate.source is geometry.Index.B1
		assert checkmate.target is geometry.Index.C3
		assert bool(checkmate)


class TestPromotion(AlgebraSetup):

	variants = ((algebra.Move, algebra.PromotionMove), (algebra.Capt, algebra.PromotionCapt))
	unsupported = (algebra.Check, (2, 8))
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("base, expected", variants)
	def test_subscription_selects_named_variant(self, base, expected) -> None:
		assert algebra.Promotion[base] is expected
		assert algebra.Promotion[base] is algebra.Promotion[base]
		assert issubclass(expected, algebra.Promotion)
		assert issubclass(expected, base)

	@pytest.mark.parametrize("base, expected", variants)
	def test_named_variant_class_serialization(self, base, expected) -> None:
		for protocol in self.pickle_protocols:
			assert pickle.loads(pickle.dumps(algebra.Promotion[base], protocol = protocol)) is expected

	@pytest.mark.parametrize("item", unsupported)
	def test_unsupported_subscription(self, item) -> None:
		with pytest.raises(TypeError):
			_ = algebra.Promotion[item]

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	def test_validity_before_selection(self, color, source, target, notation) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		promotion = algebra.Promotion[algebra.Move](target, pawn)
		assert bool(promotion)
		assert promotion.source is source
		assert promotion.target is target
		assert promotion.piece is pawn

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_selected_choice(self, color, source, target, notation, choice) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		promotion = algebra.Promotion(target, pawn)
		promotion.to = choice
		assert promotion.to is choice
		assert repr(promotion) == notation + "=" + choice.name
		assert bool(promotion)

	@pytest.mark.parametrize("color, source, target", AlgebraSetup.other_ranks)
	def test_requires_penultimate_source_rank(self, color, source, target) -> None:
		pawn = self.place(self.position(), material.Pawn, source, color)
		promotion = algebra.Promotion(target, pawn)
		assert not promotion
		promotion.to = material.Officer.N
		assert not promotion

	def test_requires_pawn(self) -> None:
		knight = self.place(self.position(), material.Knight, geometry.Index.C7, False)

		with pytest.raises(AssertionError):
			algebra.Promotion(geometry.Index.A8, knight)  # pyright: ignore[reportArgumentType]

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_requires_empty_destination(self, color, source, target, notation, friendly) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Knight, target, pawn.color if friendly else not pawn.color)
		promotion = algebra.Promotion(target, pawn)
		promotion.to = material.Officer.N
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.position(), material.Pawn, geometry.Index.A7, False)
		promotion = algebra.Promotion(geometry.Index.A8, pawn)
		promotion.to = material.Officer.N
		assert bool(promotion)
		assert promotion.to is material.Officer.N
		assert repr(promotion) == "a8=N"
		assert promotion.to is material.Officer.N

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.position(), material.Pawn, geometry.Index.A7, False)
		promotion = algebra.Promotion(geometry.Index.A8, pawn)
		promotion.to = material.Officer.N
		assert promotion.to.value is material.Knight


class TestPromotionCapt(AlgebraSetup):

	CapturePromotion = algebra.Promotion[algebra.Capt]

	illegal_ranks = (
		(False, geometry.Index.B6, geometry.Index.A7),
		(True, geometry.Index.G3, geometry.Index.H2),
	)

	def test_choices_are_independent(self) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, geometry.Index.B7, False)
		self.place(position, material.Knight, geometry.Index.A8, not pawn.color)
		first = self.CapturePromotion(geometry.Index.A8, pawn)
		second = self.CapturePromotion(geometry.Index.A8, pawn)
		first.to = material.Officer.N
		second.to = material.Officer.Q
		assert repr(first) == "bxa8=N"
		assert repr(second) == "bxa8=Q"
		first.to = material.Officer.R
		assert repr(first) == "bxa8=R"
		assert second.to is material.Officer.Q
		assert bool(first) and bool(second)

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_capture_with_selected_choice(self, color, source, target, notation, choice) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		enemy = self.place(position, material.Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		promotion.to = choice
		assert bool(promotion)
		assert promotion.other is enemy
		assert repr(promotion) == notation + "=" + choice.name

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	def test_capture_requires_enemy(self, color, source, target, notation) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
		self.place(position, material.Knight, target, pawn.color)
		assert not promotion
		self.place(position, material.Knight, target, not pawn.color)
		assert bool(promotion)
		promotion.to = material.Officer.Q
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("color, source, target", illegal_ranks)
	def test_capture_requires_penultimate_source_rank(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place(position, material.Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion


class TestEnPassant(AlgebraSetup):

	valid_moves = (
		(False, geometry.Index.E5, geometry.Index.D5, geometry.Index.D6),
		(True, geometry.Index.E4, geometry.Index.D4, geometry.Index.D3),
	)
	other_ranks = (
		(False, geometry.Index.E1, geometry.Index.D2),
		(False, geometry.Index.E2, geometry.Index.D3),
		(False, geometry.Index.E4, geometry.Index.D5),
		(True, geometry.Index.E7, geometry.Index.D6),
		(True, geometry.Index.E6, geometry.Index.D5),
		(True, geometry.Index.E5, geometry.Index.D4),
	)
	occupants = (
		(None, False, False),
		(material.Ghost, True, False),
		(material.Pawn, False, False),
		(material.Knight, False, False),
		(material.Ghost, False, True),
	)
	victims = (
		(None, False, False),
		(material.Pawn, True, False),
		(material.Knight, False, False),
		(material.Pawn, False, True),
	)
	wrong_targets = (
		(False, geometry.Index.E5, geometry.Index.D5, geometry.Index.E6),
		(False, geometry.Index.E5, geometry.Index.D5, geometry.Index.C6),
		(False, geometry.Index.E5, geometry.Index.D5, geometry.Index.D7),
		(True, geometry.Index.E4, geometry.Index.D4, geometry.Index.E3),
		(True, geometry.Index.E4, geometry.Index.D4, geometry.Index.C3),
		(True, geometry.Index.E4, geometry.Index.D4, geometry.Index.D2),
	)
	moved_states = (False, True)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_en_passant_rank(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		ghost = self.place_ghost(position, target, victim)
		capture = algebra.EnPassant(target, pawn)
		assert bool(capture)
		assert capture.source is source
		assert capture.target is target
		assert capture.other is ghost
		assert capture.middle is middle
		assert capture.other.rusher is victim

	@pytest.mark.parametrize("color, source, target", other_ranks)
	def test_requires_en_passant_rank(self, color, source, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		self.place_ghost(position, target, material.Pawn(not pawn.color))
		assert not algebra.EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", occupants)
	def test_requires_enemy_ghost(self, color, source, middle, target, kind, friendly, expected) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)

		if kind is material.Ghost:
			self.place_ghost(position, target, material.Pawn(pawn.color) if friendly else victim)

		elif kind is not None:
			self.place(position, kind, target, pawn.color if friendly else not pawn.color)

		if kind is material.Ghost:
			assert bool(algebra.EnPassant(target, pawn)) is expected

		else:
			with pytest.raises(AssertionError):
				algebra.EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", victims)
	def test_requires_enemy_pawn_beside_source(self, color, source, middle, target, kind, friendly, expected) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = None

		if kind is not None:
			victim = self.place(position, kind, middle, color if friendly else not color)

		self.place_ghost(position, target, victim if isinstance(victim, material.Pawn) and not friendly else material.Pawn(not color))

		assert bool(algebra.EnPassant(target, pawn)) is expected

	@pytest.mark.parametrize("color, source, middle, target", wrong_targets)
	def test_requires_one_forward_diagonal(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		self.place_ghost(position, target, victim)
		assert not algebra.EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_requires_capturing_pawn(self, color, source, middle, target) -> None:
		position = self.position()
		knight = self.place(position, material.Knight, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		self.place_ghost(position, target, victim)

		with pytest.raises(AssertionError):
			algebra.EnPassant(target, knight)  # pyright: ignore[reportArgumentType]

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	@pytest.mark.parametrize("moved", moved_states)
	def test_context_restores_all_three_squares_and_is_reusable(self, color, source, middle, target, moved) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		pawn.moved = moved
		victim = self.place(position, material.Pawn, middle, not color)
		victim.moved = True
		ghost = self.place_ghost(position, target, victim)
		capture = algebra.EnPassant(target, pawn)
		before = self.state(position)

		for _ in range(2):
			with capture.simulated as active:
				assert active is capture
				assert position[source] is position[middle] is None
				assert position[target] is pawn
				assert pawn.index is target
				assert pawn.moved
				assert victim.index is ghost.index is None
				assert victim not in position.side[not color]
				assert ghost not in position.side[not color]
				assert victim.moved

			assert self.state(position) == before
			assert capture.other is ghost
			assert capture.other.rusher is victim

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_context_restores_after_exception(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		self.place_ghost(position, target, victim)
		capture = algebra.EnPassant(target, pawn)
		before = self.state(position)

		with pytest.raises(LookupError, match = "simulation failed"):
			with capture.simulated:
				assert position[middle] is None

				raise LookupError("simulation failed")

		assert self.state(position) == before

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_execution_removes_victim_and_ghost(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		ghost = self.place_ghost(position, target, victim)
		capture = algebra.EnPassant(target, pawn)
		assert capture.apply() is capture
		assert position[source] is position[middle] is None
		assert position[target] is pawn
		assert pawn.index is target
		assert pawn in position.side[color]
		assert pawn.moved
		assert victim.index is ghost.index is None
		assert victim not in position.side[not color]
		assert ghost not in position.side[not color]

	@pytest.mark.parametrize("color, source, middle, target", valid_moves)
	def test_requires_linked_rusher_beside_source(self, color, source, middle, target) -> None:
		position = self.position()
		pawn = self.place(position, material.Pawn, source, color)
		victim = self.place(position, material.Pawn, middle, not color)
		self.place_ghost(position, target, victim)
		capture = algebra.EnPassant(target, pawn)
		del position[middle]
		assert not capture
		self.place(position, material.Pawn, middle, not color)
		assert not capture
		assert capture.other.rusher is victim
		before = self.state(position)

		with pytest.raises(AssertionError):
			with capture.simulated:
				...

		assert self.state(position) == before
