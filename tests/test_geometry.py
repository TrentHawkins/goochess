from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess.geometry import Square, Vector, Vectors
from goochess.mathematics import array, arrays, indices


class TestSquare: # pylint: disable = no-member

	members = tuple(Square)
	diagonal = Vector.north + Vector.east
	translations = (
		(operator.add, Square.A1, array(1, 1), Square.B2),
		(operator.add, array(1, 1), Square.A1, Square.B2),
		(operator.add, array(1, 0), Square.B2, Square.B3),
		(operator.add, Square.A1, array(1, 0), Square.A2),
		(operator.add, Square.A1, array(0, 1), Square.B1),
		(operator.sub, Square.B2, array(1, 1), Square.A1),
		(operator.add, Square.D4, diagonal, Square.C5),
		(operator.add, diagonal, Square.D4, Square.C5),
	)
	differences = ((Square.B2, Square.A1, (1, 1)), (Square.A1, Square.H8, (-7, -7)), (Square.A1, Square.A1, (0, 0)))
	invalid_translations = ((Square.H1, array(0, 1)), (Square.A8, array(1, 0)), (Square.A1, array(-1, 0)))
	rays = ((Square.A6, array(1, 0), (Square.A7, Square.A8)), (Square.H8, array(1, 1), ()))
	serialization_values = (Square.A1, Square.B2, Square.H8)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	def test_board(self) -> None:
		assert (Square.dimension, Square.base) == (2, 8)
		assert tuple(int(member) for member in self.members) == tuple(range(64))
		assert not Square.A1
		assert Square.H1

	def test_collection(self) -> None:
		assert indices(*self.members) == set(self.members)

	@pytest.mark.parametrize("member", members)
	def test_coordinates_and_notation(self, member) -> None:
		file, rank = member.name
		components = (int(rank) - 1, ord(file) - ord("A"))
		assert member.array == components
		assert (member[0], member[1]) == components
		assert member.rank == int(rank)
		assert member.file == file.lower()
		assert repr(member) == member.name.lower()
		assert bool(member) is (sum(components) % 2 == 1)
		assert Square.from_sequence(components) is member

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


class TestVector:

	definitions = (
		(Vector.north, ( 0, -1)),
		(Vector.east,  (+1,  0)),
		(Vector.south, ( 0, +1)),
		(Vector.west,  (-1,  0)),
	)
	opposites = ((Vector.north, Vector.south), (Vector.east, Vector.west))

	@pytest.mark.parametrize("direction, expected", definitions)
	def test_coordinates(self, direction, expected) -> None:
		assert direction == expected
		assert type(direction) is array

	@pytest.mark.parametrize("first, second", opposites)
	def test_opposites(self, first, second) -> None:
		assert -first == second
		assert -second == first


class TestVectors:

	axes = (
		(Vectors.ranks, {(0, -1), (0, 1)}),
		(Vectors.files, {(1, 0), (-1, 0)}),
	)
	rook = Vectors.ranks | Vectors.files
	bishop = Vectors.ranks * Vectors.files
	knight = (2 * Vectors.ranks * Vectors.files) | (Vectors.ranks * (2 * Vectors.files))
	movements = (
		(rook, {(0, -1), (1, 0), (0, 1), (-1, 0)}),
		(bishop, {(1, -1), (1, 1), (-1, 1), (-1, -1)}),
		(knight, {(1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2)}),
	)

	@pytest.mark.parametrize("directions, expected", axes)
	def test_axes(self, directions, expected) -> None:
		assert directions == expected
		assert type(directions) is arrays

	@pytest.mark.parametrize("directions, expected", movements)
	def test_composition(self, directions, expected) -> None:
		assert directions == expected
		assert type(directions) is arrays
		assert all(type(direction) is array for direction in directions)
