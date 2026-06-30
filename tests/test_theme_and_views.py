from __future__ import annotations


from dataclasses import replace
from pathlib import Path

import pytest

import src.algebra
import src.engine
import src.rules

pytest.importorskip("pygame")

from app.controller import InteractionState
from app.layout import BoardLayout
from app.theme import DEFAULT_THEME, THEMES, Theme, load_theme, theme_spec
from app.views import GameView


def test_theme_registry_and_assets(pygame_screen):
	theme = load_theme()

	assert tuple(THEMES) == (DEFAULT_THEME,)
	assert len(theme.pieces) == 14
	assert theme.background.get_size() == theme.layout.window
	assert theme.square.get_size() == theme.layout.square_size


def test_unknown_theme_lists_available_names():
	with pytest.raises(ValueError, match = "available themes: wood"):
		theme_spec("missing")


def test_missing_asset_identifies_theme_and_asset(pygame_screen):
	spec = replace(theme_spec(), background = Path("graphics/missing.png"))

	with pytest.raises(FileNotFoundError, match = "Theme 'wood' asset 'background'"):
		Theme.load(spec)


def test_rendering_does_not_mutate_core_state(pygame_screen):
	game = src.engine.Game.from_forsyth_edwards()
	state = InteractionState(selected = game[src.algebra.Square.E2])
	theme = load_theme()
	view = GameView(BoardLayout(theme.layout), theme)
	before = [
		None if piece is None else (id(piece), piece.square, piece.color)
		for piece in game
	]
	history = tuple(game.history)

	view.draw(pygame_screen, game, state)

	after = [
		None if piece is None else (id(piece), piece.square, piece.color)
		for piece in game
	]
	assert after == before
	assert tuple(game.history) == history
	assert pygame_screen.get_size() == (2160, 1440)


def test_rendering_pending_promotion(pygame_screen):
	game = src.engine.Game.from_forsyth_edwards(
		"4♚3/♙7/8/8/8/8/8/4♔3 w - - 0 1"
	)
	pawn = game[src.algebra.Square.A7]
	assert pawn is not None
	promotion = pawn.squares.get(src.algebra.Square.A8)
	assert isinstance(promotion, src.rules.Promotion)

	theme = load_theme()
	view = GameView(BoardLayout(theme.layout), theme)
	view.draw(
		pygame_screen,
		game,
		InteractionState(selected = pawn, promotion = promotion),
	)

	assert game[src.algebra.Square.A7] is pawn
	assert game[src.algebra.Square.A8] is None
