# Repository Guidelines

## Project Structure & Module Organization

The playable chess application lives in `src/`. `main.py` owns the Pygame event loop, `engine.py` manages game and board state, `rules.py` implements move rules, `algebra.py` defines coordinates and vectors, and `theme.py` handles rendering resources. Experimental hex-board logic is isolated in `hex/`. Image sources and runtime artwork belong in `graphics/`; `game/` contains captured game output. Keep new modules focused and place standard-game code under `src/`.

Read [`.agents/PROJECT_CONTEXT.md`](.agents/PROJECT_CONTEXT.md) before structural work; it records the runtime flow, invariants, and current limitations.

## Build, Test, and Development Commands

- `uv sync` creates or updates the Python 3.14 environment from `pyproject.toml` and `uv.lock`.
- `uv run python -m src.main` launches the game from the repository root.
- `uv run python -m compileall src hex` performs a quick syntax/import-independent check.
- `uv run pytest` runs the test suite.
- `uv run pylint src hex` and `uv run pyright src hex` run static checks.

Pygame loads assets through repository-relative paths, so run development commands from the project root.

## Coding Style & Naming Conventions

Follow the existing Python style: tabs for indentation, type annotations on public interfaces, and `from __future__ import annotations` in typed modules. Use `snake_case` for functions and variables, `UPPER_CASE` for constants and enum members, and `PascalCase` for normal classes. Some algebra helper types intentionally use lowercase names (`file`, `rank`, `array`); preserve those established APIs, but use conventional class naming for new abstractions. Group standard-library imports before third-party and local imports. Pylint policy is configured in `pyproject.toml`; avoid unrelated reformatting.

## Testing Guidelines

No test source or coverage threshold is currently committed. Add tests under `tests/` using pytest-style files named `test_<module>.py` and functions named `test_<behavior>()`. Prioritize deterministic unit tests for algebra, board serialization, legal moves, castling, en passant, and promotion. Keep rendering tests separate from rule tests; use Pygame's dummy video driver when tests require display initialization.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Refine graphics` and `Remove some deprecations`. Keep each commit scoped to one coherent change and explain non-obvious design decisions in the body. Pull requests should summarize behavior changes, list verification commands, and link relevant issues. Include before/after screenshots for board, piece, or layout changes, and call out any new or replaced files under `graphics/`.
