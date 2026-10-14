from __future__ import annotations


import copy
import math
import operator
import pickle

from fractions import Fraction

import pytest

from goochess.mathematics import array, arrays, collection, fraction, index, indices


class TestArray:

	class Derived(array):
		...

	class Key:

		def __index__(self) -> int:
			return 1

	array_types = (array, Derived)
	components = ((), (2,), (0, 0), (2, -3, 4))
	value = array(2, -3, 4)
	other = array(5, 1, -2)
	empty = array()
	zeros = array(0, 0, 0)
	empty_arithmetic = (
		(operator.add, value, value),
		(operator.sub, value, -value),
		(operator.mul, zeros, zeros),
	)
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
	mismatched_zeros = (array(0), array(0, 0), array(0, 0, 0, 0))
	in_place = ((operator.iadd, (7, -2, 2)), (operator.isub, (-3, -4, 6)), (operator.imul, (10, -3, -8)))
	invalid_keys = (None, "x", 1.5)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("components", components)
	def test_construction(self, array_type, components) -> None:
		value = array_type(*components)
		assert type(value) is array_type
		assert value == components
		assert len(value) == len(components)
		assert bool(value) is any(components)
		assert hash(value) == hash(components)

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("operation, other, expected", arithmetic)
	def test_arithmetic(self, array_type, operation, other, expected) -> None:
		value = array_type(*self.value)
		result = operation(value, other)
		assert result == expected
		assert type(result) is array_type
		assert value == self.value

	@pytest.mark.parametrize("operation, other, expected", reflected)
	def test_reflected_arithmetic(self, operation, other, expected) -> None:
		assert operation(other, self.value) == expected

	def test_array_laws(self) -> None:
		assert (self.value + self.other) - self.other == self.value
		assert self.value + self.other == self.other + self.value
		assert (self.value + self.other) * 2 == self.value * 2 + self.other * 2
		assert self.value + 0 == self.value * 1 == +self.value
		assert -self.value == (-2, 3, -4)
		assert sum((self.value, self.other)) == (7, -2, 2)
		assert sum((self.value, self.other), self.empty) == (7, -2, 2)
		assert array() + array() == array()

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("operation, expected, reflected", empty_arithmetic)
	def test_empty_array_arithmetic(self, array_type, operation, expected, reflected) -> None:
		value = array_type(*self.value)
		empty = array_type()
		result = operation(value, empty)
		reversed_result = operation(empty, value)
		assert result == expected
		assert reversed_result == reflected
		assert type(result) is array_type
		assert type(reversed_result) is array_type

	def test_dot_product_and_squared_norm(self) -> None:
		assert self.value @ self.other == self.other @ self.value == -1
		assert self.value @ 2 == 2 @ self.value == 6
		assert self.value @ self.empty == self.empty @ self.value == 0
		assert abs(self.value) == self.value @ self.value == 29
		assert abs(array()) == 0

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("key, expected", slices)
	def test_coordinates_and_slices(self, array_type, key, expected) -> None:
		value = array_type(*self.value)
		assert value[0] == 2
		assert value[-1] == 4
		assert value[self.Key()] == -3
		result = value[key]
		assert result == expected
		assert type(result) is tuple

	@pytest.mark.parametrize("key", invalid_keys)
	def test_invalid_subscription(self, key) -> None:
		with pytest.raises(TypeError):
			_ = self.value[key]

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("operation, expected", in_place)
	def test_augmented_arithmetic(self, array_type, operation, expected) -> None:
		value = array_type(*self.value)
		result = operation(value, self.other)
		assert result == expected
		assert type(result) is array_type
		assert value == self.value

	@pytest.mark.parametrize("operation", strict_operations)
	def test_dimension_mismatch(self, operation) -> None:
		with pytest.raises(ValueError):
			operation(self.value, array(1, 2))

	@pytest.mark.parametrize("operation", strict_operations)
	@pytest.mark.parametrize("other", mismatched_zeros)
	def test_zero_arrays_keep_dimension(self, operation, other) -> None:
		with pytest.raises(ValueError):
			operation(self.value, other)

		with pytest.raises(ValueError):
			operation(other, self.value)

	@pytest.mark.parametrize("array_type", array_types)
	@pytest.mark.parametrize("components", components)
	def test_serialization(self, array_type, components) -> None:
		value = array_type(*components)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is array_type

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is array_type
			assert hash(result) == hash(value)


class TestIndex:

	class Binary(index, dimension = 3, base = 2):
		...

	class Board(index, dimension = 2, base = 8):
		...

	class Decimal(index, dimension = 3, base = 10):
		...

	template = index.__class_getitem__((2, 8))
	nested_template = template.__class_getitem__((3, 4))
	index_types = (Binary, Board, Decimal, template, nested_template)
	encoding = ((Binary, (1, 0, 1), 5), (Board, (2, 3), 26), (Decimal, (3, 2, 1), 123))
	position = Board((2, 3))
	other = Board((1, 1))
	displacement = array(1, -1)
	empty_displacement = array()
	padding = ((0, (0, 0)), (1, (1, 0)), (7, (7, 0)), (8, (0, 1)))
	slices = ((slice(1, None), (3,)), (slice(None, None, -1), (3, 2)), (slice(0, 0), ()))
	invalid_coordinates = ((), (1,), (1, 2, 3), (-1, 2), (8, 1))
	translations = (operator.add, operator.sub)
	rays = (
		(Board((5, 0)), array(1, 0), ((6, 0), (7, 0))),
		(Board((1, 2)), array(-1, 0), ((0, 2),)),
		(Binary((0, 0, 0)), array(1, 1, 1), ((1, 1, 1),)),
		(Board((0, 0)), array(8, 0), ()),
	)
	invalid_steps = (array(0, 0), array(1), array(1, 1, 1))
	arithmetic = (
		(operator.add, position, displacement, Board(19)),
		(operator.add, displacement, position, Board(19)),
		(operator.sub, position, displacement, Board(33)),
		(operator.sub, position, other, array(1, 2)),
		(operator.add, array(1, 1), Board(0), Board(9)),
	)
	invalid_keys = TestArray.invalid_keys
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("index_type, components, encoded", encoding)
	def test_encoding(self, index_type, components, encoded) -> None:
		assert index_type(components) == index_type(encoded) == encoded
		assert index_type.from_sequence(array(*components)) == encoded
		assert index_type(encoded).array == components

	@pytest.mark.parametrize("index_type", index_types)
	def test_round_trip(self, index_type) -> None:
		assert index_type.lower == 0
		assert index_type.upper == index_type.base ** index_type.dimension

		for encoded in range(index_type.lower, index_type.upper):
			value = index_type(encoded)
			assert len(value.array) == index_type.dimension
			assert index_type.from_sequence(value.array) == value

	@pytest.mark.parametrize("encoded, components", padding)
	def test_padding(self, encoded, components) -> None:
		assert self.Board(encoded).array == components

	@pytest.mark.parametrize("key, expected", slices)
	def test_projection(self, key: slice, expected: tuple[int, ...]) -> None:
		result = self.position[key]
		assert result.array == expected
		assert result.dimension == len(expected)
		assert result.base == self.position.base

	def test_coordinates(self) -> None:
		assert self.position[0] == self.position[-2] == 2
		assert self.position[1] == self.position[-1] == 3
		assert self.position[TestArray.Key()] == 3

		with pytest.raises(IndexError):
			_ = self.position[2]

	def test_specializations(self) -> None:
		assert index.__class_getitem__((2, 8)) is self.template
		assert self.template.__class_getitem__((3, 4)) is self.nested_template
		assert issubclass(self.nested_template, self.template)
		assert (self.template.dimension, self.template.base) == (2, 8)
		assert (self.nested_template.dimension, self.nested_template.base) == (3, 4)
		assert self.Board.__class_getitem__((2, 8)) is not self.template

	@pytest.mark.parametrize("key", invalid_keys)
	def test_invalid_subscription(self, key) -> None:
		with pytest.raises(TypeError):
			_ = self.position[key]

	@pytest.mark.parametrize("operation, left, right, expected", arithmetic)
	def test_arithmetic(self, operation, left, right, expected) -> None:
		result = operation(left, right)
		assert result == expected
		assert type(result) is type(expected)

	def test_translation_laws(self) -> None:
		difference = self.position - self.other
		assert self.other + difference == self.position
		assert difference + self.other == self.position
		assert (self.position + self.displacement) - self.displacement == self.position
		assert (self.position - self.displacement) + self.displacement == self.position

	@pytest.mark.parametrize("index_type", index_types)
	def test_empty_displacement(self, index_type) -> None:
		position = index_type(0)

		for result in (
			position + self.empty_displacement,
			self.empty_displacement + position,
			position - self.empty_displacement,
		):
			assert result == position
			assert type(result) is index_type

	def test_augmented_translation_and_difference(self) -> None:
		position = self.position
		position += self.displacement
		assert type(position) is self.Board
		assert position == self.Board(19)
		position -= self.displacement
		assert position == self.position
		difference = operator.isub(position, self.other)
		assert type(difference) is array
		assert difference == array(1, 2)

	@pytest.mark.parametrize("position, step, expected", rays)
	def test_range(self, position, step, expected) -> None:
		result = tuple(position.range(step))
		assert tuple(item.array for item in result) == expected
		assert all(type(item) is type(position) for item in result)
		assert tuple(position.range(step, True)) == ()

	@pytest.mark.parametrize("step", invalid_steps)
	def test_invalid_range_direction(self, step) -> None:
		with pytest.raises(ValueError):
			tuple(self.position.range(step))

	@pytest.mark.parametrize("components", invalid_coordinates)
	def test_coordinate_bounds(self, components) -> None:
		with pytest.raises(ValueError):
			self.Board.from_sequence(components)

	@pytest.mark.parametrize("index_type", index_types)
	def test_encoded_bounds(self, index_type) -> None:
		for encoded in (index_type.lower - 1, index_type.upper):

			with pytest.raises(ValueError):
				index_type(encoded)

	@pytest.mark.parametrize("operation", translations)
	def test_translation_bounds_and_dimension(self, operation) -> None:
		with pytest.raises(ValueError):
			operation(self.position, array(1))

		with pytest.raises(ValueError):
			operation(self.Board(0), array(-1, 8))

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
			assert result.array == value.array
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
	items = (0, 1, 2)
	other = (2, 3)
	operations = (
		(operator.or_, "union", {0, 1, 2, 3}),
		(operator.and_, "intersection", {2}),
		(operator.sub, "difference", {0, 1}),
		(operator.xor, "symmetric_difference", {0, 1, 3}),
	)
	commutative = (operator.or_, operator.and_, operator.xor)
	in_place = ((operator.ior, {0, 1, 2, 3}), (operator.iand, {2}), (operator.isub, {0, 1}), (operator.ixor, {0, 1, 3}))
	operand_types = (set, tuple, iter)
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
	@pytest.mark.parametrize("operand_type", operand_types)
	def test_in_place_operations(self, collection_type, operation, expected, operand_type) -> None:
		value = collection_type(*self.items)
		result = operation(value, operand_type(self.other))
		assert result == expected
		assert result is value

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_multiple_operands(self, collection_type) -> None:
		value = collection_type(*self.items)
		assert value.union(self.other, (3, 4)) == {0, 1, 2, 3, 4}
		assert value.intersection(self.other, (2, 4)) == {2}
		assert value.difference(self.other, (4,)) == {0, 1}

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


class TestArrays:

	class Derived(arrays):
		...

	collection_types = (arrays, Derived)
	left = arrays(array(0, 0), array(1, 0))
	right = arrays(array(0, 1), array(1, 1))
	third = arrays(array(0, -1), array(-1, 0))
	unit = arrays(array())
	forward = arrays(array(1, 0))
	backward = arrays(array(-1, 0))
	directions = forward | backward
	zero_vectors = arrays(array(), array(0), array(0, 0))
	zero_removals = (
		(array(), {(0,), (0, 0)}),
		(array(0), {(), (0, 0)}),
		(array(0, 0), {(), (0,)}),
	)
	products = (
		(right, {array(0, 1), array(1, 1), array(2, 1)}),
		(((0, 1), (1, 1)), {array(0, 1), array(1, 1), array(2, 1)}),
		((1, -1), {array(1, 1), array(2, 1), array(-1, -1), array(0, -1)}),
	)
	scalars = (
		(2, {array(0, 0), array(2, 0)}),
		(0, set()),
		(1, set(left)),
	)
	powers = (
		(1, set(left)),
		(2, {array(0, 0), array(1, 0), array(2, 0)}),
		(3, {array(0, 0), array(1, 0), array(2, 0), array(3, 0)}),
		(True, set(left)),
	)
	power_pairs = ((1, 1), (1, 2), (2, 3))
	unsupported_powers = (0, -1, False)
	set_operations = (operator.or_, operator.and_, operator.sub, operator.xor)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("other, expected", products)
	def test_pairwise_product(self, collection_type, other, expected) -> None:
		value = collection_type(*self.left)
		assert value * other == other * value == expected
		assert value * iter(other) == iter(other) * value == expected
		assert type(value * other) is collection_type

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("other, expected", products)
	def test_augmented_product(self, collection_type, other, expected) -> None:
		value = collection_type(*self.left)
		alias = value
		value *= iter(other)
		assert value == expected
		assert type(value) is collection_type
		assert alias == self.left

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("scalar, expected", scalars)
	def test_scalar_multiplication(self, collection_type, scalar, expected) -> None:
		value = collection_type(*self.left)
		assert value * scalar == scalar * value == expected
		assert type(value * scalar) is collection_type

	def test_array_set_laws(self) -> None:
		assert self.left * arrays(array(0, 0)) == self.left
		assert self.left * self.unit == self.unit * self.left == self.left
		assert (self.left * self.right) * self.third == self.left * (self.right * self.third)
		assert self.left * (self.right | self.third) == (self.left * self.right) | (self.left * self.third)
		assert (self.left * self.right) * 2 == (self.left * 2) * (self.right * 2)
		assert self.left * arrays() == arrays() * self.left == arrays()
		assert arrays() * 2 == arrays()

	def test_cancellation(self) -> None:
		assert self.forward * self.backward == arrays(array(0, 0))
		assert (self.forward * self.backward) * self.right == self.forward * (self.backward * self.right)
		assert self.directions ** 2 == {(-2, 0), (0, 0), (2, 0)}
		assert (self.directions ** 2) * self.directions == self.directions ** 3 == {(-3, 0), (-1, 0), (1, 0), (3, 0)}

	@pytest.mark.parametrize("zero, expected", zero_removals)
	def test_zero_vector_removal(self, zero, expected) -> None:
		result = self.zero_vectors - {zero}
		assert result == expected
		assert type(result) is arrays

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("exponent, expected", powers)
	def test_powers(self, collection_type, exponent, expected) -> None:
		value = collection_type(*self.left)
		result = value ** exponent
		assert result == expected
		assert type(result) is collection_type
		assert value == self.left

	@pytest.mark.parametrize("left, right", power_pairs)
	def test_power_laws(self, left, right) -> None:
		assert (self.left ** left) * (self.left ** right) == self.left ** (left + right)

	def test_empty_and_zero_dimensional_powers(self) -> None:
		assert arrays() ** 1 == arrays() ** 3 == arrays()
		assert self.unit ** 1 == self.unit ** 3 == self.unit

	@pytest.mark.parametrize("exponent", unsupported_powers)
	def test_unsupported_power(self, exponent) -> None:
		with pytest.raises(NotImplementedError):
			_ = self.left ** exponent

	def test_negative_scalar(self) -> None:
		with pytest.raises(NotImplementedError):
			_ = self.left * -1

		with pytest.raises(NotImplementedError):
			_ = -1 * self.left

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_augmented_power(self, collection_type) -> None:
		value = collection_type(*self.left)
		alias = value
		value **= 3
		assert value == {array(0, 0), array(1, 0), array(2, 0), array(3, 0)}
		assert type(value) is collection_type
		assert alias == self.left
		value **= 1
		assert value == alias * alias * alias
		assert type(value) is collection_type

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation", set_operations)
	def test_inherited_set_operations(self, collection_type, operation) -> None:
		value = collection_type(*self.left)
		result = operation(value, self.right)
		assert result == operation(set(self.left), set(self.right))
		assert type(result) is collection_type

	def test_dimension_mismatch(self) -> None:
		with pytest.raises(ValueError):
			_ = self.left * arrays(array(1))

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


class TestIndices:

	class Board(index, dimension = 2, base = 8):
		...

	class Derived(indices):
		...

	collection_types = (indices, Derived)
	positions = (Board(0), Board((1, 1)), Board((2, 1)))
	left = indices(*positions)
	steps = (array(0, 1), array(1, 1))
	unit = arrays(array())
	expected = {Board((0, 1)), Board((1, 1)), Board((1, 2)), Board((2, 2)), Board((3, 2))}
	invalid_steps = (array(1), array(-2, 0))
	set_operations = TestArrays.set_operations
	copy_functions = TestCollection.copy_functions
	pickle_protocols = TestCollection.pickle_protocols

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_pairwise_translation(self, collection_type) -> None:
		value = collection_type(*self.left)

		for other in (self.steps, iter(self.steps)):
			result = value * other
			assert result == self.expected
			assert type(result) is collection_type
			assert all(type(item) is self.Board for item in result)

		assert iter(self.steps) * value == self.expected
		assert value * () == collection_type() * self.steps == collection_type()
		assert value * self.unit == value

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_augmented_translation(self, collection_type) -> None:
		value = collection_type(*self.left)
		value *= self.steps
		assert value == self.expected
		assert type(value) is collection_type
		assert self.left == set(self.positions)

	@pytest.mark.parametrize("step", invalid_steps)
	def test_translation_bounds_and_dimension(self, step) -> None:
		with pytest.raises(ValueError):
			_ = self.left * (step,)

	@pytest.mark.parametrize("collection_type", collection_types)
	@pytest.mark.parametrize("operation", set_operations)
	def test_inherited_set_operations(self, collection_type, operation) -> None:
		value = collection_type(*self.left)
		result = operation(value, self.expected)
		assert result == operation(set(self.left), self.expected)
		assert type(result) is collection_type

	@pytest.mark.parametrize("collection_type", collection_types)
	def test_serialization(self, collection_type) -> None:
		value = collection_type(*self.left)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is collection_type
			assert all(type(item) is self.Board for item in result)

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is collection_type
			assert all(type(item) is self.Board for item in result)
