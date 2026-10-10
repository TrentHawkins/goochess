from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess.geometry import Square
from goochess.mathematics import vector


class TestSquare: # pylint: disable = no-member

	members = tuple(Square)
	translations = (
		(operator.add, Square.A1, vector(1, 1), Square.B2),
		(operator.add, vector(1, 1), Square.A1, Square.B2),
		(operator.add, Square.A1, vector(1, 0), Square.A2),
		(operator.add, Square.A1, vector(0, 1), Square.B1),
		(operator.sub, Square.B2, vector(1, 1), Square.A1),
	)
	differences = ((Square.B2, Square.A1, (1, 1)), (Square.A1, Square.H8, (-7, -7)), (Square.A1, Square.A1, (0, 0)))
	invalid_translations = ((Square.H1, vector(0, 1)), (Square.A8, vector(1, 0)), (Square.A1, vector(-1, 0)))
	serialization_values = (Square.A1, Square.B2, Square.H8)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	def test_board(self) -> None:
		assert (Square.dim, Square.base) == (2, 8)
		assert tuple(int(member) for member in self.members) == tuple(range(64))
		assert not Square.A1
		assert Square.H1

	@pytest.mark.parametrize("member", members)
	def test_coordinates_and_notation(self, member) -> None:
		file, rank = member.name
		components = (int(rank) - 1, ord(file) - ord("A"))
		assert member.vector == components
		assert (member[0], member[1]) == components
		assert member.rank == int(rank)
		assert member.file == file.lower()
		assert repr(member) == member.name.lower()
		assert bool(member) is (sum(components) % 2 == 1)
		assert Square.from_vector(components) is member

	@pytest.mark.parametrize("operation, left, right, expected", translations)
	def test_translation(self, operation, left, right, expected) -> None:
		assert operation(left, right) is expected

	@pytest.mark.parametrize("left, right, expected", differences)
	def test_difference(self, left, right, expected) -> None:
		result = left - right
		assert result == expected
		assert type(result) is vector

	@pytest.mark.parametrize("square, displacement", invalid_translations)
	def test_translation_bounds(self, square, displacement) -> None:
		with pytest.raises(ValueError):
			_ = square + displacement

	@pytest.mark.parametrize("value", serialization_values)
	def test_serialization(self, value) -> None:
		for copier in self.copy_functions:
			assert copier(value) is value

		for protocol in self.pickle_protocols:
			assert pickle.loads(pickle.dumps(value, protocol = protocol)) is value
