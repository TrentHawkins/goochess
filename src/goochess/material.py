from __future__ import annotations


from .geometry import Square

class Piece:

	...


class Pawn(Piece):

	...


class Melee(Piece):

	...


class Ranged(Piece):

	...


class Officer(Piece):

	...


class Rook(Melee, Officer):

	...


class Bishop(Melee, Officer):

	...


class Knight(Melee, Officer):

	...


class Queen(Ranged, Officer):

	...


class King(Melee):

	...
