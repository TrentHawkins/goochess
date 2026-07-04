from __future__ import annotations


import pytest

import src.algebra
import src.engine
import src.material

pytest.importorskip("pygame")

import pygame

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

	control.click(src.algebra.Square.D2)
	assert control.state.selected is game[src.algebra.Square.D2]

	control.click(src.algebra.Square.D2)
	assert control.state.selected is None

	control.click(src.algebra.Square.E2)
	control.click(src.algebra.Square.E5)
	assert control.state.selected is None

	control.click(src.algebra.Square.E2)
	control.click(src.algebra.Square.E4)

	assert control.animator.active
	assert game[src.algebra.Square.E2] is not None
	assert game[src.algebra.Square.E4] is None

	half = control.animator.spec.duration / 2
	assert not control.update(half)
	assert control.update(half)
	assert control.state.selected is None
	assert isinstance(game[src.algebra.Square.E4], src.material.Pawn)
	assert game.current is game.black


def test_cursor_tracks_playable_piece_hover(monkeypatch):
	game = src.engine.Game.from_forsyth_edwards()
	control = controller(game)
	cursors: list[pygame.cursors.Cursor] = []
	monkeypatch.setattr(pygame.mouse, "set_cursor", cursors.append)

	position = control.layout.square_rect(src.algebra.Square.E2).center
	assert control.handle(pygame.event.Event(pygame.MOUSEMOTION, pos = position))
	assert cursors == [pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)]

	assert control.hover(control.layout.square_rect(src.algebra.Square.D2).center)
	assert len(cursors) == 1

	assert not control.hover(control.layout.square_rect(src.algebra.Square.E7).center)
	assert cursors[-1] == pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)

	assert not control.hover((0, 0))
	assert len(cursors) == 2


def test_cursor_follows_turn_after_move(monkeypatch):
	game = src.engine.Game.from_forsyth_edwards()
	control = controller(game)
	cursors: list[pygame.cursors.Cursor] = []
	monkeypatch.setattr(pygame.mouse, "set_cursor", cursors.append)

	control.click(src.algebra.Square.E2)
	control.click(src.algebra.Square.E4)
	control.update(control.animator.spec.duration)

	assert not control.hover(control.layout.square_rect(src.algebra.Square.E4).center)
	assert cursors[-1] == pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)

	assert control.hover(control.layout.square_rect(src.algebra.Square.E7).center)
	assert cursors[-1] == pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)


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
	assert isinstance(game[src.algebra.Square.A7], src.material.Pawn)
	assert game[src.algebra.Square.A8] is None

	control.update(control.animator.spec.duration)
	assert isinstance(game[src.algebra.Square.A8], src.material.Rook)

	game = src.engine.Game.from_forsyth_edwards(notation)
	control = controller(game)
	control.click(src.algebra.Square.A7)
	control.click(src.algebra.Square.A8)
	control.click(src.algebra.Square.E1)

	assert control.state.promotion is None
	assert control.state.selected is game[src.algebra.Square.E1]
	assert isinstance(game[src.algebra.Square.A7], src.material.Pawn)

	game = src.engine.Game.from_forsyth_edwards(notation)
	control = controller(game)
	control.click(src.algebra.Square.A7)
	control.click(src.algebra.Square.A8)
	control.click(src.algebra.Square.B7)

	assert control.state.promotion is None
	assert control.state.selected is None
	assert isinstance(game[src.algebra.Square.A7], src.material.Pawn)
