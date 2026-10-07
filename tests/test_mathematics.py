from __future__ import annotations


import copy
import operator
import pickle
import sys

from fractions import Fraction

import pytest

from mathematics import fraction, index, vector


class TestVector:

	class Derived(vector):
		pass

	class Key:
		def __index__(self) -> int:
			return 1

	value = vector(2, -3, 4)
	other = vector(5, 1, -2)
	empty = vector()
	derived = Derived(2, -3, 4)
	keys = ((0, 2), (-1, 4), (Key(), -3))
	slices = (
		(slice(1, None), vector(-3, 4)),
		(slice(None, None, -1), vector(4, -3, 2)),
		(slice(0, 0), vector()),
	)
	truth_values = ((empty, False), (vector(0, 0), False), (vector(1, -1), True))
	binary_cases = (
		(operator.add, value, other, vector(7, -2, 2)),
		(operator.sub, value, other, vector(-3, -4, 6)),
		(operator.mul, value, other, vector(10, -3, -8)),
		(operator.add, value, tuple(other), vector(7, -2, 2)),
		(operator.sub, value, tuple(other), vector(-3, -4, 6)),
		(operator.mul, value, tuple(other), vector(10, -3, -8)),
		(operator.add, tuple(other), value, vector(7, -2, 2)),
		(operator.sub, tuple(other), value, vector(3, 4, -6)),
		(operator.mul, tuple(other), value, vector(10, -3, -8)),
		(operator.add, value, 2, vector(4, -1, 6)),
		(operator.sub, value, 2, vector(0, -5, 2)),
		(operator.mul, value, 2, vector(4, -6, 8)),
		(operator.add, 2, value, vector(4, -1, 6)),
		(operator.sub, 2, value, vector(0, 5, -2)),
		(operator.mul, 2, value, vector(4, -6, 8)),
	)
	identities = (
		(operator.add, value, 0),
		(operator.add, 0, value),
		(operator.sub, value, 0),
		(operator.mul, value, 1),
		(operator.mul, 1, value),
	)
	dot_products = ((value, other, -1), (value, tuple(other), -1), (tuple(other), value, -1), (value, 2, 6), (2, value, 6))
	truncated_operations = (
		(operator.add, vector(7, -2)),
		(operator.sub, vector(-3, -4)),
		(operator.mul, vector(10, -3)),
		(operator.matmul, 7),
	)
	vector_operations = (operator.add, operator.sub, operator.mul)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = (0, 2, pickle.HIGHEST_PROTOCOL)

	def test_tuple_behavior(self):
		assert tuple(self.value) == (2, -3, 4)
		assert hash(self.value) == hash(tuple(self.value))
		assert repr(self.value) == "vector(2, -3, 4)"
		assert repr(self.empty) == "vector()"

	@pytest.mark.parametrize("value, expected", truth_values)
	def test_truthiness(self, value, expected):
		assert bool(value) is expected

	@pytest.mark.parametrize("key, expected", keys)
	def test_component_access(self, key, expected):
		assert self.value[key] == expected
		assert type(self.value[key]) is int

	@pytest.mark.parametrize("key, expected", slices)
	def test_slices_preserve_type(self, key, expected):
		result = self.derived[key]
		assert result == expected
		assert type(result) is self.Derived

	@pytest.mark.parametrize("operation, left, right, expected", binary_cases)
	def test_arithmetic(self, operation, left, right, expected):
		result = operation(left, right)
		assert result == expected
		assert type(result) is vector

	@pytest.mark.parametrize("operation, left, right", identities)
	def test_scalar_identity_reuses_instance(self, operation, left, right):
		assert operation(left, right) is self.value

	@pytest.mark.parametrize("left, right, expected", dot_products)
	def test_dot_product(self, left, right, expected):
		assert left @ right == expected
		assert type(left @ right) is int

	@pytest.mark.parametrize("operation, expected", truncated_operations)
	def test_unequal_lengths_are_intentionally_truncated(self, operation, expected):
		assert operation(self.value, self.other[:2]) == expected

	@pytest.mark.parametrize("operation", vector_operations)
	def test_empty_arithmetic(self, operation):
		assert operation(self.empty, self.value) == self.empty
		assert operation(self.value, self.empty) == self.empty
		assert operation(self.empty, 2) == self.empty

	@pytest.mark.parametrize("operation", vector_operations)
	def test_arithmetic_preserves_subclass(self, operation):
		result = operation(self.derived, self.other)
		assert type(result) is self.Derived
		assert result == operation(self.value, self.other)

	def test_unary_operations(self):
		assert +self.value is self.value
		assert -self.value == vector(-2, 3, -4)
		assert type(operator.neg(self.derived)) is self.Derived
		assert abs(self.value) == 29
		assert type(abs(self.value)) is int
		assert -self.empty == self.empty
		assert abs(self.empty) == 0

	def test_sum(self):
		result = sum((self.value, self.other))
		assert result == vector(7, -2, 2)
		assert type(result) is vector

	@pytest.mark.parametrize("copier", copy_functions)
	def test_copy(self, copier):
		result = copier(self.derived)
		assert result == self.derived
		assert type(result) is self.Derived

	@pytest.mark.parametrize("protocol", pickle_protocols)
	def test_pickle(self, protocol):
		result = pickle.loads(pickle.dumps(self.derived, protocol = protocol))
		assert result == self.derived
		assert type(result) is self.Derived


class TestIndex:

	class Binary(index, base = 2):
		pass

	class Square(index, base = 8):
		pass

	class Decimal(index, base = 10):
		pass

	position = Square((2, 3))
	other = Square((1, 1))
	displacement = vector(1, -1)
	encoding_cases = (
		(Binary, (1, 0, 1), 5),
		(Square, (2, 3), 26),
		(Square, (7, 7), 63),
		(Square, (7, 1, 1), 79),
		(Decimal, (3, 2, 1), 123),
	)
	zero_tail_cases = (((), ()), ((0, 0), ()), ((2, 3, 0), (2, 3)))
	arithmetic_cases = (
		(operator.add, position, displacement, Square(19)),
		(operator.add, displacement, position, Square(19)),
		(operator.add, position, tuple(displacement), Square(19)),
		(operator.add, tuple(displacement), position, Square(19)),
		(operator.sub, position, displacement, Square(33)),
		(operator.sub, position, tuple(displacement), Square(33)),
		(operator.sub, position, other, vector(1, 2)),
		(operator.sub, position, int(other), vector(1, 2)),
		(operator.sub, position, position, vector(0, 0)),
	)
	invalid_coordinates = ((-1,), (8,), (-1, 2), (8, 1))
	invalid_movements = (
		(operator.add, Square((7, 1)), vector(1, 0)),
		(operator.sub, Square((0, 2)), vector(1, 0)),
		(operator.sub, Square(1), vector(2)),
	)
	unsupported_operations = (
		(operator.sub, displacement, position),
		(operator.mul, displacement, position),
		(operator.mul, position, displacement),
		(operator.matmul, displacement, position),
		(operator.matmul, position, displacement),
	)
	scalar_lookalikes = (Square(0), Square(1))
	copy_functions = (copy.copy, copy.deepcopy)

	@pytest.mark.parametrize("position_type, coordinates, encoded", encoding_cases)
	def test_encoding_and_decoding(self, position_type, coordinates, encoded):
		for source in (coordinates, vector(*coordinates), encoded):
			result = position_type(source)
			assert result == encoded
			assert type(result) is position_type
			assert result.vector == coordinates
			assert type(result.vector) is vector

	@pytest.mark.parametrize("coordinates, decoded", zero_tail_cases)
	def test_decoding_intentionally_discards_trailing_zeros(self, coordinates, decoded):
		assert self.Square(coordinates).vector == decoded

	@pytest.mark.parametrize("operation, left, right, expected", arithmetic_cases)
	def test_position_arithmetic(self, operation, left, right, expected):
		result = operation(left, right)
		assert result == expected
		assert type(result) is type(expected)

	def test_equal_length_displacement_round_trip(self):
		assert self.other + (self.position - self.other) == self.position
		assert (self.position + self.displacement) - self.displacement == self.position

	def test_translation_uses_truncating_vector_operations(self):
		assert self.position + vector(1) == self.Square(3)
		assert self.Square(2) + vector(1, 1) == self.Square(3)

	@pytest.mark.parametrize("coordinates", invalid_coordinates)
	def test_invalid_coordinates(self, coordinates):
		with pytest.raises(ValueError):
			self.Square(coordinates)

	def test_negative_encoded_position(self):
		with pytest.raises(ValueError):
			self.Square(-1)

	@pytest.mark.parametrize("operation, position, displacement", invalid_movements)
	def test_translation_rejects_out_of_bounds_coordinates(self, operation, position, displacement):
		with pytest.raises(ValueError):
			operation(position, displacement)

	@pytest.mark.parametrize("operation, left, right", unsupported_operations)
	def test_unsupported_position_operations(self, operation, left, right):
		with pytest.raises(TypeError):
			operation(left, right)

	@pytest.mark.parametrize("position", scalar_lookalikes)
	def test_positions_are_not_scalar_identities(self, position):
		assert self.displacement.__add__(position) is NotImplemented
		assert self.displacement.__sub__(position) is NotImplemented
		assert self.displacement.__mul__(position) is NotImplemented
		assert type(vector(1) + position) is self.Square

	@pytest.mark.parametrize("copier", copy_functions)
	def test_copy(self, copier):
		result = copier(self.position)
		assert result == self.position
		assert type(result) is self.Square

	def test_pickle(self):
		result = pickle.loads(pickle.dumps(self.position))
		assert result == self.position
		assert type(result) is self.Square
		assert result.vector == self.position.vector


class TestFraction:

	class Derived(fraction):
		pass

	class Slotted(fraction):
		__slots__ = ()

	class WithSlot(fraction):
		__slots__ = ("notes",)

	class Reflected:
		def __radd__(self, other): return "add"
		def __rsub__(self, other): return "sub"
		def __rmul__(self, other): return "mul"
		def __rtruediv__(self, other): return "div"

	value = fraction(2, 3)
	derived = Derived(2, 3)
	positive_infinity = fraction(1, 0)
	negative_infinity = fraction(-1, 0)
	nan = fraction(0, 0)
	reflected = Reflected()
	normalization_cases = (
		(2, 4, (1, 2)),
		(-2, 4, (-1, 2)),
		(2, -4, (-1, 2)),
		(-2, -4, (1, 2)),
		(1, -1, (-1, 1)),
		(0, -4, (0, 1)),
		(9, 0, (1, 0)),
		(-9, 0, (-1, 0)),
		(0, 0, (0, 0)),
	)
	truth_values = ((fraction(0), False), (value, True), (positive_infinity, True), (negative_infinity, True), (nan, True))
	finite_operands = ((2, 3), (-2, 5), (7, -3), (2 ** 60 + 1, 7))
	binary_operations = (operator.add, operator.sub, operator.mul, operator.truediv)
	nonfinite_arithmetic = (
		(operator.add, positive_infinity, positive_infinity, (1, 0)),
		(operator.add, negative_infinity, negative_infinity, (-1, 0)),
		(operator.add, positive_infinity, negative_infinity, (0, 0)),
		(operator.add, positive_infinity, value, (1, 0)),
		(operator.add, value, negative_infinity, (-1, 0)),
		(operator.sub, positive_infinity, positive_infinity, (0, 0)),
		(operator.sub, positive_infinity, negative_infinity, (1, 0)),
		(operator.sub, negative_infinity, positive_infinity, (-1, 0)),
		(operator.sub, value, positive_infinity, (-1, 0)),
		(operator.mul, positive_infinity, 0, (0, 0)),
		(operator.mul, positive_infinity, -2, (-1, 0)),
		(operator.mul, negative_infinity, negative_infinity, (1, 0)),
		(operator.truediv, positive_infinity, -2, (-1, 0)),
		(operator.truediv, negative_infinity, -2, (1, 0)),
		(operator.truediv, positive_infinity, negative_infinity, (0, 0)),
		(operator.truediv, value, negative_infinity, (0, 1)),
		(operator.truediv, value, 0, (1, 0)),
		(operator.truediv, fraction(-2, 3), 0, (-1, 0)),
		(operator.truediv, fraction(0), 0, (0, 0)),
	)
	comparators = (operator.eq, operator.ne, operator.lt, operator.le, operator.gt, operator.ge)
	comparison_values = (
		(negative_infinity, float("-inf")),
		(fraction(-3, 2), Fraction(-3, 2)),
		(-1, -1),
		(fraction(0), Fraction(0)),
		(0, 0),
		(value, Fraction(2, 3)),
		(fraction(4, 6), Fraction(2, 3)),
		(fraction(2 ** 60 + 1), Fraction(2 ** 60 + 1)),
		(positive_infinity, float("inf")),
		(nan, float("nan")),
	)
	unsupported_operands = (object(), None, "2", 0.5)
	arithmetic_methods = ("__add__", "__sub__", "__mul__", "__truediv__", "__radd__", "__rsub__", "__rmul__", "__rtruediv__")
	comparison_methods = ("__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__")
	ordering_operations = (operator.lt, operator.le, operator.gt, operator.ge)
	serialization_values = (value, derived, Slotted(2, 3), WithSlot(2, 3), fraction(0), positive_infinity, negative_infinity, nan)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))
	immutability_types = (fraction, Derived, Slotted, WithSlot)
	dictionary_free_types = (fraction, Slotted, WithSlot)
	metadata_types = (Derived, WithSlot)
	protected_attributes = ("numerator", "denominator", "as_integer_ratio", "inverse")
	reinitialization_inputs = (9, fraction(9, 7))
	repr_cases = ((value, "+2/3"), (negative_infinity, "-1/0"), (nan, "+0/0"))
	inverse_cases = ((value, (3, 2)), (fraction(0), (1, 0)), (negative_infinity, (0, 1)), (nan, (0, 0)))
	in_place_operations = (
		(operator.iadd, 1, (5, 3)),
		(operator.isub, 1, (-1, 3)),
		(operator.imul, 2, (4, 3)),
		(operator.itruediv, 2, (1, 3)),
		(operator.ipow, -2, (9, 4)),
	)
	arithmetic_cases = (
		(operator.add, (derived, 1), (5, 3)),
		(operator.add, (1, derived), (5, 3)),
		(operator.sub, (derived, 1), (-1, 3)),
		(operator.sub, (1, derived), (1, 3)),
		(operator.mul, (derived, 2), (4, 3)),
		(operator.mul, (2, derived), (4, 3)),
		(operator.truediv, (derived, 2), (1, 3)),
		(operator.truediv, (2, derived), (3, 1)),
		(operator.pos, (derived,), (2, 3)),
		(operator.neg, (derived,), (-2, 3)),
		(abs, (Derived(-2, 3),), (2, 3)),
		(operator.attrgetter("inverse"), (derived,), (3, 2)),
		(operator.add, (Derived(1, 0), Derived(1, 0)), (1, 0)),
		(operator.sub, (Derived(1, 0), Derived(-1, 0)), (1, 0)),
		(operator.truediv, (-2, Derived(0)), (-1, 0)),
	)
	finite_bases = (Fraction(2, 3), Fraction(-2, 3), Fraction(3, -2), Fraction(2 ** 60 + 1, 7))
	exponents = (-3, -2, -1, 0, 1, 2, 3)
	special_powers = (
		(fraction(0), -2, (1, 0)),
		(fraction(0), 0, (1, 1)),
		(fraction(0), 2, (0, 1)),
		(fraction(1, 0), -1, (0, 1)),
		(fraction(1, 0), 0, (1, 1)),
		(fraction(1, 0), 2, (1, 0)),
		(fraction(-1, 0), -1, (0, 1)),
		(fraction(-1, 0), 0, (1, 1)),
		(fraction(-1, 0), 2, (1, 0)),
		(fraction(-1, 0), 3, (-1, 0)),
		(fraction(0, 0), -1, (0, 0)),
		(fraction(0, 0), 0, (1, 1)),
		(fraction(0, 0), 2, (0, 0)),
	)
	unsupported_exponents = (0.5, 2.0, Fraction(1, 2), fraction(1, 2), "2")
	moduli = (0, 5, -5)
	hash_modulus = sys.hash_info.modulus
	hash_cases = (
		(0, 1), (1, 1), (-1, 1), (2, 3), (-2, 3), (2, -3),
		(10 ** 400 + 1, 7), (-10 ** 400 - 1, 7), (7, 10 ** 400 + 1),
		(hash_modulus, 1), (-hash_modulus, 1), (-hash_modulus - 1, 1),
		(1, hash_modulus), (-1, hash_modulus), (1, 2 * hash_modulus),
		(1, hash_modulus ** 2), (hash_modulus, 2 * hash_modulus),
		(-hash_modulus - 2, 2),
	)
	hash_types = (fraction, Derived)
	hash_scales = (2, -3)
	integer_keys = (0, 1, -1, 10 ** 400, -10 ** 400, False, True)
	equivalent_keys = (
		(fraction(2, 3), fraction(4, 6)),
		(value, derived),
		(positive_infinity, fraction(9, 0)),
		(negative_infinity, fraction(-9, 0)),
	)
	infinity_hashes = ((positive_infinity, float("inf")), (negative_infinity, float("-inf")))
	unsupported_numeric_keys = (
		(fraction(1, 2), 0.5),
		(fraction(-3, 4), -0.75),
		(fraction(0), 0.0),
		(fraction(1, 2), Fraction(1, 2)),
	)
	nan_keys = (nan, fraction(0, 0))

	def test_default_construction(self):
		assert fraction().as_integer_ratio == (0, 1)

	@pytest.mark.parametrize("value, expected", repr_cases)
	def test_representation(self, value, expected):
		assert repr(value) == expected

	@pytest.mark.parametrize("value, expected", inverse_cases)
	def test_inverse(self, value, expected):
		assert value.inverse.as_integer_ratio == expected

	@pytest.mark.parametrize("fraction_type", immutability_types)
	@pytest.mark.parametrize("name", protected_attributes)
	def test_assignment_and_deletion_preserve_value_and_hash(self, fraction_type, name):
		value = fraction_type(2, 3)
		original_hash = hash(value)
		mapping = {value: "found"}
		with pytest.raises(AttributeError):
			setattr(value, name, 9)
		with pytest.raises(AttributeError):
			delattr(value, name)
		assert value.as_integer_ratio == (2, 3)
		assert hash(value) == original_hash
		assert mapping[fraction(2, 3)] == "found"

	@pytest.mark.parametrize("fraction_type", dictionary_free_types)
	def test_slots_prevent_an_instance_dictionary_and_extra_attributes(self, fraction_type):
		value = fraction_type(2, 3)
		assert not hasattr(value, "__dict__")
		with pytest.raises(AttributeError):
			value.extra = 1
		with pytest.raises(AttributeError):
			del value.extra

	@pytest.mark.parametrize("fraction_type", immutability_types)
	@pytest.mark.parametrize("source", reinitialization_inputs)
	def test_reinitialization_cannot_change_value(self, fraction_type, source):
		value = fraction_type(2, 3)
		with pytest.raises(AttributeError):
			value.__init__(source)
		assert value.as_integer_ratio == (2, 3)

	@pytest.mark.parametrize("fraction_type", metadata_types)
	def test_subclass_metadata_remains_writable(self, fraction_type):
		value = fraction_type(2, 3)
		original_hash = hash(value)
		value.notes = "initial"
		value.notes = "updated"
		assert value.notes == "updated"
		del value.notes
		assert not hasattr(value, "notes")
		assert value.as_integer_ratio == (2, 3)
		assert hash(value) == original_hash

	@pytest.mark.parametrize("fraction_type", immutability_types)
	@pytest.mark.parametrize("operation, other, expected", in_place_operations)
	def test_augmented_operations_create_new_values(self, fraction_type, operation, other, expected):
		value = fraction_type(2, 3)
		result = operation(value, other)
		assert result is not value
		assert type(result) is fraction_type
		assert result.as_integer_ratio == expected
		assert value.as_integer_ratio == (2, 3)

	def test_sum(self):
		result = sum((self.value, self.value, self.value))
		assert result.as_integer_ratio == (2, 1)

	@pytest.mark.parametrize("fraction_type", hash_types)
	@pytest.mark.parametrize("scale", hash_scales)
	@pytest.mark.parametrize("numerator, denominator", hash_cases)
	def test_equivalent_representations_have_equal_hashes(self, fraction_type, scale, numerator, denominator):
		value = fraction_type(numerator, denominator)
		equivalent = fraction(numerator * scale, denominator * scale)
		assert value == equivalent
		assert hash(value) == hash(equivalent)
		assert {value: "found"}[equivalent] == "found"

	@pytest.mark.parametrize("integer", integer_keys)
	def test_integer_keys_are_interchangeable(self, integer):
		value = fraction(integer)
		assert value == integer
		assert hash(value) == hash(integer)
		assert {value: "found"}[integer] == "found"
		assert {integer: "found"}[value] == "found"
		assert len({value, integer}) == 1

	@pytest.mark.parametrize("left, right", equivalent_keys)
	def test_equal_fraction_keys_are_interchangeable(self, left, right):
		assert left == right
		assert hash(left) == hash(right)
		assert {left: "found"}[right] == "found"
		assert len({left, right}) == 1

	@pytest.mark.parametrize("value, reference", infinity_hashes)
	def test_infinity_hash_matches_float_conventions(self, value, reference):
		assert hash(value) == hash(reference)

	@pytest.mark.parametrize("value, other", unsupported_numeric_keys)
	def test_unsupported_numeric_types_are_distinct_keys(self, value, other):
		assert value != other
		assert other != value
		mapping = {value: "fraction", other: "other"}
		assert len(mapping) == 2
		assert mapping[value] == "fraction"
		assert mapping[other] == "other"

	def test_nan_keys_remain_distinct_and_retrievable(self):
		left, right = self.nan_keys
		assert left != right
		original_hash = hash(left)
		mapping = {left: "left", right: "right"}
		assert hash(left) == original_hash
		assert len(mapping) == 2
		assert mapping[left] == "left"
		assert mapping[right] == "right"

	@pytest.mark.parametrize("numerator, denominator, expected", normalization_cases)
	def test_normalization(self, numerator, denominator, expected):
		assert fraction(numerator, denominator).as_integer_ratio == expected

	@pytest.mark.parametrize("value", serialization_values)
	def test_coercion(self, value):
		result = type(value)(value)
		assert result.as_integer_ratio == value.as_integer_ratio
		assert type(result) is type(value)
		assert result is not value

	@pytest.mark.parametrize("value, expected", truth_values)
	def test_truthiness(self, value, expected):
		assert bool(value) is expected

	@pytest.mark.parametrize("operation", binary_operations)
	@pytest.mark.parametrize("left", finite_operands)
	@pytest.mark.parametrize("right", finite_operands)
	def test_finite_arithmetic_matches_standard_fraction(self, operation, left, right):
		result = operation(fraction(*left), fraction(*right))
		expected = operation(Fraction(*left), Fraction(*right))
		assert result.as_integer_ratio == expected.as_integer_ratio()

	@pytest.mark.parametrize("operation, left, right, expected", nonfinite_arithmetic)
	def test_nonfinite_arithmetic(self, operation, left, right, expected):
		assert operation(left, right).as_integer_ratio == expected

	@pytest.mark.parametrize("operation", binary_operations)
	def test_nan_propagates_through_arithmetic(self, operation):
		assert operation(self.nan, self.value).as_integer_ratio == (0, 0)
		assert operation(self.value, self.nan).as_integer_ratio == (0, 0)

	@pytest.mark.parametrize("comparator", comparators)
	@pytest.mark.parametrize("left, expected_left", comparison_values)
	@pytest.mark.parametrize("right, expected_right", comparison_values)
	def test_comparisons(self, comparator, left, expected_left, right, expected_right):
		assert comparator(left, right) == comparator(expected_left, expected_right)

	@pytest.mark.parametrize("method", comparison_methods)
	@pytest.mark.parametrize("other", unsupported_operands)
	def test_unsupported_comparisons_return_not_implemented(self, method, other):
		assert getattr(self.value, method)(other) is NotImplemented

	@pytest.mark.parametrize("other", unsupported_operands)
	def test_unrelated_equality(self, other):
		assert (self.value == other) is False
		assert (other == self.value) is False
		assert (self.value != other) is True
		assert (other != self.value) is True

	@pytest.mark.parametrize("operation", ordering_operations)
	@pytest.mark.parametrize("other", unsupported_operands)
	def test_unrelated_ordering_is_unsupported(self, operation, other):
		with pytest.raises(TypeError):
			operation(self.value, other)
		with pytest.raises(TypeError):
			operation(other, self.value)

	@pytest.mark.parametrize("method", arithmetic_methods)
	@pytest.mark.parametrize("other", unsupported_operands)
	def test_unsupported_arithmetic_raises_type_error(self, method, other):
		with pytest.raises(TypeError):
			getattr(self.value, method)(other)

	@pytest.mark.parametrize("operation", binary_operations)
	def test_unsupported_arithmetic_does_not_try_reflected_fallback(self, operation):
		with pytest.raises(TypeError):
			operation(self.value, self.reflected)

	@pytest.mark.parametrize("copier", copy_functions)
	@pytest.mark.parametrize("value", serialization_values)
	def test_copy(self, copier, value):
		result = copier(value)
		assert result.as_integer_ratio == value.as_integer_ratio
		assert type(result) is type(value)
		assert result is not value
		with pytest.raises(AttributeError):
			result.numerator = 9
		with pytest.raises(AttributeError):
			del result.denominator

	@pytest.mark.parametrize("protocol", pickle_protocols)
	@pytest.mark.parametrize("value", serialization_values)
	def test_pickle(self, protocol, value):
		result = pickle.loads(pickle.dumps(value, protocol = protocol))
		assert result.as_integer_ratio == value.as_integer_ratio
		assert type(result) is type(value)
		with pytest.raises(AttributeError):
			result.numerator = 9
		with pytest.raises(AttributeError):
			del result.denominator

	@pytest.mark.parametrize("fraction_type", metadata_types)
	def test_copy_preserves_subclass_metadata(self, fraction_type):
		value = fraction_type(2, 3)
		value.notes = ["original"]
		shallow = copy.copy(value)
		deep = copy.deepcopy(value)
		assert shallow.notes is value.notes
		assert deep.notes == value.notes
		assert deep.notes is not value.notes
		assert shallow.as_integer_ratio == deep.as_integer_ratio == value.as_integer_ratio
		assert type(shallow) is type(deep) is fraction_type

	@pytest.mark.parametrize("fraction_type", metadata_types)
	@pytest.mark.parametrize("protocol", pickle_protocols)
	def test_pickle_preserves_subclass_metadata(self, fraction_type, protocol):
		value = fraction_type(2, 3)
		value.notes = ["original"]
		result = pickle.loads(pickle.dumps(value, protocol = protocol))
		assert result.as_integer_ratio == value.as_integer_ratio
		assert type(result) is fraction_type
		assert result.notes == value.notes

	@pytest.mark.parametrize("base", finite_bases)
	@pytest.mark.parametrize("exponent", exponents)
	def test_integer_powers_are_exact(self, base, exponent):
		value = fraction(base.numerator, base.denominator)
		result = value ** exponent
		expected = base ** exponent
		assert type(result) is fraction
		assert (result.numerator, result.denominator) == (expected.numerator, expected.denominator)
		assert (value.numerator, value.denominator) == (base.numerator, base.denominator)

	@pytest.mark.parametrize("value, exponent, expected", special_powers)
	def test_special_powers(self, value, exponent, expected):
		result = value ** exponent
		assert (result.numerator, result.denominator) == expected

	@pytest.mark.parametrize("exponent", exponents)
	def test_powers_preserve_subclass(self, exponent):
		assert type(self.derived ** exponent) is self.Derived

	@pytest.mark.parametrize("operation, arguments, expected", arithmetic_cases)
	def test_arithmetic_preserves_subclass(self, operation, arguments, expected):
		result = operation(*arguments)
		assert type(result) is self.Derived
		assert result.as_integer_ratio == expected

	@pytest.mark.parametrize("exponent", unsupported_exponents)
	def test_unsupported_exponents(self, exponent):
		with pytest.raises(TypeError):
			_ = self.value ** exponent

	@pytest.mark.parametrize("modulus", moduli)
	def test_modular_powers_are_unsupported(self, modulus):
		with pytest.raises(TypeError):
			pow(self.value, 2, modulus)

	def test_pow_accepts_none_modulus(self):
		result = pow(self.value, -2, None)
		assert (result.numerator, result.denominator) == (9, 4)
