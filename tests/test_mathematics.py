from __future__ import annotations


import copy
import math
import operator
import pickle

import pytest

from mathematics import average, geometric, harmonic, index, vector


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
		result = pickle.loads(pickle.dumps(self.derived, protocol=protocol))
		assert result == self.derived
		assert type(result) is self.Derived


class TestIndex:

	class Binary(index, base=2):
		pass

	class Square(index, base=8):
		pass

	class Decimal(index, base=10):
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


class TestAverage:

	mean_type = average
	left = average(4, 2)
	right = average(9)
	combined_value = 17 / 3
	zero_sample_value = 8 / 3
	empty_value = 0.0
	empty_inputs = (0.0, math.nan, math.inf)
	zero_seeds = (0, 0.0)
	edit_values = (2, 2.0)
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = (0, 2, pickle.HIGHEST_PROTOCOL)

	def test_construction_stores_public_value(self):
		result = self.mean_type(4)
		assert float(result) == 4
		assert result.count == 1

	def test_coercion_preserves_value_and_count(self):
		result = self.mean_type(self.left)
		assert result == self.left
		assert result.count == self.left.count
		assert type(result) is self.mean_type

	def test_explicit_count_overrides_copied_count(self):
		result = self.mean_type(self.left, 5)
		assert result == self.left
		assert result.count == 5
		assert self.left.count == 2

	def test_negative_count(self):
		with pytest.raises(ValueError):
			self.mean_type(4, -1)

	def test_weighted_addition(self):
		result = self.left + self.right
		assert float(result) == pytest.approx(self.combined_value)
		assert result.count == 3
		assert type(result) is self.mean_type

	def test_scalar_addition_counts_a_sample(self):
		result = self.left + float(self.right)
		assert float(result) == pytest.approx(self.combined_value)
		assert result.count == 3
		assert type(result) is self.mean_type

	def test_zero_on_the_right_counts_a_sample(self):
		result = self.left + 0
		assert float(result) == pytest.approx(self.zero_sample_value)
		assert result.count == 3

	def test_zero_average_on_the_left_counts_a_sample(self):
		result = self.mean_type(0) + self.left
		assert float(result) == pytest.approx(self.zero_sample_value)
		assert result.count == 3

	def test_subtraction_removes_weighted_samples(self):
		combined = self.left + self.right
		for removed in (self.right, float(self.right)):
			result = combined - removed
			assert float(result) == pytest.approx(float(self.left))
			assert result.count == self.left.count
			assert type(result) is self.mean_type

	def test_removing_too_many_samples(self):
		with pytest.raises(ValueError):
			operator.sub(self.right, self.left)

	def test_removing_all_samples_and_reusing_result(self):
		empty = self.left - self.left
		assert empty == self.empty_value
		assert empty.count == 0
		assert type(empty) is self.mean_type
		result = empty + self.left
		assert float(result) == pytest.approx(float(self.left))
		assert result.count == self.left.count

	@pytest.mark.parametrize("value", empty_inputs)
	def test_empty_operands_contribute_nothing(self, value):
		empty = self.mean_type(value, 0)
		for result in (empty + self.left, self.left + empty, self.left - empty):
			assert float(result) == pytest.approx(float(self.left))
			assert result.count == self.left.count
			assert type(result) is self.mean_type
		result = empty + empty
		assert result == self.empty_value
		assert result.count == 0

	def test_sum_preserves_weight(self):
		result = sum((self.left, self.right))
		assert float(result) == pytest.approx(self.combined_value)
		assert isinstance(result, self.mean_type)
		assert result.count == 3

	@pytest.mark.parametrize("seed", zero_seeds)
	def test_reflected_zero_is_an_identity(self, seed):
		assert seed + self.left is self.left

	@pytest.mark.parametrize("value", edit_values)
	def test_other_reflected_arithmetic_returns_float(self, value):
		added = value + self.left
		subtracted = value - self.left
		assert type(added) is type(subtracted) is float
		assert added == 6.0
		assert subtracted == -2.0

	def test_scaling_and_negation_return_float(self):
		for result in (self.left * 2, 2 * self.left):
			assert result == 8.0
			assert type(result) is float
		assert -self.left == -4.0
		assert type(-self.left) is float

	def test_augmented_assignment_preserves_original(self):
		result = self.left
		result += self.right
		assert float(result) == pytest.approx(self.combined_value)
		assert result.count == 3
		assert result is not self.left
		assert self.left == 4
		assert self.left.count == 2
		result -= self.right
		assert float(result) == pytest.approx(float(self.left))
		assert result.count == self.left.count

	@pytest.mark.parametrize("copier", copy_functions)
	def test_copy(self, copier):
		result = copier(self.left)
		assert result == self.left
		assert result.count == self.left.count
		assert type(result) is self.mean_type

	@pytest.mark.parametrize("protocol", pickle_protocols)
	def test_pickle(self, protocol):
		result = pickle.loads(pickle.dumps(self.left, protocol=protocol))
		assert result == self.left
		assert result.count == self.left.count
		assert type(result) is self.mean_type


class TestGeometric(TestAverage):

	mean_type = geometric
	left = geometric(4, 2)
	right = geometric(9)
	combined_value = 144 ** (1 / 3)
	zero_sample_value = 0.0
	empty_value = 1.0
	logarithms = ((1.0, 0.0), (math.e, 1.0), (0.0, -math.inf), (math.inf, math.inf))
	invalid_logarithms = (-1.0, -math.inf, math.nan)
	exponentials = ((0.0, 1.0), (1.0, math.e), (1000.0, math.inf), (math.inf, math.inf), (-math.inf, 0.0))

	@pytest.mark.parametrize("value, expected", logarithms)
	def test_encoding(self, value, expected):
		assert self.mean_type.encode(value) == pytest.approx(expected)

	@pytest.mark.parametrize("value", invalid_logarithms)
	def test_invalid_encoding_produces_nan(self, value):
		assert math.isnan(self.mean_type.encode(value))

	@pytest.mark.parametrize("value, expected", exponentials)
	def test_decoding(self, value, expected):
		assert self.mean_type.decode(value) == pytest.approx(expected)

	def test_nan_decoding(self):
		assert math.isnan(self.mean_type.decode(math.nan))


class TestHarmonic(TestAverage):

	mean_type = harmonic
	left = harmonic(4, 2)
	right = harmonic(9)
	combined_value = 54 / 11
	zero_sample_value = 0.0
	empty_value = math.inf
	reciprocals = ((2.0, 0.5), (-2.0, -0.5), (0.0, math.inf), (-0.0, -math.inf), (math.inf, 0.0), (-math.inf, -0.0))

	@pytest.mark.parametrize("value, expected", reciprocals)
	def test_encoding_and_decoding_preserve_sign(self, value, expected):
		for function in (self.mean_type.encode, self.mean_type.decode):
			result = function(value)
			assert result == pytest.approx(expected)
			assert math.copysign(1, result) == math.copysign(1, expected)

	def test_nan_encoding_and_decoding(self):
		assert math.isnan(self.mean_type.encode(math.nan))
		assert math.isnan(self.mean_type.decode(math.nan))
