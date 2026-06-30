from __future__ import annotations


from dataclasses import replace
from pathlib import Path

import pytest

import src.algebra
import src.engine
import src.rules

pytest.importorskip("pygame")

from app.controller import InteractionState
from app.layout import BoardLayout, LayoutSpec
from app.theme import (
	BOARD_THEMES,
	DEFAULT_BOARD_THEME,
	DEFAULT_PIECE_THEME,
	PIECE_THEMES,
	BoardTheme,
	PieceTheme,
	board_theme_spec,
	load_appearance,
	piece_theme_spec,
)
from app.views import GameView


def test_independent_theme_registries_and_assets(pygame_screen):
	layout = LayoutSpec()
	appearance = load_appearance(layout)

	assert tuple(BOARD_THEMES) == (DEFAULT_BOARD_THEME,)
	assert tuple(PIECE_THEMES) == (DEFAULT_PIECE_THEME,)
	assert appearance.board.spec.name == "wood"
	assert appearance.pieces.spec.name == "default"
	assert len(appearance.pieces.surfaces) == 14
	assert appearance.board.background.get_size() == layout.window
	assert appearance.board.square.get_size() == layout.square_size


def test_unknown_themes_list_available_names():
	with pytest.raises(ValueError, match = "available board themes: wood"):
		board_theme_spec("missing")

	with pytest.raises(ValueError, match = "available piece themes: default"):
		piece_theme_spec("missing")


def test_missing_board_asset_identifies_theme_and_asset(pygame_screen):
	spec = replace(board_theme_spec(), background = Path("graphics/missing.png"))

	with pytest.raises(FileNotFoundError, match = "Board theme 'wood' asset 'background'"):
		BoardTheme.load(spec, LayoutSpec())


def test_missing_piece_asset_identifies_theme_and_asset(pygame_screen):
	spec = piece_theme_spec()
	key = next(iter(spec.styles))
	styles = dict(spec.styles)
	styles[key] = replace(styles[key], asset = Path("graphics/missing.png"))

	with pytest.raises(FileNotFoundError, match = "Piece theme 'default' asset"):
		PieceTheme.load(replace(spec, styles = styles), LayoutSpec())


def test_rendering_does_not_mutate_core_state(pygame_screen):
	game = src.engine.Game.from_forsyth_edwards()
	state = InteractionState(selected = game[src.algebra.Square.E2])
	layout = LayoutSpec()
	appearance = load_appearance(layout)
	view = GameView(BoardLayout(layout), appearance)
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

	layout = LayoutSpec()
	appearance = load_appearance(layout)
	view = GameView(BoardLayout(layout), appearance)
	view.draw(
		pygame_screen,
		game,
		InteractionState(selected = pawn, promotion = promotion),
	)

	assert game[src.algebra.Square.A7] is pawn
	assert game[src.algebra.Square.A8] is None
