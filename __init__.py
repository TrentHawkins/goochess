from __future__ import annotations


import itertools
import typing

from chess.theme import Theme, DEFAULT
from chess.algebra import Color, Rank, File, Difference, Square, Difference
from chess.material import Piece, Pawn, Rook, Bishop, Knight, Queen, King
from chess.rules import Move, Capt, CastleLong, CastleShort
from chess.engine import Game, Side, Game
