from __future__ import annotations


from .geometry import Square
from .material import Piece


class Board(list[Piece | None]):

	...
