from __future__ import annotations


import pytest

from goochess.algebra import Capt, Promotion
from goochess.engine import Game
from goochess.geometry import Color, Index
from goochess.material import Knight, Officer, Pawn, Piece


class AlgebraSetup:

	choices = ("Q", "R", "N", "B")
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
		game = Game("")
		list.extend(game, [None] * 64)

		return game

	@staticmethod
	def place(game: Game, kind: type[Piece], square: Index,
		color: Color,
	) -> Piece:
		side = game.white if color is Color.WHITE else game.black
		piece = kind(side)
		game[square] = piece
		side.add(piece)

		return piece

	@staticmethod
	def opponent(color: Color) -> Color:
		return Color.BLACK if color is Color.WHITE else Color.WHITE


class TestPromotion(AlgebraSetup):

	@pytest.mark.parametrize("color, source, target, notation", AlgebraSetup.quiet_cases)
	def test_default_choice(self, color, source, target, notation) -> None:
		pawn = self.place(self.board(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		assert promotion.to == "Q"
		assert repr(promotion) == notation + "=Q"
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
		assert promotion.to == choice
		assert repr(promotion) == notation + "=" + choice
		assert bool(promotion)

	@pytest.mark.parametrize("color, source, target", AlgebraSetup.other_ranks)
	def test_requires_final_rank_for_color(self, color, source, target) -> None:
		pawn = self.place(self.board(), Pawn, source, color)
		promotion = Promotion(target, pawn)
		assert not promotion
		promotion.to = "N"
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
		promotion.to = "N"
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, Color.WHITE)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = "N"
		assert bool(promotion)
		assert promotion.to == "N"
		assert repr(promotion) == "a8=N"
		assert promotion.to == "N"

	def test_choices_are_independent(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, Color.WHITE)
		first = Promotion(Index.A8, pawn)
		second = Promotion(Index.A8, pawn)
		first.to = "N"
		assert first.to == "N"
		assert second.to == "Q"
		third = Promotion(Index.A8, pawn)
		assert third.to == "Q"

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, Color.WHITE)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = "N"
		assert Officer[promotion.to].value is Knight


class TestCapturePromotion(AlgebraSetup):

	class CapturePromotion(Promotion, Capt):
		...

	illegal_ranks = (
		(Color.WHITE, Index.B6, Index.A7),
		(Color.BLACK, Index.G3, Index.H2),
	)

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
		assert repr(promotion) == notation + "=" + choice

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
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("color, source, target", illegal_ranks)
	def test_capture_requires_final_rank(self, color, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, color)
		self.place(game, Knight, target, self.opponent(color))
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
