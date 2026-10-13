from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess.geometry import Square, Vector
from goochess.mathematics import array, arrays, indices


class TestSquare: # pylint: disable = no-member

	members = tuple(Square)
	translations = (
		(operator.add, Square.A1, array((1, 1)), Square.B2),
		(operator.add, array((1, 1)), Square.A1, Square.B2),
		(operator.add, array((1, 0)), Square.B2, Square.B3),
		(operator.add, Square.A1, array((1, 0)), Square.A2),
		(operator.add, Square.A1, array((0, 1)), Square.B1),
		(operator.sub, Square.B2, array((1, 1)), Square.A1),
		(operator.add, Square.D4, Vector.NE, Square.C5),
		(operator.add, Vector.NE, Square.D4, Square.C5),
	)
	differences = ((Square.B2, Square.A1, (1, 1)), (Square.A1, Square.H8, (-7, -7)), (Square.A1, Square.A1, (0, 0)))
	invalid_translations = ((Square.H1, array((0, 1))), (Square.A8, array((1, 0))), (Square.A1, array((-1, 0))))
	rays = ((Square.A6, array((1, 0)), (Square.A7, Square.A8)), (Square.H8, array((1, 1)), ()))
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
		(Vector.N,   ( 0, -1), "▲"),
		(Vector.E,   (+1,  0), "▶"),
		(Vector.S,   ( 0, +1), "▼"),
		(Vector.W,   (-1,  0), "◀"),
		(Vector.N2,  ( 0, -2), "▲▲"),
		(Vector.S2,  ( 0, +2), "▼▼"),
		(Vector.E2,  (+2,  0), "▶▶"),
		(Vector.W2,  (-2,  0), "◀◀"),
		(Vector.NE,  (+1, -1), "▲▶"),
		(Vector.SE,  (+1, +1), "▼▶"),
		(Vector.SW,  (-1, +1), "▼◀"),
		(Vector.NW,  (-1, -1), "▲◀"),
		(Vector.NNE, (+1, -2), "▲▲▶"),
		(Vector.NEE, (+2, -1), "▲▶▶"),
		(Vector.SEE, (+2, +1), "▼▶▶"),
		(Vector.SSE, (+1, +2), "▼▼▶"),
		(Vector.SSW, (-1, +2), "▼▼◀"),
		(Vector.SWW, (-2, +1), "▼◀◀"),
		(Vector.NWW, (-2, -1), "▲◀◀"),
		(Vector.NNW, (-1, -2), "▲▲◀"),
	)
	members = tuple(member for member, _, _ in definitions)
	arithmetic = (
		(operator.add, Vector.N, Vector.E, Vector.NE),
		(operator.add, Vector.E, Vector.N, Vector.NE),
		(operator.add, Vector.N, Vector.N, Vector.N2),
		(operator.add, Vector.NE, Vector.N, Vector.NNE),
		(operator.add, Vector.NE, Vector.E, Vector.NEE),
		(operator.sub, Vector.NE, Vector.E, Vector.N),
		(operator.mul, Vector.N, 2, Vector.N2),
		(operator.mul, 2, Vector.N, Vector.N2),
		(operator.mul, Vector.E, 4, (4, 0)),
		(operator.mul, Vector.NE, Vector.SW, Vector.NW),
		(operator.add, Vector.N2, Vector.N, (0, -3)),
		(operator.mul, Vector.E2, 4, (8, 0)),
		(operator.sub, Vector.N, Vector.N, (0, 0)),
		(operator.mul, Vector.N, 0, (0, 0)),
		(operator.add, Vector.N, 0, Vector.N),
		(operator.add, 0, Vector.N, Vector.N),
		(operator.sub, Vector.N, 0, Vector.N),
		(operator.sub, 0, Vector.N, Vector.S),
		(operator.mul, Vector.N, 1, Vector.N),
		(operator.mul, 1, Vector.N, Vector.N),
		(operator.iadd, Vector.N, Vector.E, Vector.NE),
		(operator.isub, Vector.NE, Vector.E, Vector.N),
		(operator.imul, Vector.N, 2, Vector.N2),
	)
	dot_products = (
		(Vector.N2, Vector.N2, 4),
		(Vector.E2, Vector.W2, -4),
		(Vector.NE, Vector.SW, -2),
		(Vector.NE, 2, 0),
		(Vector.N2, (-1, 2), -4),
	)
	slices = (
		(slice(None), (0, -1)),
		(slice(None, None, -1), (-1, 0)),
		(slice(1, None), (-1,)),
		(slice(0, 0), ()),
	)
	knight_moves = arrays(Vector.NNE, Vector.NEE, Vector.SEE, Vector.SSE, Vector.SSW, Vector.SWW, Vector.NWW, Vector.NNW)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("member, coordinates, representation", definitions)
	def test_coordinates_and_notation(self, member, coordinates, representation) -> None:
		assert tuple(member) == member.value == coordinates
		assert len(member) == 2
		assert (member[0], member[1]) == coordinates
		assert bool(member) is any(coordinates)
		assert repr(member) == representation
		assert Vector(array(coordinates)) is member
		assert abs(member) == sum(component ** 2 for component in coordinates)

	@pytest.mark.parametrize("operation, left, right, expected", arithmetic)
	def test_arithmetic(self, operation, left, right, expected) -> None:
		result = operation(left, right)
		assert result == expected
		assert type(result) is array

	@pytest.mark.parametrize("left, right, expected", dot_products)
	def test_dot_product(self, left, right, expected) -> None:
		assert left @ right == right @ left == expected

	def test_unary_operations(self) -> None:
		for member in self.members:
			assert +member is member
			result = -member
			assert type(result) is array
			assert Vector(result) == result
			assert -result == member

	@pytest.mark.parametrize("key, expected", slices)
	def test_slicing(self, key, expected) -> None:
		result = Vector.N[key]
		assert result == expected
		assert type(result) is tuple

	def test_movement_collections(self) -> None:
		product = self.knight_moves * self.knight_moves
		assert product == self.knight_moves ** 2
		assert array((0, 0)) in product
		assert all(type(move) is array for move in product)
		assert product * product == self.knight_moves ** 4

	@pytest.mark.parametrize("member", members)
	def test_serialization(self, member) -> None:
		for copier in self.copy_functions:
			assert copier(member) is member

		for protocol in self.pickle_protocols:
			assert pickle.loads(pickle.dumps(member, protocol = protocol)) is member
