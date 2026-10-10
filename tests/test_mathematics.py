from __future__ import annotations


import copy
import math
import operator
import pickle

from fractions import Fraction

import pytest

from goochess.mathematics import collection, fraction, index, vector, vectors


class TestVector:

	class Derived(vector):
		...

	vector_types = (vector, Derived)
	components = ((), (2,), (2, -3, 4))
	value = vector(2, -3, 4)
	other = vector(5, 1, -2)
	arithmetic = (
		(operator.add, other, (7, -2, 2)),
		(operator.sub, other, (-3, -4, 6)),
		(operator.mul, other, (10, -3, -8)),
		(operator.add, 2, (4, -1, 6)),
		(operator.sub, 2, (0, -5, 2)),
		(operator.mul, 2, (4, -6, 8)),
	)
	reflected = (
		(operator.add, 2, (4, -1, 6)),
		(operator.sub, 2, (0, 5, -2)),
		(operator.mul, 2, (4, -6, 8)),
		(operator.sub, tuple(other), (3, 4, -6)),
	)
	slices = ((slice(1, None), (-3, 4)), (slice(None, None, -1), (4, -3, 2)), (slice(0, 0), ()))
	strict_operations = (operator.add, operator.sub, operator.mul, operator.matmul)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("vector_type", vector_types)
	@pytest.mark.parametrize("components", components)
	def test_construction(self, vector_type, components) -> None:
		value = vector_type(*components)
		assert value == components
		assert len(value) == len(components)
		assert bool(value) is any(components)
		assert hash(value) == hash(components)

	@pytest.mark.parametrize("vector_type", vector_types)
	@pytest.mark.parametrize("operation, other, expected", arithmetic)
	def test_arithmetic(self, vector_type, operation, other, expected) -> None:
		value = vector_type(*self.value)
		result = operation(value, other)
		assert result == expected
		assert type(result) is vector_type
		assert value == self.value

	@pytest.mark.parametrize("operation, other, expected", reflected)
	def test_reflected_arithmetic(self, operation, other, expected) -> None:
		assert operation(other, self.value) == expected

	def test_vector_laws(self) -> None:
		assert (self.value + self.other) - self.other == self.value
		assert self.value + self.other == self.other + self.value
		assert (self.value + self.other) * 2 == self.value * 2 + self.other * 2
		assert self.value + 0 == self.value * 1 == +self.value
		assert -self.value == (-2, 3, -4)
		assert sum((self.value, self.other)) == (7, -2, 2)
		assert vector() + vector() == vector()

	def test_dot_product_and_squared_norm(self) -> None:
		assert self.value @ self.other == self.other @ self.value == -1
		assert self.value @ 2 == 2 @ self.value == 6
		assert abs(self.value) == self.value @ self.value == 29
		assert abs(vector()) == 0

	@pytest.mark.parametrize("vector_type", vector_types)
	@pytest.mark.parametrize("key, expected", slices)
	def test_coordinates_and_slices(self, vector_type, key, expected) -> None:
		value = vector_type(*self.value)
		assert value[0] == 2
		assert value[-1] == 4
		result = value[key]
		assert result == expected
		assert type(result) is vector_type

	@pytest.mark.parametrize("operation", strict_operations)
	def test_dimension_mismatch(self, operation) -> None:
		with pytest.raises(ValueError):
			operation(self.value, vector(1, 2))

	@pytest.mark.parametrize("vector_type", vector_types)
	@pytest.mark.parametrize("components", components)
	def test_serialization(self, vector_type, components) -> None:
		value = vector_type(*components)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is vector_type

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is vector_type
			assert hash(result) == hash(value)


class TestIndex:

	class Binary(index, dim = 3, base = 2):
		...

	class Board(index, dim = 2, base = 8):
		...

	class Decimal(index, dim = 3, base = 10):
		...

	template = index.__class_getitem__((2, 8))
	nested_template = template.__class_getitem__((3, 4))
	index_types = (Binary, Board, Decimal, template, nested_template)
	encoding = ((Binary, (1, 0, 1), 5), (Board, (2, 3), 26), (Decimal, (3, 2, 1), 123))
	position = Board((2, 3))
	other = Board((1, 1))
	displacement = vector(1, -1)
	padding = ((0, (0, 0)), (1, (1, 0)), (7, (7, 0)), (8, (0, 1)))
	slices = ((slice(1, None), (3,)), (slice(None, None, -1), (3, 2)), (slice(0, 0), ()))
	invalid_coordinates = ((), (1,), (1, 2, 3), (-1, 2), (8, 1))
	invalid_values = (-1, 64)
	translations = (operator.add, operator.sub)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("index_type, components, encoded", encoding)
	def test_encoding(self, index_type, components, encoded) -> None:
		assert index_type(components) == index_type(encoded) == encoded
		assert index_type.from_vector(vector(*components)) == encoded
		assert index_type(encoded).vector == components

	@pytest.mark.parametrize("index_type", index_types)
	def test_round_trip(self, index_type) -> None:
		for encoded in range(index_type.base ** index_type.dim):
			value = index_type(encoded)
			assert len(value.vector) == index_type.dim
			assert index_type.from_vector(value.vector) == value

	@pytest.mark.parametrize("encoded, components", padding)
	def test_padding(self, encoded, components) -> None:
		assert self.Board(encoded).vector == components

	@pytest.mark.parametrize("key, expected", slices)
	def test_projection(self, key: slice, expected: tuple[int, ...]) -> None:
		result = self.position[key]
		assert result.vector == expected
		assert result.dim == len(expected)
		assert result.base == self.position.base

	def test_coordinates(self) -> None:
		assert self.position[0] == self.position[-2] == 2
		assert self.position[1] == self.position[-1] == 3

		with pytest.raises(IndexError):
			_ = self.position[2]

	def test_translation_and_difference(self) -> None:
		difference = self.position - self.other
		assert isinstance(difference, vector)
		assert self.position + self.displacement == self.displacement + self.position == self.Board(19)
		assert self.position - self.displacement == self.Board(33)
		assert difference == vector(1, 2)
		assert self.other + difference == self.position
		assert (self.position + self.displacement) - self.displacement == self.position
		assert type(self.position + self.displacement) is self.Board
		assert type(difference) is vector

	@pytest.mark.parametrize("components", invalid_coordinates)
	def test_coordinate_bounds(self, components) -> None:
		with pytest.raises(ValueError):
			self.Board.from_vector(components)

	@pytest.mark.parametrize("encoded", invalid_values)
	def test_encoded_bounds(self, encoded) -> None:
		with pytest.raises(ValueError):
			self.Board(encoded)

	@pytest.mark.parametrize("operation", translations)
	def test_translation_bounds_and_dimension(self, operation) -> None:
		with pytest.raises(ValueError):
			operation(self.position, vector(1))

		with pytest.raises(ValueError):
			operation(self.Board(0), vector(-1, 8))

	@pytest.mark.parametrize("index_type", index_types)
	def test_serialization(self, index_type) -> None:
		value = index_type(1)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is index_type

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert result.vector == value.vector
			assert type(result) is index_type


class TestFraction:

	class Derived(fraction):
		...

	value = fraction(2, 3)
	positive_infinity = fraction(1, 0)
	negative_infinity = fraction(-1, 0)
	nan = fraction(0, 0)
	normalization = ((2, 4, (1, 2)), (2, -4, (-1, 2)), (-2, -4, (1, 2)), (0, -4, (0, 1)), (9, 0, (1, 0)), (0, 0, (0, 0)))
	finite_pairs = (((2, 3), (-2, 5)), ((7, -3), (5, 2)), ((2 ** 60 + 1, 7), (3, 4)))
	operations = (operator.add, operator.sub, operator.mul, operator.truediv)
	reflected = ((operator.add, (5, 3)), (operator.sub, (1, 3)), (operator.mul, (2, 3)), (operator.truediv, (3, 2)))
	nonfinite = (
		(operator.add, positive_infinity, positive_infinity, (1, 0)),
		(operator.add, negative_infinity, negative_infinity, (-1, 0)),
		(operator.add, positive_infinity, negative_infinity, (0, 0)),
		(operator.add, positive_infinity, value, (1, 0)),
		(operator.sub, positive_infinity, positive_infinity, (0, 0)),
		(operator.sub, negative_infinity, positive_infinity, (-1, 0)),
		(operator.mul, positive_infinity, 0, (0, 0)),
		(operator.mul, negative_infinity, -2, (1, 0)),
		(operator.truediv, positive_infinity, negative_infinity, (0, 0)),
		(operator.truediv, value, negative_infinity, (0, 1)),
		(operator.truediv, value, 0, (1, 0)),
		(operator.truediv, fraction(0), 0, (0, 0)),
	)
	comparators = (operator.eq, operator.ne, operator.lt, operator.le, operator.gt, operator.ge)
	comparisons = (
		(value, fraction(4, 6), Fraction(2, 3), Fraction(2, 3)),
		(fraction(-3, 2), value, Fraction(-3, 2), Fraction(2, 3)),
		(fraction(1), 1, 1, 1),
		(negative_infinity, value, -math.inf, Fraction(2, 3)),
		(value, positive_infinity, Fraction(2, 3), math.inf),
		(negative_infinity, positive_infinity, -math.inf, math.inf),
		(positive_infinity, positive_infinity, math.inf, math.inf),
		(nan, value, math.nan, Fraction(2, 3)),
		(value, nan, Fraction(2, 3), math.nan),
		(nan, nan, math.nan, math.nan),
	)
	powers = (-2, 0, 3)
	special_powers = ((fraction(0), -1, (1, 0)), (fraction(0), 0, (1, 1)), (positive_infinity, -1, (0, 1)),
		(negative_infinity, 3, (-1, 0)), (nan, -1, (0, 0)), (nan, 0, (1, 1)))
	protected_attributes = ("numerator", "denominator")
	serialization_values = (value, Derived(2, 3), positive_infinity, negative_infinity, nan)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("numerator, denominator, expected", normalization)
	def test_normalization(self, numerator, denominator, expected) -> None:
		assert fraction(numerator, denominator).as_integer_ratio == expected

	@pytest.mark.parametrize("operation", operations)
	@pytest.mark.parametrize("left, right", finite_pairs)
	def test_finite_arithmetic(self, operation, left, right) -> None:
		result = operation(fraction(*left), fraction(*right))
		expected = operation(Fraction(*left), Fraction(*right))
		assert result.as_integer_ratio == (expected.numerator, expected.denominator)

	@pytest.mark.parametrize("operation, expected", reflected)
	def test_reflected_arithmetic(self, operation, expected) -> None:
		assert operation(1, self.value).as_integer_ratio == expected

	@pytest.mark.parametrize("operation, left, right, expected", nonfinite)
	def test_nonfinite_arithmetic(self, operation, left, right, expected) -> None:
		assert operation(left, right).as_integer_ratio == expected

	@pytest.mark.parametrize("operation", operations)
	def test_nan_propagation(self, operation) -> None:
		assert operation(self.value, self.nan).as_integer_ratio == (0, 0)
		assert operation(self.nan, self.value).as_integer_ratio == (0, 0)

	@pytest.mark.parametrize("comparator", comparators)
	def test_comparisons(self, comparator) -> None:
		for left, right, reference_left, reference_right in self.comparisons:
			assert comparator(left, right) is comparator(reference_left, reference_right)

	@pytest.mark.parametrize("exponent", powers)
	def test_integer_powers(self, exponent) -> None:
		result = self.value ** exponent
		expected = Fraction(2, 3) ** exponent
		assert result.as_integer_ratio == (expected.numerator, expected.denominator)

	@pytest.mark.parametrize("value, exponent, expected", special_powers)
	def test_nonfinite_powers(self, value, exponent, expected) -> None:
		assert (value ** exponent).as_integer_ratio == expected

	def test_unary_operations(self) -> None:
		assert (+self.value).as_integer_ratio == (2, 3)
		assert (-self.value).as_integer_ratio == (-2, 3)
		assert abs(-self.value).as_integer_ratio == (2, 3)
		assert (~self.value).as_integer_ratio == (3, 2)
		assert sum((self.value, self.value, self.value)) == 2
		assert not fraction(0)
		assert bool(self.positive_infinity)
		assert bool(self.nan)

	def test_subclass_results(self) -> None:
		value = self.Derived(self.value)
		assert type(value + 1) is self.Derived
		assert type(value * 2) is self.Derived
		assert type(-value) is self.Derived

	def test_hashing(self) -> None:
		assert self.value == fraction(4, 6)
		assert hash(self.value) == hash(fraction(4, 6))
		assert hash(fraction(3)) == hash(3)
		assert hash(self.positive_infinity) == hash(math.inf)
		assert hash(self.negative_infinity) == hash(-math.inf)
		assert {self.value: "value"}[fraction(4, 6)] == "value"

	@pytest.mark.parametrize("attribute", protected_attributes)
	def test_immutability(self, attribute) -> None:
		with pytest.raises(AttributeError):
			setattr(self.value, attribute, 9)

		with pytest.raises(AttributeError):
			delattr(self.value, attribute)

	@pytest.mark.parametrize("value", serialization_values)
	def test_serialization(self, value) -> None:
		for copier in self.copy_functions:
			result = copier(value)
			assert result.as_integer_ratio == value.as_integer_ratio
			assert type(result) is type(value)

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result.as_integer_ratio == value.as_integer_ratio
			assert type(result) is type(value)


class TestCollection:

	class Derived(collection[int]):
		...

	collection_types = (collection, Derived)
	items = (1, 2)
	other = (2, 3)
	operations = (
		(operator.or_, "union", {1, 2, 3}),
		(operator.and_, "intersection", {2}),
		(operator.sub, "difference", {1}),
		(operator.xor, "symmetric_difference", {1, 3}),
	)
	commutative = (operator.or_, operator.and_, operator.xor)
	in_place = ((operator.ior, {1, 2, 3}), (operator.iand, {2}), (operator.isub, {1}), (operator.ixor, {1, 3}))
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_construction_and_set_laws(self, collection_type) -> None:
		left = collection_type(*self.items, *self.items)
		right = collection_type(*self.other)
		empty = collection_type()
		assert left == set(self.items)
		assert left | empty == left & left == left
		assert left - left == left ^ left == empty
		assert left | right == right | left
		assert left & right == right & left
		assert left ^ right == (left - right) | (right - left)
		assert (left - right) | (left & right) == left

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation, method, expected", operations)
	def test_operations(self, collection_type, operation, method, expected) -> None:
		value = collection_type(*self.items)

		for result in (operation(value, self.other), getattr(value, method)(self.other)):
			assert result == expected
			assert type(result) is collection_type

		assert value == set(self.items)

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation", commutative)
	def test_reflected_operations(self, collection_type, operation) -> None:
		value = collection_type(*self.items)
		result = operation(self.other, value)
		assert result == operation(set(self.items), set(self.other))
		assert type(result) is collection_type

	def test_difference_preserves_source_type(self) -> None:
		result = set(self.other) - self.Derived(*self.items)
		assert result == {3}
		assert type(result) is set

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation, expected", in_place)
	def test_in_place_operations(self, collection_type, operation, expected) -> None:
		value = collection_type(*self.items)
		result = operation(value, set(self.other))
		assert result == expected
		assert result is value

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_multiple_operands(self, collection_type) -> None:
		value = collection_type(*self.items)
		assert value.union(self.other, (3, 4)) == {1, 2, 3, 4}
		assert value.intersection(self.other, (2, 4)) == {2}
		assert value.difference(self.other, (4,)) == {1}

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_serialization(self, collection_type) -> None:
		value = collection_type(*self.items)

		for copier in (collection_type.copy, *self.copy_functions):
			result = copier(value)
			assert result == value
			assert type(result) is collection_type
			assert result is not value

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is collection_type


class TestVectors:

	class Derived(vectors):
		...

	collection_types = (vectors, Derived)
	left = vectors(vector(0, 0), vector(1, 0))
	right = vectors(vector(0, 1), vector(1, 1))
	third = vectors(vector(0, -1), vector(-1, 0))
	additions = (
		(right, {vector(0, 1), vector(1, 1), vector(2, 1)}),
		(((0, 1), (1, 1)), {vector(0, 1), vector(1, 1), vector(2, 1)}),
		((1, -1), {vector(1, 1), vector(2, 1), vector(-1, -1), vector(0, -1)}),
	)
	scalars = ((2, {vector(0, 0), vector(2, 0)}), (-1, {vector(0, 0), vector(-1, 0)}), (0, {vector(0, 0)}))
	set_operations = (operator.or_, operator.and_, operator.sub, operator.xor)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("other, expected", additions)
	def test_pairwise_addition(self, collection_type, other, expected) -> None:
		value = collection_type(*self.left)
		assert value + other == other + value == expected
		assert type(value + other) is collection_type

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("scalar, expected", scalars)
	def test_scalar_multiplication(self, collection_type, scalar, expected) -> None:
		value = collection_type(*self.left)
		assert value * scalar == scalar * value == expected
		assert type(value * scalar) is collection_type

	def test_vector_set_laws(self) -> None:
		assert self.left + vectors(vector(0, 0)) == self.left
		assert (self.left + self.right) + self.third == self.left + (self.right + self.third)
		assert self.left + (self.right | self.third) == (self.left + self.right) | (self.left + self.third)
		assert (self.left + self.right) * 2 == self.left * 2 + self.right * 2
		assert self.left + vectors() == vectors() + self.left == vectors()
		assert vectors() * 2 == vectors()

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation", set_operations)
	def test_inherited_set_operations(self, collection_type, operation) -> None:
		value = collection_type(*self.left)
		result = operation(value, self.right)
		assert result == operation(set(self.left), set(self.right))
		assert type(result) is collection_type

	def test_dimension_mismatch(self) -> None:
		with pytest.raises(ValueError):
			_ = self.left + vectors(vector(1))

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_serialization(self, collection_type) -> None:
		value = collection_type(*self.left)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is collection_type

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is collection_type
