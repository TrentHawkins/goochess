from __future__ import annotations


import pytest

import src.algebra
import src.engine
import src.material

pytest.importorskip("pygame")

from app.controller import GameController
from app.layout import BoardLayout, LayoutSpec


def controller(game: src.engine.Game) -> GameController:
	return GameController(game, BoardLayout(LayoutSpec()))


def test_selection_deselection_and_move():
	game = src.engine.Game.from_forsyth_edwards()
	control = controller(game)

	control.click(src.algebra.Square.E7)
	assert control.state.selected is None

	control.click(src.algebra.Square.E2)
	assert control.state.selected is game[src.algebra.Square.E2]

	control.click(src.algebra.Square.E5)
	assert control.state.selected is None

	control.click(src.algebra.Square.E2)
	control.click(src.algebra.Square.E4)

	assert control.state.selected is None
	assert isinstance(game[src.algebra.Square.E4], src.material.Pawn)
	assert game.current is game.black


def test_promotion_cycle_commit_and_cancel():
	notation = "4♚3/♙7/8/8/8/8/8/4♔3 w - - 0 1"
	game = src.engine.Game.from_forsyth_edwards(notation)
	control = controller(game)

	control.click(src.algebra.Square.A7)
	control.click(src.algebra.Square.A8)
	assert control.state.promotion is not None
	assert control.state.promotion.officer is src.material.Officer.Q

	control.click(src.algebra.Square.A7)
	assert control.state.promotion.officer is src.material.Officer.R

	control.click(src.algebra.Square.A8)
	assert control.state.promotion is None
	assert control.state.selected is None
	assert isinstance(game[src.algebra.Square.A8], src.material.Rook)

	game = src.engine.Game.from_forsyth_edwards(notation)
	control = controller(game)
	control.click(src.algebra.Square.A7)
	control.click(src.algebra.Square.A8)
	control.click(src.algebra.Square.B7)

	assert control.state.promotion is None
	assert control.state.selected is None
	assert isinstance(game[src.algebra.Square.A7], src.material.Pawn)
