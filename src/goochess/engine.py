from __future__ import annotations


from .geometry import Index
from .material import Piece


class Board(list[Piece | None]):

	...
