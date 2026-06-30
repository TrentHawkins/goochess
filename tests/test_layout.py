from __future__ import annotations


import pytest

import src.algebra

pytest.importorskip("pygame")

from app.layout import BoardLayout, LayoutSpec


def test_square_round_trip():
	layout = BoardLayout(LayoutSpec())

	for square in src.algebra.Square:
		assert layout.square_at(layout.square_rect(square).center) is square


def test_points_outside_board_have_no_square():
	layout = BoardLayout(LayoutSpec())
	rect = layout.board_rect

	assert layout.square_at((rect.left - 1, rect.top)) is None
	assert layout.square_at((rect.left, rect.top - 1)) is None
	assert layout.square_at((rect.right, rect.bottom - 1)) is None
	assert layout.square_at((rect.right - 1, rect.bottom)) is None
