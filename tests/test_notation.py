from __future__ import annotations


import copy
import pickle

import pytest

from goochess import notation


class NotationSetup:

	positions = (
		("8/8/8/8/8/8/8/8", ("--------",) * 8),
		(
			"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
			("rnbqkbnr", "pppppppp", "--------", "--------", "--------", "--------", "PPPPPPPP", "RNBQKBNR"),
		),
		(
			"r1b1k2q/1p4n1/8/6N1/2B5/7P/4KQ2/R7",
			("r-b-k--q", "-p----n-", "--------", "------N-", "--B-----", "-------P", "----KQ--", "R-------"),
		),
	)


class TestRank:

	cases = (
		("8", "--------", "8"),
		("RNBQKBNR", "RNBQKBNR", "RNBQKBNR"),
		("pppppppp", "pppppppp", "pppppppp"),
		("2PP4", "--PP----", "2PP4"),
		("3K4", "---K----", "3K4"),
		("1p1P1n1N", "-p-P-n-N", "1p1P1n1N"),
		("5p2", "-----p--", "5p2"),
		("6k1", "------k-", "6k1"),
		("K7", "K-------", "K7"),
		("r------R", "r------R", "r6R"),
		("----P---", "----P---", "4P3"),
		("--------", "--------", "8"),
	)
	invalid = ("", "7", "9", "88", "PPPPPPP", "PPPPPPPPP", "4P4", "3X4", "3.4", "00000000", "3 4")

	@pytest.mark.parametrize("source, expanded, compact", cases)
	def test_expansion_and_compaction(self, source, expanded, compact) -> None:
		value = notation.rank(source)
		assert type(value) is notation.rank
		assert len(value) == 8
		assert value[:] == expanded
		assert str(value) == compact
		assert notation.rank(str(value)) == value
		assert notation.rank(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_rank(self, source) -> None:
		with pytest.raises(ValueError):
			notation.rank(source)


class TestBoard(NotationSetup):

	iterables = (list, tuple, iter)
	invalid_counts = (0, 1, 7, 9)
	invalid_rows = ("7", "9", "3X4", "4P4", "0-------")

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_rank_structure(self, compact, expanded) -> None:
		value = notation.board(compact)
		assert type(value) is notation.board
		assert isinstance(value, tuple)
		assert len(value) == 8
		assert all(type(row) is notation.rank for row in value)
		assert tuple(row[:] for row in value) == expanded
		assert str(value) == compact

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	@pytest.mark.parametrize("iterable", iterables)
	@pytest.mark.parametrize("raw", (True, False))
	def test_iterable_ranks(self, compact, expanded, iterable, raw) -> None:
		expected = tuple(notation.rank(row) for row in expanded)
		rows = compact.split("/") if raw else expected
		value = notation.board(iterable(rows))
		assert tuple(value) == expected
		assert all(type(row) is notation.rank for row in value)
		assert str(value) == compact

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_serial_projection(self, compact, expanded) -> None:
		value = notation.board(compact)
		assert type(value.serial) is str
		assert len(value.serial) == 64
		assert value.serial == "".join(expanded)

	@pytest.mark.parametrize("count", invalid_counts)
	@pytest.mark.parametrize("as_text", (True, False))
	def test_invalid_rank_count(self, count, as_text) -> None:
		rows = ["8"] * count
		source = "/".join(rows) if as_text else iter(rows)

		with pytest.raises(ValueError):
			notation.board(source)

	@pytest.mark.parametrize("row", invalid_rows)
	def test_invalid_iterable_rank(self, row) -> None:
		rows = ["8"] * 8
		rows[3] = row

		with pytest.raises(ValueError):
			notation.board(rows)


class TestSerial(NotationSetup):

	invalid_lengths = (0, 1, 63, 65, 72)
	invalid_symbols = ("0", "8", "X", "_", " ")

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	@pytest.mark.parametrize("use_fen", (True, False))
	def test_fen_and_flat_construction(self, compact, expanded, use_fen) -> None:
		flat = "".join(expanded)
		value = notation.serial(compact if use_fen else flat)
		assert type(value) is notation.serial
		assert len(value) == 64
		assert value[:] == flat
		assert str(value) == compact

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_idempotent_construction(self, compact, expanded) -> None:
		value = notation.serial(compact)
		repeated = notation.serial(value)
		assert type(repeated) is notation.serial
		assert repeated == value
		assert repeated[:] == "".join(expanded)
		assert str(repeated) == compact

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_independent_rank_views(self, compact, expanded) -> None:
		value = notation.serial(compact)
		first = iter(value.ranks)
		second = iter(value.ranks)
		assert first is not second
		assert next(first) == expanded[0]
		rows = tuple(second)
		assert all(type(row) is notation.rank for row in rows)
		assert tuple(row[:] for row in rows) == expanded
		assert tuple(row[:] for row in first) == expanded[1:]
		assert tuple(value.ranks) == rows

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_round_trip(self, compact, expanded) -> None:
		value = notation.serial(compact)
		rows = notation.board(value.ranks)
		assert str(rows) == compact
		assert rows.serial == "".join(expanded)
		assert notation.serial(rows.serial) == value
		assert notation.board(str(value)).serial == value[:]

	@pytest.mark.parametrize("length", invalid_lengths)
	def test_invalid_flat_length(self, length) -> None:
		with pytest.raises(ValueError):
			notation.serial("-" * length)

	@pytest.mark.parametrize("symbol", invalid_symbols)
	def test_invalid_flat_symbol(self, symbol) -> None:
		with pytest.raises(ValueError):
			notation.serial("-" * 31 + symbol + "-" * 32)


class TestColor:

	cases = (("w", 0, "w"), ("b", 1, "b"), (0, 0, "w"), (1, 1, "b"), (False, 0, "w"), (True, 1, "b"))
	invalid = ("", "W", "B", "white", "black", "0", "1", "x", -1, 2, 8)

	@pytest.mark.parametrize("source, number, symbol", cases)
	def test_numeric_value_and_notation(self, source, number, symbol) -> None:
		value = notation.color(source)
		assert type(value) is notation.color
		assert isinstance(value, int)
		assert int(value) == number
		assert value == number
		assert bool(value) == bool(number)
		assert str(value) == symbol
		assert notation.color(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_color(self, source) -> None:
		with pytest.raises(ValueError):
			notation.color(source)

	@pytest.mark.parametrize("source, number, symbol", cases)
	def test_copy_and_pickle(self, source, number, symbol) -> None:
		value = notation.color(source)
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.color
			assert restored == number
			assert str(restored) == symbol


class TestCastling:

	cases = ("-", "K", "Q", "k", "q", "KQ", "Kk", "Kq", "Qk", "Qq", "kq", "KQk", "KQq", "Kkq", "Qkq", "KQkq")
	invalid = ("", "--", "K-", "-q", "KK", "qq", "qk", "QK", "kK", "Kqk", "KQK", "A", "w", " K", "K ")

	@pytest.mark.parametrize("source", cases)
	def test_notation(self, source) -> None:
		value = notation.castling(source)
		assert type(value) is notation.castling
		assert value == source
		assert str(value) == source
		assert notation.castling(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_castling(self, source) -> None:
		with pytest.raises(ValueError):
			notation.castling(source)

	@pytest.mark.parametrize("source", cases)
	def test_copy_and_pickle(self, source) -> None:
		value = notation.castling(source)
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.castling
			assert restored == value


class TestEnPassant:

	cases = ("-",) + tuple(file + rank for file in "abcdefgh" for rank in "36")
	invalid = ("", "--", "a", "3", "a1", "a2", "a4", "a5", "a7", "a8", "i3", "A3", "h9", "aa3", " a3", "a3 ")

	@pytest.mark.parametrize("source", cases)
	def test_notation(self, source) -> None:
		value = notation.en_passant(source)
		assert type(value) is notation.en_passant
		assert value == source
		assert str(value) == source
		assert notation.en_passant(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_en_passant(self, source) -> None:
		with pytest.raises(ValueError):
			notation.en_passant(source)

	@pytest.mark.parametrize("source", cases)
	def test_copy_and_pickle(self, source) -> None:
		value = notation.en_passant(source)
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.en_passant
			assert restored == value


class TestHalfmove:

	cases = ((0, 0), (1, 1), (125, 125), (False, 0), (True, 1), ("0", 0), ("125", 125), ("000", 0), ("00125", 125))
	invalid = (-1, "", "-1", "+1", " 1", "1 ", "1_0", "1.0", "1e2", "nan", "inf", "١", "１", "¹", 0.0, 1.5)

	@pytest.mark.parametrize("source, number", cases)
	def test_numeric_value_and_notation(self, source, number) -> None:
		value = notation.halfmove(source)
		assert type(value) is notation.halfmove
		assert isinstance(value, int)
		assert value == number
		assert str(value) == str(number)
		assert notation.halfmove(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_halfmove(self, source) -> None:
		with pytest.raises(ValueError):
			notation.halfmove(source)

	@pytest.mark.parametrize("source, number", cases)
	def test_copy_and_pickle(self, source, number) -> None:
		value = notation.halfmove(source)
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.halfmove
			assert restored == number


class TestFullmove:

	cases = ((1, 1), (125, 125), (True, 1), ("1", 1), ("125", 125), ("00125", 125))
	invalid = (0, -1, False, "0", "000", "", "-1", "+1", " 1", "1 ", "1_0", "1.0", "1e2", "nan", "inf", "١", "１", "¹", 1.0, 1.5)

	@pytest.mark.parametrize("source, number", cases)
	def test_numeric_value_and_notation(self, source, number) -> None:
		value = notation.fullmove(source)
		assert type(value) is notation.fullmove
		assert isinstance(value, int)
		assert value == number
		assert str(value) == str(number)
		assert notation.fullmove(value) == value

	@pytest.mark.parametrize("source", invalid)
	def test_invalid_fullmove(self, source) -> None:
		with pytest.raises(ValueError):
			notation.fullmove(source)

	@pytest.mark.parametrize("source, number", cases)
	def test_copy_and_pickle(self, source, number) -> None:
		value = notation.fullmove(source)
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.fullmove
			assert restored == number


class TestPosition:

	cases = (
		(
			"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
			"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", False, "KQkq", "-", 0, 1,
		),
		(
			"r3k2r/8/8/8/8/8/8/R3K2R b kq - 12 43",
			"r3k2r/8/8/8/8/8/8/R3K2R", True, "kq", "-", 12, 43,
		),
		(
			"8/8/8/3pP3/8/8/8/8 w - d6 17 128",
			"8/8/8/3pP3/8/8/8/8", False, "-", "d6", 17, 128,
		),
		(
			"r---k--r/--------/--------/--------/--------/--------/--------/R---K--R b Kq e3 105 1200",
			"r3k2r/8/8/8/8/8/8/R3K2R", True, "Kq", "e3", 105, 1200,
		),
	)
	field_types = (notation.board, notation.color, notation.castling, notation.en_passant, notation.halfmove, notation.fullmove)
	invalid_fields = ((0, "7/8/8/8/8/8/8/8"), (1, "W"), (2, "qK"), (3, "a4"), (4, "-1"), (4, "+1"), (5, "0"))
	invalid_arity = ("", "8/8/8/8/8/8/8/8", "8/8/8/8/8/8/8/8 w - - 0", "8/8/8/8/8/8/8/8 w - - 0 1 extra")

	@pytest.mark.parametrize("source, placement, color, castling, en_passant, halfmove, fullmove", cases)
	def test_decoded_fields(self, source, placement, color, castling, en_passant, halfmove, fullmove) -> None:
		value = notation.position(source)
		expected = (
			notation.board(placement), notation.color(color), notation.castling(castling), notation.en_passant(en_passant),
			notation.halfmove(halfmove), notation.fullmove(fullmove),
		)
		assert type(value) is notation.position
		assert isinstance(value, tuple)
		assert len(value) == 6
		assert tuple(type(item) for item in value) == self.field_types
		assert tuple(value) == expected
		assert (
			value.placement, value.color, value.castling, value.enpassant, value.halfmove, value.fullmove,
		) == expected
		assert all(type(row) is notation.rank for row in value.placement)

	@pytest.mark.parametrize("source, placement, color, castling, en_passant, halfmove, fullmove", cases)
	def test_round_trip(self, source, placement, color, castling, en_passant, halfmove, fullmove) -> None:
		value = notation.position(source)
		encoded = f"{placement} {'b' if color else 'w'} {castling} {en_passant} {halfmove} {fullmove}"
		assert str(value) == encoded
		assert notation.position(encoded) == value

	@pytest.mark.parametrize("source, placement, color, castling, en_passant, halfmove, fullmove", cases)
	def test_copy_and_pickle(self, source, placement, color, castling, en_passant, halfmove, fullmove) -> None:
		value = notation.position(source)
		encoded = f"{placement} {'b' if color else 'w'} {castling} {en_passant} {halfmove} {fullmove}"
		restored_values = (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value)))

		for restored in restored_values:
			assert type(restored) is notation.position
			assert restored == value
			assert tuple(type(item) for item in restored) == self.field_types
			assert all(type(row) is notation.rank for row in restored.placement)
			assert str(restored) == encoded

	@pytest.mark.parametrize("field, invalid", invalid_fields)
	def test_invalid_field(self, field, invalid) -> None:
		parts = self.cases[0][0].split()
		parts[field] = invalid

		with pytest.raises(ValueError):
			notation.position(" ".join(parts))

	@pytest.mark.parametrize("source", invalid_arity)
	def test_invalid_field_count(self, source) -> None:
		with pytest.raises(ValueError):
			notation.position(source)

	def test_counter_normalization(self) -> None:
		value = notation.position("8/8/8/8/8/8/8/8 w - h3 000 001")
		assert value.halfmove == 0
		assert value.fullmove == 1
		assert str(value) == "8/8/8/8/8/8/8/8 w - h3 0 1"

	def test_replacement_preserves_codec(self) -> None:
		source = self.cases[2][0]
		value = notation.position(source)
		replacement = value._replace(color = notation.color("b"), halfmove = notation.halfmove(25))
		assert type(replacement) is notation.position
		assert str(replacement) == "8/8/8/3pP3/8/8/8/8 b - d6 25 128"
		assert notation.position(str(replacement)) == replacement
		assert str(value) == source
