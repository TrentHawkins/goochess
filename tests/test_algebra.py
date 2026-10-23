from __future__ import annotations


import pickle

import pytest

from goochess.algebra import Capt, Check, Checkmate, EnPassant, Move, Promotion, PromotionCapt, PromotionMove, Rush
from goochess.engine import Game
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
	def game() -> Game:
		return Game("8/8/8/8/8/8/8/8")

	@staticmethod
	def place[T: Piece](game: Game, kind: type[T], square: Index,
		color: bool,
	) -> T:
		piece = kind(color)
		game[square] = piece

		return piece


class TestMove(AlgebraSetup):

	notations = (
		(Pawn, False, Index.E2, Index.E3, "e3"),
		(Pawn, True, Index.E7, Index.E6, "e6"),
		(Knight, False, Index.B1, Index.C3, "Nc3"),
		(Knight, True, Index.B8, Index.C6, "Nc6"),
	)
	invalid_targets = (-1, 64)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_source_target_and_notation(self, kind, color, source, target, notation) -> None:
		piece = self.place(self.game(), kind, source, color)
		move = Move(target, piece)
		assert move.piece is piece
		assert move.source is source
		assert move.target is target
		assert move.other is None
		assert repr(move) == notation
		assert bool(move)

	def test_requires_placed_piece(self) -> None:
		piece = Pawn(False)

		with pytest.raises(ValueError, match = "valid index"):
			Move(Index.E3, piece)

	@pytest.mark.parametrize("target", invalid_targets)
	def test_target_bounds(self, target) -> None:
		piece = self.place(self.game(), Pawn, Index.E2, False)

		with pytest.raises(ValueError):
			Move(target, piece)

	def test_source_is_snapshot(self) -> None:
		game = self.game()
		piece = self.place(game, Pawn, Index.E2, False)
		move = Move(Index.E4, piece)
		del game[Index.E2]
		game[Index.E3] = piece
		assert piece.index is Index.E3
		assert move.source is Index.E2

	def test_destination_occupancy_is_live(self) -> None:
		game = self.game()
		piece = self.place(game, Pawn, Index.E2, False)
		move = Move(Index.E3, piece)
		assert bool(move)
		self.place(game, Knight, Index.E3, not piece.color)
		assert not move
		assert move.other is None
		del game[Index.E3]
		assert bool(move)

	def test_equality_and_hash_use_target(self) -> None:
		game = self.game()
		first = self.place(game, Pawn, Index.E2, False)
		second = self.place(game, Knight, Index.F6, not first.color)
		move = Move(Index.E4, first)
		capture = Capt(Index.E4, second)
		assert move == capture == Index.E4
		assert hash(move) == hash(capture) == hash(Index.E4)
		assert len({move, capture}) == 1
		assert move != Move(Index.E3, first)


class TestCapt(AlgebraSetup):

	notations = (
		(Pawn, False, Index.E4, Index.D5, "exd5"),
		(Pawn, True, Index.E5, Index.D4, "exd4"),
		(Knight, False, Index.B1, Index.C3, "Nxc3"),
		(Knight, True, Index.B8, Index.C6, "Nxc6"),
	)

	@pytest.mark.parametrize("kind, color, source, target, notation", notations)
	def test_enemy_capture_and_notation(self, kind, color, source, target, notation) -> None:
		game = self.game()
		piece = self.place(game, kind, source, color)
		enemy = self.place(game, Knight, target, not piece.color)
		capture = Capt(target, piece)
		assert bool(capture)
		assert capture.piece is piece
		assert capture.source is source
		assert capture.target is target
		assert capture.other is enemy
		assert repr(capture) == notation

	@pytest.mark.parametrize("color", AlgebraSetup.colors)
	def test_requires_enemy_and_preserves_other_snapshot(self, color) -> None:
		game = self.game()
		piece = self.place(game, Pawn, Index.E4, color)
		enemy = self.place(game, Knight, Index.D5, not piece.color)
		assert enemy.color is not piece.color
		capture = Capt(Index.D5, piece)
		assert bool(capture)
		del game[Index.D5]
		assert not capture
		friendly = self.place(game, Knight, Index.D5, piece.color)
		assert friendly.color is piece.color
		assert not capture
		self.place(game, Knight, Index.D5, not piece.color)
		assert bool(capture)
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
		game = self.game()
		piece = self.place(game, Pawn, source, color)
		piece.moved = moved

		if middle_occupied:
			self.place(game, Knight, middle, not piece.color)

		if target_occupied:
			self.place(game, Knight, target, not piece.color)

		rush = Rush(target, piece)
		assert rush.middle is middle
		assert bool(rush) is (not moved and not middle_occupied and not target_occupied)


class TestCheck(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.game(), Knight, Index.B1, False)
		check = Check(Index.C3, piece)
		assert repr(check) == "Nc3+"
		assert check.source is Index.B1
		assert check.target is Index.C3
		assert bool(check)


class TestCheckmate(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.game(), Knight, Index.B1, False)
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
		pawn = self.place(self.game(), Pawn, source, color)
		promotion = Promotion[Move](target, pawn)
		assert bool(promotion)
		assert promotion.source is source
		assert promotion.target is target
		assert promotion.piece is pawn

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_selected_choice(self, color, source, target, notation, choice) -> None:
		pawn = self.place(self.game(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		promotion.to = choice
		assert promotion.to is choice
		assert repr(promotion) == notation + "=" + choice.name
		assert bool(promotion)

	@pytest.mark.parametrize("color, source, target", AlgebraSetup.other_ranks)
	def test_requires_penultimate_source_rank(self, color, source, target) -> None:
		pawn = self.place(self.game(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		assert not promotion
		promotion.to = Officer.N
		assert not promotion

	def test_requires_pawn(self) -> None:
		knight = self.place(self.game(), Knight, Index.C7, False)
		promotion = Promotion(Index.A8, knight)
		assert not promotion

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_requires_empty_destination(self, color, source, target, notation, friendly) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Knight, target, pawn.color if friendly else not pawn.color)
		promotion = Promotion(target, pawn)
		promotion.to = Officer.N
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.game(), Pawn, Index.A7, False)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert bool(promotion)
		assert promotion.to is Officer.N
		assert repr(promotion) == "a8=N"
		assert promotion.to is Officer.N

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.game(), Pawn, Index.A7, False)
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
		game = self.game()
		pawn = self.place(game, Pawn, Index.B7, False)
		self.place(game, Knight, Index.A8, not pawn.color)
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
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		enemy = self.place(game, Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		promotion.to = choice
		assert bool(promotion)
		assert promotion.other is enemy
		assert repr(promotion) == notation + "=" + choice.name

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	def test_capture_requires_enemy(self, color, source, target, notation) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
		self.place(game, Knight, target, pawn.color)
		assert not promotion
		self.place(game, Knight, target, not pawn.color)
		assert bool(promotion)
		promotion.to = Officer.Q
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("color, source, target", illegal_ranks)
	def test_capture_requires_penultimate_source_rank(self, color, source, target) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Knight, target, not pawn.color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion


class TestEnPassant(AlgebraSetup):

	valid_moves = (
		(False, Index.E5, Index.D6),
		(True, Index.E4, Index.D3),
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

	@pytest.mark.parametrize("color, source, target", valid_moves)
	def test_en_passant_rank(self, color, source, target) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		ghost = self.place(game, Ghost, target, not pawn.color)
		capture = EnPassant(target, pawn)
		assert bool(capture)
		assert capture.source is source
		assert capture.target is target
		assert capture.other is ghost

	@pytest.mark.parametrize("color, source, target", other_ranks)
	def test_requires_en_passant_rank(self, color, source, target) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Ghost, target, not pawn.color)
		assert not EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", occupants)
	def test_requires_enemy_ghost(self, color, source, target, kind, friendly, expected) -> None:
		game = self.game()
		pawn = self.place(game, Pawn, source, color)

		if kind is not None:
			self.place(game, kind, target, pawn.color if friendly else not pawn.color)

		assert bool(EnPassant(target, pawn)) is expected
