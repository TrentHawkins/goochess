from __future__ import annotations

from abc import ABC as AbstractClass, abstractmethod

import pygame

from chess.algebra import Color, Rank, File, Difference, Square, Difference
from chess.material import Piece, Pawn, Rook, Bishop, Knight, Queen, King
from chess.rules import Move, Capt, CastleLong, CastleShort
from chess.engine import Board, Side, Game
