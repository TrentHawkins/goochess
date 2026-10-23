from __future__ import annotations


import pickle

import pytest

from goochess.algebra import Capt, Check, Checkmate, EnPassant, Move, Promotion, PromotionCapt, PromotionMove, Rush
from goochess.engine import Board, Side
from goochess.geometry import Index
from goochess.material import Ghost, Knight, Officer, Pawn, Piece


class AlgebraSetup:

	whites = (True, False)
	choices = tuple(Officer)
	quiet_cases = (
		(True, Index.A7, Index.A8, "a8"),
		(False, Index.H2, Index.H1, "h1"),
	)
	capture_cases = (
		(True, Index.B7, Index.A8, "bxa8"),
		(False, Index.G2, Index.H1, "gxh1"),
	)
	other_ranks = (
		(True, Index.A6, Index.A7),
		(False, Index.H3, Index.H2),
		(True, Index.A2, Index.A1),
		(False, Index.H7, Index.H8),
	)

	@staticmethod
	def board() -> Board:
		return Board("8/8/8/8/8/8/8/8")

	@staticmethod
	def place[T: Piece](board: Board, kind: type[T], square: Index,
		side: Side | bool,
	) -> T:
		if isinstance(side, bool):
			side = board.white if side else board.black

		piece = kind(side)
		board[square] = piece

		return piece


class TestMove(AlgebraSetup):

	notations = (
		(Pawn, True, Index.E2, Index.E3, "e3"),
		(Pawn, False, Index.E7, Index.E6, "e6"),
		(Knight, True, Index.B1, Index.C3, "Nc3"),
		(Knight, False, Index.B8, Index.C6, "Nc6"),
	)
	invalid_targets = (-1, 64)

	@pytest.mark.parametrize("kind, white, source, target, notation", notations)
	def test_source_target_and_notation(self, kind, white, source, target, notation) -> None:
		piece = self.place(self.board(), kind, source, white)
		move = Move(target, piece)
		assert move.piece is piece
		assert move.source is source
		assert move.target is target
		assert move.other is None
		assert repr(move) == notation
		assert bool(move)

	def test_requires_placed_piece(self) -> None:
		piece = Pawn(self.board().white)

		with pytest.raises(ValueError, match = "valid index"):
			Move(Index.E3, piece)

	@pytest.mark.parametrize("target", invalid_targets)
	def test_target_bounds(self, target) -> None:
		piece = self.place(self.board(), Pawn, Index.E2, True)

		with pytest.raises(ValueError):
			Move(target, piece)

	def test_source_is_snapshot(self) -> None:
		game = self.board()
		piece = self.place(game, Pawn, Index.E2, True)
		move = Move(Index.E4, piece)
		del game[Index.E2]
		game[Index.E3] = piece
		assert piece.index is Index.E3
		assert move.source is Index.E2

	def test_destination_occupancy_is_live(self) -> None:
		game = self.board()
		piece = self.place(game, Pawn, Index.E2, True)
		move = Move(Index.E3, piece)
		assert bool(move)
		self.place(game, Knight, Index.E3, piece.side.other)
		assert not move
		assert move.other is None
		del game[Index.E3]
		assert bool(move)

	def test_equality_and_hash_use_target(self) -> None:
		board = self.board()
		first = self.place(board, Pawn, Index.E2, board.white)
		second = self.place(board, Knight, Index.F6, first.side.other)
		move = Move(Index.E4, first)
		capture = Capt(Index.E4, second)
		assert move == capture == Index.E4
		assert hash(move) == hash(capture) == hash(Index.E4)
		assert len({move, capture}) == 1
		assert move != Move(Index.E3, first)


class TestCapt(AlgebraSetup):

	notations = (
		(Pawn, True, Index.E4, Index.D5, "exd5"),
		(Pawn, False, Index.E5, Index.D4, "exd4"),
		(Knight, True, Index.B1, Index.C3, "Nxc3"),
		(Knight, False, Index.B8, Index.C6, "Nxc6"),
	)

	@pytest.mark.parametrize("kind, white, source, target, notation", notations)
	def test_enemy_capture_and_notation(self, kind, white, source, target, notation) -> None:
		game = self.board()
		piece = self.place(game, kind, source, white)
		enemy = self.place(game, Knight, target, piece.side.other)
		capture = Capt(target, piece)
		assert bool(capture)
		assert capture.piece is piece
		assert capture.source is source
		assert capture.target is target
		assert capture.other is enemy
		assert repr(capture) == notation

	@pytest.mark.parametrize("white", AlgebraSetup.whites)
	def test_requires_enemy_and_preserves_other_snapshot(self, white) -> None:
		game = self.board()
		piece = self.place(game, Pawn, Index.E4, white)
		enemy = self.place(game, Knight, Index.D5, piece.side.other)
		assert enemy.side is not piece.side
		capture = Capt(Index.D5, piece)
		assert bool(capture)
		del game[Index.D5]
		assert not capture
		friendly = self.place(game, Knight, Index.D5, piece.side)
		assert friendly.side is piece.side
		assert not capture
		self.place(game, Knight, Index.D5, piece.side.other)
		assert bool(capture)
		assert capture.other is enemy


class TestRush(AlgebraSetup):

	cases = (
		(True, Index.A2, Index.A3, Index.A4),
		(False, Index.H7, Index.H6, Index.H5),
	)
	states = tuple((moved, middle, target) for moved in (False, True) for middle in (False, True) for target in (False, True))

	@pytest.mark.parametrize("white, source, middle, target", cases)
	@pytest.mark.parametrize("moved, middle_occupied, target_occupied", states)
	def test_requires_unmoved_piece_and_clear_path(self, white, source, middle, target,
		moved, middle_occupied, target_occupied,
	) -> None:
		game = self.board()
		piece = self.place(game, Pawn, source, white)
		piece.moved = moved

		if middle_occupied:
			self.place(game, Knight, middle, piece.side.other)

		if target_occupied:
			self.place(game, Knight, target, piece.side.other)

		rush = Rush(target, piece)
		assert rush.middle is middle
		assert bool(rush) is (not moved and not middle_occupied and not target_occupied)


class TestCheck(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.board(), Knight, Index.B1, True)
		check = Check(Index.C3, piece)
		assert repr(check) == "Nc3+"
		assert check.source is Index.B1
		assert check.target is Index.C3
		assert bool(check)


class TestCheckmate(AlgebraSetup):

	def test_notation(self) -> None:
		piece = self.place(self.board(), Knight, Index.B1, True)
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

	@pytest.mark.parametrize("white, source, target, notation", AlgebraSetup.quiet_cases)
	def test_validity_before_selection(self, white, source, target, notation) -> None:
		pawn = self.place(self.board(), Pawn, source, white)
		promotion = Promotion[Move](target, pawn)
		assert bool(promotion)
		assert promotion.source is source
		assert promotion.target is target
		assert promotion.piece is pawn

	@pytest.mark.parametrize("white, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_selected_choice(self, white, source, target, notation, choice) -> None:
		pawn = self.place(self.board(), Pawn, source, white)
		promotion = Promotion(target, pawn)
		promotion.to = choice
		assert promotion.to is choice
		assert repr(promotion) == notation + "=" + choice.name
		assert bool(promotion)

	@pytest.mark.parametrize("white, source, target", AlgebraSetup.other_ranks)
	def test_requires_penultimate_source_rank(self, white, source, target) -> None:
		pawn = self.place(self.board(), Pawn, source, white)
		promotion = Promotion(target, pawn)
		assert not promotion
		promotion.to = Officer.N
		assert not promotion

	def test_requires_pawn(self) -> None:
		knight = self.place(self.board(), Knight, Index.C7, True)
		promotion = Promotion(Index.A8, knight)
		assert not promotion

	@pytest.mark.parametrize("white, source, target, notation", AlgebraSetup.quiet_cases)
	@pytest.mark.parametrize("friendly", (True, False))
	def test_requires_empty_destination(self, white, source, target, notation, friendly) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		self.place(game, Knight, target, pawn.side if friendly else pawn.side.other)
		promotion = Promotion(target, pawn)
		promotion.to = Officer.N
		assert not promotion
		assert repr(promotion) == notation + "=N"

	def test_reading_preserves_choice(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, True)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert bool(promotion)
		assert promotion.to is Officer.N
		assert repr(promotion) == "a8=N"
		assert promotion.to is Officer.N

	def test_choice_resolves_to_officer(self) -> None:
		pawn = self.place(self.board(), Pawn, Index.A7, True)
		promotion = Promotion(Index.A8, pawn)
		promotion.to = Officer.N
		assert promotion.to.value is Knight


class TestPromotionCapt(AlgebraSetup):

	CapturePromotion = Promotion[Capt]

	illegal_ranks = (
		(True, Index.B6, Index.A7),
		(False, Index.G3, Index.H2),
	)

	def test_choices_are_independent(self) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, Index.B7, True)
		self.place(game, Knight, Index.A8, pawn.side.other)
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

	@pytest.mark.parametrize("white, source, target, notation", AlgebraSetup.capture_cases)
	@pytest.mark.parametrize("choice", AlgebraSetup.choices)
	def test_capture_with_selected_choice(self, white, source, target, notation, choice) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		enemy = self.place(game, Knight, target, pawn.side.other)
		promotion = self.CapturePromotion(target, pawn)
		promotion.to = choice
		assert bool(promotion)
		assert promotion.other is enemy
		assert repr(promotion) == notation + "=" + choice.name

	@pytest.mark.parametrize("white, source, target, notation", AlgebraSetup.capture_cases)
	def test_capture_requires_enemy(self, white, source, target, notation) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion
		self.place(game, Knight, target, pawn.side)
		assert not promotion
		self.place(game, Knight, target, pawn.side.other)
		assert bool(promotion)
		promotion.to = Officer.Q
		assert repr(promotion) == notation + "=Q"

	@pytest.mark.parametrize("white, source, target", illegal_ranks)
	def test_capture_requires_penultimate_source_rank(self, white, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		self.place(game, Knight, target, pawn.side.other)
		promotion = self.CapturePromotion(target, pawn)
		assert not promotion


class TestEnPassant(AlgebraSetup):

	valid_moves = (
		(True, Index.E5, Index.D6),
		(False, Index.E4, Index.D3),
	)
	other_ranks = (
		(True, Index.E1, Index.D2),
		(True, Index.E2, Index.D3),
		(True, Index.E4, Index.D5),
		(False, Index.E7, Index.D6),
		(False, Index.E6, Index.D5),
		(False, Index.E5, Index.D4),
	)
	occupants = (
		(None, False, False),
		(Ghost, True, False),
		(Pawn, False, False),
		(Knight, False, False),
		(Ghost, False, True),
	)

	@pytest.mark.parametrize("white, source, target", valid_moves)
	def test_en_passant_rank(self, white, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		ghost = self.place(game, Ghost, target, pawn.side.other)
		capture = EnPassant(target, pawn)
		assert bool(capture)
		assert capture.source is source
		assert capture.target is target
		assert capture.other is ghost

	@pytest.mark.parametrize("white, source, target", other_ranks)
	def test_requires_en_passant_rank(self, white, source, target) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)
		self.place(game, Ghost, target, pawn.side.other)
		assert not EnPassant(target, pawn)

	@pytest.mark.parametrize("white, source, target", valid_moves)
	@pytest.mark.parametrize("kind, friendly, expected", occupants)
	def test_requires_enemy_ghost(self, white, source, target, kind, friendly, expected) -> None:
		game = self.board()
		pawn = self.place(game, Pawn, source, white)

		if kind is not None:
			self.place(game, kind, target, pawn.side if friendly else pawn.side.other)

		assert bool(EnPassant(target, pawn)) is expected
