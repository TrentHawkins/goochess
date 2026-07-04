from __future__ import annotations


import pytest

import src.algebra
import src.engine
import src.material

pytest.importorskip("pygame")

from app.animation import AnimationSpec
from app.controller import GameController
from app.layout import BoardLayout, LayoutSpec


def controller(game: src.engine.Game) -> GameController:
	return GameController(game, BoardLayout(LayoutSpec()))


def test_sinusoidal_ease_in_out():
	spec = AnimationSpec(duration = 1.0)

	assert spec.ease(0.0) == pytest.approx(0.0)
	assert spec.ease(0.25) == pytest.approx(0.1464466)
	assert spec.ease(0.5) == pytest.approx(0.5)
	assert spec.ease(0.75) == pytest.approx(0.8535534)
	assert spec.ease(1.0) == pytest.approx(1.0)


def test_capture_remains_until_arrival():
	game = src.engine.Game.from_forsyth_edwards(
		"8/8/8/3♟4/4♙3/8/8/4♔3 w - - 0 1"
	)
	pawn = game[src.algebra.Square.E4]
	captured = game[src.algebra.Square.D5]
	assert isinstance(pawn, src.material.Pawn)
	assert isinstance(captured, src.material.Pawn)

	control = controller(game)
	control.click(src.algebra.Square.E4)
	control.click(src.algebra.Square.D5)

	assert game[src.algebra.Square.E4] is pawn
	assert game[src.algebra.Square.D5] is captured
	assert not control.click(src.algebra.Square.E1)
	assert control.state.selected is None
	half = control.animator.spec.duration / 2
	assert not control.update(half)
	assert game[src.algebra.Square.D5] is captured

	assert control.update(half)
	assert game[src.algebra.Square.E4] is None
	assert game[src.algebra.Square.D5] is pawn


@pytest.mark.parametrize(
	("target", "rook_source", "rook_target"),
	(
		(src.algebra.Square.G1, src.algebra.Square.H1, src.algebra.Square.F1),
		(src.algebra.Square.C1, src.algebra.Square.A1, src.algebra.Square.D1),
	),
)
def test_castling_animates_and_commits_both_pieces(target, rook_source, rook_target):
	game = src.engine.Game.from_forsyth_edwards(
		"4♚3/8/8/8/8/8/8/♖3♔2♖ w KQ - 0 1"
	)
	king = game[src.algebra.Square.E1]
	rook = game[rook_source]
	assert isinstance(king, src.material.King)
	assert isinstance(rook, src.material.Rook)

	control = controller(game)
	control.click(src.algebra.Square.E1)
	control.click(target)

	animation = control.animator.current
	assert animation is not None
	assert tuple(
		(motion.piece, motion.source, motion.target)
		for motion in animation.motions
	) == (
		(king, src.algebra.Square.E1, target),
		(rook, rook_source, rook_target),
	)
	assert game[src.algebra.Square.E1] is king
	assert game[rook_source] is rook

	assert control.update(control.animator.spec.duration)
	assert game[target] is king
	assert game[rook_target] is rook
