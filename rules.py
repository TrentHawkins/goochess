from __future__ import annotations


import dataclasses
import typing

import chess.geometry

if typing.TYPE_CHECKING: import chess.material
if typing.TYPE_CHECKING: import chess.engine


@dataclasses.dataclass
class Rule:

	game: chess.engine.Game
	side: chess.engine.Side


@dataclasses.dataclass
class Move:

	piece: chess.material.Piece
	square: chess.geometry.Square


	def __post_init__(self):
		self.game = self.piece.game
		self.side = self.piece.side

		assert self.piece.square is not None

		self.source = self.piece.square
		self.target = self.square

	def __repr__(self) -> str:
		return repr(self.piece) + repr(self.source) + "-" + repr(self.target)

	def __bool__(self) -> bool:
		return self.game[self.target] is None


@dataclasses.dataclass
class Capt(Move):

	def __repr__(self) -> str:
		return super().__repr__().replace("-", "×")

	def __bool__(self) -> bool:
		return (other := self.game[self.target]) is not None and self.piece.color != other.color


@dataclasses.dataclass
class Promote(Move):

	rank: type[chess.material.Officer]


	def __repr__(self) -> str:
		return super().__repr__() + repr(self.rank)

	def __bool__(self) -> bool:
		return self.target.rank.final(self.piece.color) and super().__bool__()


@dataclasses.dataclass
class CastleLong(Rule):

	def __repr__(self) -> str:
		return "O-O-O"

	def __bool__(self) -> bool:
		return not self.side.king.moved


@dataclasses.dataclass
class CastleShort(Rule):

	def __repr__(self) -> str:
		return "O-O"

	def __bool__(self) -> bool:
		return not self.side.king.moved
