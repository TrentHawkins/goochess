from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess.geometry import Color, Compass, Index
from goochess.mathematics import array, arrays, indices


class TestSquare: # pylint: disable = no-member

	members = tuple(Index)
	fen_names = tuple(f"{file}{rank}" for rank in range(8, 0, -1) for file in "ABCDEFGH")
	diagonal = array(-1, 0) + array(0, -1)
	translations = (
		(operator.add, Index.A1, array(1, -1), Index.B2),
		(operator.add, array(1, -1), Index.A1, Index.B2),
		(operator.add, array(0, -1), Index.B2, Index.B3),
		(operator.add, Index.A1, array(0, -1), Index.A2),
		(operator.add, Index.A1, array(1, 0), Index.B1),
		(operator.sub, Index.B2, array(1, -1), Index.A1),
		(operator.add, Index.D4, diagonal, Index.C5),
		(operator.add, diagonal, Index.D4, Index.C5),
	)
	differences = ((Index.B2, Index.A1, (1, -1)), (Index.A1, Index.H8, (-7, 7)), (Index.A1, Index.A1, (0, 0)))
	invalid_translations = ((Index.H1, array(1, 0)), (Index.A8, array(0, -1)), (Index.A1, array(0, 1)))
	rays = ((Index.A6, array(0, -1), (Index.A7, Index.A8)), (Index.H8, array(1, -1), ()))
	serialization_values = (Index.A1, Index.B2, Index.H8)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	def test_board(self) -> None:
		assert (Index.dimension, Index.base) == (2, 8)
		assert tuple(member.name for member in self.members) == self.fen_names
		assert tuple(int(member) for member in self.members) == tuple(range(64))
		assert (int(Index.A8), int(Index.H8), int(Index.A7), int(Index.A1), int(Index.H1)) == (0, 7, 8, 56, 63)
		assert not Index.A1
		assert Index.A8
		assert Index.H1

	def test_collection(self) -> None:
		assert indices(*self.members) == set(self.members)

	@pytest.mark.parametrize("member", members)
	def test_coordinates_and_notation(self, member) -> None:
		file, rank = member.name
		components = (ord(file) - ord("A"), 8 - int(rank))
		white = (ord(file) - ord("A") + int(rank) - 1) % 2 == 1
		assert member.array == components
		assert (member[0], member[1]) == components
		assert member.rank == int(rank)
		assert member.file == file.lower()
		assert repr(member) == member.name.lower()
		assert bool(member) is white
		assert member.color is (Color.WHITE if white else Color.BLACK)
		assert Index.from_sequence(components) is member

	@pytest.mark.parametrize("operation, left, right, expected", translations)
	def test_translation(self, operation, left, right, expected) -> None:
		assert operation(left, right) is expected

	@pytest.mark.parametrize("left, right, expected", differences)
	def test_difference(self, left, right, expected) -> None:
		result = left - right
		assert result == expected
		assert type(result) is array

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
		(Compass.north, (0, -1), Index.D5),
		(Compass.south, (0, 1), Index.D3),
		(Compass.east, (1, 0), Index.E4),
		(Compass.west, (-1, 0), Index.C4),
	)

	@pytest.mark.parametrize("direction, components, target", directions)
	def test_direction(self, direction, components, target) -> None:
		assert direction == components
		assert Index.D4 + direction is target
