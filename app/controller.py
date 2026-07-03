from __future__ import annotations


from dataclasses import dataclass

import pygame

import src.algebra
import src.engine
import src.material
import src.rules

from app.layout import BoardLayout


@dataclass(slots = True)
class InteractionState:

	selected: src.material.Piece | None = None
	promotion: src.rules.Promotion | None = None


class GameController:

	def __init__(self,
		game: src.engine.Game,
		layout: BoardLayout,
		state: InteractionState | None = None,
	):
		self.game = game
		self.layout = layout
		self.state = state if state is not None else InteractionState()


	def handle(self, event: pygame.event.Event) -> bool:
		if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
			return False

		square = self.layout.square_at(event.pos)
		return False if square is None else self.click(square)

	def click(self, square: src.algebra.Square) -> bool:
		if self.state.promotion is not None:
			promotion = self.state.promotion

			if square == promotion.source:
				officers = tuple(src.material.Officer)
				index = officers.index(promotion.officer)
				promotion.officer = officers[(index + 1) % len(officers)]

			else:
				if square == promotion.target:
					self.game += promotion

				self.state.selected = None
				self.state.promotion = None

			return True

		if self.state.selected is not None:
			rule = self.state.selected.squares.get(square)

			if rule is not None:
				if isinstance(rule, src.rules.Promotion):
					self.state.promotion = rule

				else:
					self.game += rule
					self.state.selected = None
			else:
				self.state.selected = None

			return True

		piece = self.game[square]

		if piece is not None and piece.side:
			self.state.selected = piece

		return True
