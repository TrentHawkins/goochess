from __future__ import annotations


import copy
import operator
import pickle

import pytest

from goochess.structs import collection, switch


class TestSwitch:

	class Derived(switch[str]):
		...

	switch_types = (switch, Derived)
	items = ("false", "true")
	selections = ((False, "false"), (True, "true"), (-4, "false"), (-3, "true"), (-1, "true"),
		(0, "false"), (1, "true"), (2, "false"), (3, "true"), (100, "false"), (101, "true"))
	invalid_keys = (None, 1.5, "1", slice(None))
	mutations = ((operator.setitem, (0, "changed")), (operator.delitem, (0,)))
	copy_functions = (copy.copy, copy.deepcopy)
	pickle_protocols = tuple(range(pickle.HIGHEST_PROTOCOL + 1))

	@pytest.mark.parametrize("switch_type", switch_types)
	def test_construction(self, switch_type) -> None:
		value = switch_type(*self.items)
		false, true = value
		assert type(value) is switch_type
		assert len(value) == 2
		assert tuple(value) == self.items
		assert (false, true) == self.items
		assert value == self.items
		assert hash(value) == hash(self.items)

	@pytest.mark.parametrize("switch_type", switch_types)
	@pytest.mark.parametrize("key, expected", selections)
	def test_selection(self, switch_type, key, expected) -> None:
		assert switch_type(*self.items)[key] == expected

	@pytest.mark.parametrize("key", invalid_keys)
	def test_invalid_subscription(self, key) -> None:
		with pytest.raises(TypeError):
			_ = switch(*self.items)[key]

	@pytest.mark.parametrize("mutation, arguments", mutations)
	def test_immutability(self, mutation, arguments) -> None:
		value = switch(*self.items)

		with pytest.raises(TypeError):
			mutation(value, *arguments)

		assert tuple(value) == self.items

	@pytest.mark.parametrize("switch_type", switch_types)
	def test_serialization(self, switch_type) -> None:
		value = switch_type(*self.items)

		for copier in self.copy_functions:
			result = copier(value)
			assert result == value
			assert type(result) is switch_type

		for protocol in self.pickle_protocols:
			result = pickle.loads(pickle.dumps(value, protocol = protocol))
			assert result == value
			assert type(result) is switch_type


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
