from __future__ import annotations


from itertools import product

from src import zerosumarray


class TestHex:

	def test_initialization(self):
		class hex(zerosumarray,
			dimension = 3,
		):

			...

		for x, y, z in product(range(-16, +16),
			repeat = 3,
		):
			vector = hex(x, y, z)

			assert len(vector) == vector.dimension - 1
			assert sum(vector) == 0
