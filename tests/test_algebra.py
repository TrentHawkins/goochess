from __future__ import annotations


import pickle

import pytest

from goochess.algebra import Capt, Check, EnPassant, Move, Promotion, PromotionCapt, PromotionMove
from goochess.engine import Game
from goochess.geometry import Color, Index
from goochess.material import Ghost, Knight, Officer, Pawn, Piece


class AlgebraSetup:

	choices = tuple(Officer)
	quiet_cases = (
		(Color.WHITE, Index.A7, Index.A8, "a8"),
		(Color.BLACK, Index.H2, Index.H1, "h1"),
	)
	capture_cases = (
		(Color.WHITE, Index.B7, Index.A8, "bxa8"),
		(Color.BLACK, Index.G2, Index.H1, "gxh1"),
	)
	other_ranks = (
		(Color.WHITE, Index.A6, Index.A7),
		(Color.BLACK, Index.H3, Index.H2),
		(Color.WHITE, Index.A2, Index.A1),
		(Color.BLACK, Index.H7, Index.H8),
	)

	@staticmethod
	def board() -> Game:
		return Game("8/8/8/8/8/8/8/8")

	@staticmethod
	def place[T: Piece](game: Game, kind: type[T], square: Index,
		color: Color,
	) -> T:
		side = game.white if color is Color.WHITE else game.black
		piece = kind(side)
		game[square] = piece
		side.add(piece)

		return piece

	@staticmethod
	def opponent(color: Color) -> Color:
		return Color.BLACK if color is Color.WHITE else Color.WHITE


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
		pawn = self.place(self.board(), Pawn, source, color)
		promotion = Promotion[Move](target, pawn)
		assert bool(promotion)
		assert promotion.source is source
		assert promotion.target is target
		assert promotion.piece is pawn

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_selected_choice(self, color, source, target, notation, choice) -> None:
		pawn = self.place(self.board(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		promotion.to = choice
		assert promotion.to is choice
		assert repr(promotion) == notation + "=" + choice.name
		assert bool(promotion)

	@pytest.mark.parametrize("color, source, target", AlgebraSetup.other_ranks)
	def test_requires_penultimate_source_rank(self, color, source, target) -> None:
		pawn = self.place(self.board(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		assert not promotion
		promotion.to = Officer.N
		assert not promotion

	def test_requires_pawn(self) -> None:
		knight = self.place(self.board(), Knight, Index.C7, Color.WHITE)
		promotion = Promotion(Index.A8, knight)
		assert not promotion

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_requires_empty_destination(self, color, source, target, notation, friendly) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Knight, target, color if friendly else self.opponent(color))
		promotion = Promotion(target, pawn)
		promotion.to = Officer.N
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, Color.WHITE)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert bool(promotion)
		assert promotion.to is Officer.N
		assert repr(promotion) == "a8=N"
		assert promotion.to is Officer.N

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, Color.WHITE)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert promotion.to.value is Knight


class TestCapturePromotion(AlgebraSetup):

	CapturePromotion = Promotion[Capt]

	illegal_ranks = (
		(Color.WHITE, Index.B6, Index.A7),
		(Color.BLACK, Index.G3, Index.H2),
	)

	def test_choices_are_independent(self) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, Index.B7, Color.WHITE)
		self.place(game, Knight, Index.A8, Color.BLACK)
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
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		enemy = self.place(game, Knight, target, self.opponent(color))
		promotion = self.CapturePromotion(target, pawn)
		promotion.to = choice
		assert bool(promotion)
		assert promotion.other is enemy
		assert repr(promotion) == notation + "=" + choice.name

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.capture_cases)
	def test_capture_requires_enemy(self, color, source, target, notation) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
		self.place(game, Knight, target, color)
		assert not promotion
		self.place(game, Knight, target, self.opponent(color))
		assert bool(promotion)
		promotion.to = Officer.Q
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("color, source, target", illegal_ranks)
	def test_capture_requires_penultimate_source_rank(self, color, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Knight, target, self.opponent(color))
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion


class TestEnPassant(AlgebraSetup):

	valid_moves = (
		(Color.WHITE, Index.E5, Index.D6),
		(Color.BLACK, Index.E4, Index.D3),
	)
	other_ranks = (
		(Color.WHITE, Index.E1, Index.D2),
		(Color.WHITE, Index.E2, Index.D3),
		(Color.WHITE, Index.E4, Index.D5),
		(Color.BLACK, Index.E7, Index.D6),
		(Color.BLACK, Index.E6, Index.D5),
		(Color.BLACK, Index.E5, Index.D4),
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
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		ghost = self.place(game, Ghost, target, self.opponent(color))
		capture = EnPassant(target, pawn)
		assert bool(capture)
		assert capture.source is source
		assert capture.target is target
		assert capture.other is ghost

	@pytest.mark.parametrize("color, source, target", other_ranks)
	def test_requires_en_passant_rank(self, color, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Ghost, target, self.opponent(color))
		assert not EnPassant(target, pawn)

	@pytest.mark.parametrize("color, source, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", occupants)
	def test_requires_enemy_ghost(self, color, source, target, kind, friendly, expected) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)

		if kind is not None:
			self.place(game, kind, target, color if friendly else self.opponent(color))

		assert bool(EnPassant(target, pawn)) is expected
