from __future__ import annotations

from enum import Enum
from typing import Any


class Color(int, Enum):

	WHITE = -1  # ⬜
	BLACK = +1  # ⬛


	def __repr__(self) -> str:
		return "⬛" if self + 1 else "⬜"
