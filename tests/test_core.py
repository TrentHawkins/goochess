from __future__ import annotations


import src.algebra
import src.engine
import src.material
import src.rules


def move(game: src.engine.Game, source: src.algebra.Square, target: src.algebra.Square) -> src.rules.Move:
	piece = game[source]
	assert piece is not None

	rule = piece.squares.get(target)
	assert rule is not None
	game += rule

	return rule


def test_initial_position_and_turn_progression():
	game = src.engine.Game.from_forsyth_edwards()
	pawn = game[src.algebra.Square.E2]

	assert len(game) == 64
	assert len(list(game.white)) == 16
	assert len(list(game.black)) == 16
	assert game.current is game.white
	assert pawn is not None
	assert {rule.target for rule in pawn.squares} == {
		src.algebra.Square.E3,
		src.algebra.Square.E4,
	}

	move(game, src.algebra.Square.E2, src.algebra.Square.E4)

	assert game[src.algebra.Square.E2] is None
	assert game[src.algebra.Square.E4] is pawn
	assert game.current is game.black
	assert len(game.history) == 1


def test_capture():
	game = src.engine.Game.from_forsyth_edwards(
		"8/8/8/3♟4/4♙3/8/8/4♔3 w - - 0 1"
	)
	pawn = game[src.algebra.Square.E4]
	assert pawn is not None

	rule = pawn.squares.get(src.algebra.Square.D5)

	assert isinstance(rule, src.rules.Capt)
	game += rule
	assert game[src.algebra.Square.D5] is pawn
	assert game[src.algebra.Square.E4] is None


def test_castling_targets_and_execution():
	game = src.engine.Game.from_forsyth_edwards(
		"4♚3/8/8/8/8/8/8/♖3♔2♖ w KQ - 0 1"
	)
	king = game[src.algebra.Square.E1]
	assert isinstance(king, src.material.King)

	assert isinstance(king.squares.get(src.algebra.Square.C1), src.rules.CastWest)
	assert isinstance(king.squares.get(src.algebra.Square.G1), src.rules.CastEast)

	move(game, src.algebra.Square.E1, src.algebra.Square.G1)

	assert isinstance(game[src.algebra.Square.G1], src.material.King)
	assert isinstance(game[src.algebra.Square.F1], src.material.Rook)


def test_en_passant_expires_after_one_reply():
	game = src.engine.Game.from_forsyth_edwards()

	move(game, src.algebra.Square.E2, src.algebra.Square.E4)
	move(game, src.algebra.Square.A7, src.algebra.Square.A6)
	move(game, src.algebra.Square.E4, src.algebra.Square.E5)
	move(game, src.algebra.Square.D7, src.algebra.Square.D5)

	pawn = game[src.algebra.Square.E5]
	assert pawn is not None
	assert isinstance(pawn.squares.get(src.algebra.Square.D6), src.rules.EnPassant)

	move(game, src.algebra.Square.H2, src.algebra.Square.H3)

	assert game[src.algebra.Square.D6] is None


def test_king_safety_rejects_exposing_move():
	game = src.engine.Game.from_forsyth_edwards(
		"4♜3/8/8/8/8/8/4♖3/4♔3 w - - 0 1"
	)
	rook = game[src.algebra.Square.E2]
	assert isinstance(rook, src.material.Rook)

	assert rook.targets.get(src.algebra.Square.D2) is not None
	assert rook.squares.get(src.algebra.Square.D2) is None


def test_promotion_uses_explicit_officer_choice():
	game = src.engine.Game.from_forsyth_edwards(
		"4♚3/♙7/8/8/8/8/8/4♔3 w - - 0 1"
	)
	pawn = game[src.algebra.Square.A7]
	assert isinstance(pawn, src.material.Pawn)

	rule = pawn.squares.get(src.algebra.Square.A8)
	assert isinstance(rule, src.rules.Promotion)
	assert rule.officer is src.material.Officer.Q

	rule.officer = src.material.Officer.R
	game += rule

	assert isinstance(game[src.algebra.Square.A8], src.material.Rook)
