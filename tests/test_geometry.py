from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess import geometry
from goochess import mathematics


class TestIndex: # pylint: disable = no-member

	members = tuple(geometry.Index)
	fen_names = tuple(f"{file}{rank}" for rank in range(8, 0, -1) for file in "ABCDEFGH")
	diagonal = mathematics.array(-1, 0) + mathematics.array(0, -1)
	translations = (
		(operator.add, geometry.Index.A1, mathematics.array(1, -1), geometry.Index.B2),
		(operator.add, mathematics.array(1, -1), geometry.Index.A1, geometry.Index.B2),
		(operator.add, mathematics.array(0, -1), geometry.Index.B2, geometry.Index.B3),
		(operator.add, geometry.Index.A1, mathematics.array(0, -1), geometry.Index.A2),
		(operator.add, geometry.Index.A1, mathematics.array(1, 0), geometry.Index.B1),
		(operator.sub, geometry.Index.B2, mathematics.array(1, -1), geometry.Index.A1),
		(operator.add, geometry.Index.D4, diagonal, geometry.Index.C5),
		(operator.add, diagonal, geometry.Index.D4, geometry.Index.C5),
	)
	differences = ((geometry.Index.B2, geometry.Index.A1, (1, -1)), (geometry.Index.A1, geometry.Index.H8, (-7, 7)), (geometry.Index.A1, geometry.Index.A1, (0, 0)))
	invalid_translations = ((geometry.Index.H1, mathematics.array(1, 0)), (geometry.Index.A8, mathematics.array(0, -1)), (geometry.Index.A1, mathematics.array(0, 1)))
	rays = ((geometry.Index.A6, mathematics.array(0, -1), (geometry.Index.A7, geometry.Index.A8)), (geometry.Index.H8, mathematics.array(1, -1), ()))
	serialization_values = (geometry.Index.A1, geometry.Index.B2, geometry.Index.H8)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	def test_board(self) -> None:
		assert (geometry.Index.dimension, geometry.Index.base) == (2, 8)
		assert tuple(member.name for member in self.members) == self.fen_names
		assert tuple(int(member) for member in self.members) == tuple(range(64))
		assert (int(geometry.Index.A8), int(geometry.Index.H8), int(geometry.Index.A7), int(geometry.Index.A1), int(geometry.Index.H1)) == (0, 7, 8, 56, 63)
		assert geometry.Index.A1
		assert not geometry.Index.A8
		assert not geometry.Index.H1

	def test_collection(self) -> None:
		assert mathematics.indices(*self.members) == set(self.members)

	@pytest.mark.parametrize("member", members)
	def test_coordinates_and_notation(self, member) -> None:
		file, rank = member.name
		components = (ord(file) - ord("A"), 8 - int(rank))
		black = (ord(file) - ord("A") + int(rank) - 1) % 2 == 0
		assert member.array == components
		assert (member[0], member[1]) == components
		assert member.rank == int(rank)
		assert member.file == file.lower()
		assert repr(member) == member.name.lower()
		assert bool(member) is black
		assert geometry.Index.from_sequence(components) is member

	@pytest.mark.parametrize("operation, left, right, expected", translations)
	def test_translation(self, operation, left, right, expected) -> None:
		assert operation(left, right) is expected

	@pytest.mark.parametrize("left, right, expected", differences)
	def test_difference(self, left, right, expected) -> None:
		result = left - right
		assert result == expected
		assert type(result) is mathematics.array

	@pytest.mark.parametrize("square, displacement", invalid_translations)
	def test_translation_bounds(self, square, displacement) -> None:
		with pytest.raises(ValueError):
			_ = square + displacement

	@pytest.mark.parametrize("square, step, expected", rays)
	def test_range(self, square, step, expected) -> None:
		result = tuple(square.range(step))
		assert result == expected
		assert all(actual is member for actual, member in zip(result, expected, strict = True))

	@pytest.mark.parametrize("value", serialization_values)
	def test_serialization(self, value) -> None:
		for copier in self.copy_functions:
			assert copier(value) is value

		for protocol in self.pickle_protocols:
			assert pickle.loads(pickle.dumps(value, protocol = protocol)) is value


class TestCompass:

	directions = (
		(geometry.Compass.north, (0, -1), geometry.Index.D5),
		(geometry.Compass.south, (0, 1), geometry.Index.D3),
		(geometry.Compass.east, (1, 0), geometry.Index.E4),
		(geometry.Compass.west, (-1, 0), geometry.Index.C4),
	)

	@pytest.mark.parametrize("direction, components, target", directions)
	def test_direction(self, direction, components, target) -> None:
		assert direction == components
		assert geometry.Index.D4 + direction is target

	def test_orthogonal_groups(self) -> None:
		assert geometry.Compass.ranks == mathematics.arrays(geometry.Compass.north, geometry.Compass.south)
		assert geometry.Compass.files == mathematics.arrays(geometry.Compass.east, geometry.Compass.west)
