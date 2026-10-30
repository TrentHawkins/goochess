from __future__ import annotations


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

	@pytest.mark.parametrize("source, expanded, compact", cases)
	def test_expansion_and_compaction(self, source, expanded, compact) -> None:
		value = notation.rank(source)
		assert type(value) is notation.rank
		assert len(value) == 8
		assert value[:] == expanded
		assert str(value) == compact
		assert notation.rank(str(value)) == value
		assert notation.rank(value) == value


class TestBoard(NotationSetup):

	iterables = (list, tuple, iter)

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
	def test_iterable_ranks(self, compact, expanded, iterable) -> None:
		rows = tuple(notation.rank(row) for row in expanded)
		value = notation.board(iterable(rows))
		assert tuple(value) == rows
		assert all(type(row) is notation.rank for row in value)
		assert str(value) == compact

	@pytest.mark.parametrize("compact, expanded", NotationSetup.positions)
	def test_serial_projection(self, compact, expanded) -> None:
		value = notation.board(compact)
		assert type(value.serial) is str
		assert len(value.serial) == 64
		assert value.serial == "".join(expanded)


class TestSerial(NotationSetup):

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
