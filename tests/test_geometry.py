from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess import geometry
from goochess.mathematics import vector


class TestIndex:

	coordinates = ((0, 0), (7, 0), (0, 7), (7, 7), (2, 3))
	invalid_coordinates = ((), (0,), (0, 0, 0), (-1, 0), (0, -1), (8, 0), (0, 8))
	invalid_values = (-1, 64)

	def test_board_configuration(self) -> None:
		assert geometry.index.dim == 2
		assert geometry.index.base == 8

	@pytest.mark.parametrize("coordinates", coordinates)
	def test_construction_and_factory_agree(self, coordinates) -> None:
		value = geometry.index(coordinates)
		result = geometry.index.from_vector(vector(coordinates))
		assert type(value) is type(result) is geometry.index
		assert value == result == coordinates[0] + 8 * coordinates[1]
		assert value.vector == coordinates

	@pytest.mark.parametrize("coordinates", invalid_coordinates)
	def test_invalid_coordinates(self, coordinates) -> None:
		with pytest.raises(ValueError):
			geometry.index.from_vector(coordinates)

	@pytest.mark.parametrize("value", invalid_values)
	def test_encoded_bounds(self, value) -> None:
		with pytest.raises(ValueError):
			geometry.index(value)


class TestSquare:

	members = tuple(geometry.Square)
	encoded_values = tuple(range(64))
	displacement = vector((1, 1))
	arithmetic_cases = (
		(operator.add, geometry.Square.A1, displacement, geometry.Square.B2),
		(operator.add, displacement, geometry.Square.A1, geometry.Square.B2),
		(operator.add, geometry.Square.A1, tuple(displacement), geometry.Square.B2),
		(operator.add, tuple(displacement), geometry.Square.A1, geometry.Square.B2),
		(operator.sub, geometry.Square.B2, displacement, geometry.Square.A1),
		(operator.sub, geometry.Square.B2, tuple(displacement), geometry.Square.A1),
		(operator.add, geometry.Square.A1, vector((0, 0)), geometry.Square.A1),
		(operator.add, geometry.Square.A1, vector((1, 0)), geometry.Square.A2),
		(operator.add, geometry.Square.A1, vector((0, 1)), geometry.Square.B1),
	)
	difference_cases = (
		(geometry.Square.B2, geometry.Square.A1, vector((1, 1))),
		(geometry.Square.A1, geometry.Square.H8, vector((-7, -7))),
		(geometry.Square.A1, geometry.Square.A1, vector((0, 0))),
		(geometry.Square.B2, 0, vector((1, 1))),
	)
	invalid_movements = (
		(operator.add, geometry.Square.H1, vector((0, 1))),
		(operator.add, geometry.Square.A8, vector((1, 0))),
		(operator.sub, geometry.Square.A1, vector((1, 0))),
		(operator.sub, geometry.Square.A1, vector((0, 1))),
		(operator.add, geometry.Square.A1, vector((1,))),
		(operator.sub, geometry.Square.A1, vector((1, 1, 1))),
	)
	invalid_coordinates = ((), (1,), (1, 1, 0), (-1, 0), (8, 0), (0, -1), (0, 8))
	invalid_encoded_values = (-1, 64)
	coordinate_inputs = ((1, 1), vector((1, 1)))
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))
	serialization_values = (geometry.Square.A1, geometry.Square.B2, geometry.Square.H8)

	def test_members_cover_board_exactly_once(self) -> None:
		assert len(self.members) == len(geometry.Square.__members__) == 64
		assert tuple(int(member) for member in self.members) == self.encoded_values

	@pytest.mark.parametrize("member", members)
	def test_coordinates_and_representation_match_name(self, member) -> None:
		file, rank = member.name
		expected = (int(rank) - 1, ord(file) - ord("A"))
		assert member.vector == expected
		assert type(member.vector) is vector
		assert repr(member) == member.name.lower()
		assert type(member.value) is geometry.index
		assert geometry.Square(int(member)) is member
		assert geometry.Square[member.name] is member
		assert geometry.Square.from_vector(expected) is member
		assert geometry.Square.from_vector(member.vector) is member

	@pytest.mark.parametrize("operation, left, right, expected", arithmetic_cases)
	def test_translation_returns_existing_member(self, operation, left, right, expected) -> None:
		assert operation(left, right) is expected

	@pytest.mark.parametrize("left, right, expected", difference_cases)
	def test_difference_returns_vector(self, left, right, expected) -> None:
		result = left - right
		assert result == expected
		assert type(result) is vector

	@pytest.mark.parametrize("operation, position, displacement", invalid_movements)
	def test_invalid_translations(self, operation, position, displacement) -> None:
		with pytest.raises(ValueError):
			operation(position, displacement)

	@pytest.mark.parametrize("coordinates", invalid_coordinates)
	def test_factory_validates_coordinates(self, coordinates) -> None:
		with pytest.raises(ValueError):
			geometry.Square.from_vector(coordinates)

	@pytest.mark.parametrize("value", invalid_encoded_values)
	def test_encoded_lookup_bounds(self, value) -> None:
		with pytest.raises(ValueError):
			geometry.Square(value)

	@pytest.mark.parametrize("coordinates", coordinate_inputs)
	def test_coordinates_require_explicit_factory(self, coordinates) -> None:
		with pytest.raises(ValueError):
			geometry.Square(coordinates)

	@pytest.mark.parametrize("copier", copy_functions)
	@pytest.mark.parametrize("value", serialization_values)
	def test_copy_preserves_identity(self, copier, value) -> None:
		assert copier(value) is value

	@pytest.mark.parametrize("protocol", pickle_protocols)
	@pytest.mark.parametrize("value", serialization_values)
	def test_pickle_preserves_identity(self, protocol, value) -> None:
		assert pickle.loads(pickle.dumps(value, protocol = protocol)) is value
