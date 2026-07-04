from __future__ import annotations


from dataclasses import dataclass

import pygame

import src.algebra
import src.engine
import src.material
import src.rules

from app.animation import MoveAnimator
from app.layout import BoardLayout


_ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
_HAND_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)


@dataclass(slots = True)
class InteractionState:

	selected: src.material.Piece | None = None
	promotion: src.rules.Promotion | None = None


class GameController:

	def __init__(self,
		game: src.engine.Game,
		layout: BoardLayout,
		state: InteractionState | None = None,
		animator: MoveAnimator | None = None,
	):
		self.game = game
		self.layout = layout
		self.state = state if state is not None else InteractionState()
		self.animator = animator if animator is not None else MoveAnimator()
		self._cursor: pygame.cursors.Cursor | None = None


	def handle(self, event: pygame.event.Event) -> bool:
		if event.type == pygame.MOUSEMOTION:
			self.hover(event.pos)
			return True

		if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
			return False

		square = self.layout.square_at(event.pos)
		handled = False if square is None else self.click(square)
		self.hover(event.pos)

		return handled

	def hover(self, position: tuple[int, int]) -> bool:
		square = self.layout.square_at(position)
		piece = None if square is None else self.game[square]
		playable = not self.animator.active and piece is not None and bool(piece.side)
		cursor = _HAND_CURSOR if playable else _ARROW_CURSOR

		if cursor != self._cursor:
			pygame.mouse.set_cursor(cursor)
			self._cursor = cursor

		return playable

	def click(self, square: src.algebra.Square) -> bool:
		if self.animator.active:
			return False

		if self.state.promotion is not None:
			promotion = self.state.promotion

			if square == promotion.source:
				officers = tuple(src.material.Officer)
				index = officers.index(promotion.officer)
				promotion.officer = officers[(index + 1) % len(officers)]
				return True

			if square == promotion.target:
				self.animator.start(promotion)
				self.state.selected = None

			else:
				self.reselect(square)

			self.state.promotion = None
			return True

		if self.state.selected is not None:
			rule = self.state.selected.squares.get(square)

			if rule is not None:
				if isinstance(rule, src.rules.Promotion):
					self.state.promotion = rule

				else:
					self.animator.start(rule)
					self.state.selected = None
			else:
				self.reselect(square)

			return True

		piece = self.game[square]

		if piece is not None and piece.side:
			self.state.selected = piece

		return True

	def reselect(self, square: src.algebra.Square) -> None:
		piece = self.game[square]
		self.state.selected = piece if piece is not None and piece is not self.state.selected and piece.side else None

	def update(self, seconds: float) -> bool:
		rule = self.animator.advance(seconds)

		if rule is None:
			return False

		self.game += rule
		return True
