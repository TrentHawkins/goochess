# Repository Guidelines

## Project Structure & Module Organization

The Pygame-free chess core lives in `src/`: `engine.py` owns game state, `rules.py` executable moves, `material.py` pieces, and `algebra.py` coordinates. The optional frontend lives in `app/`; its controller translates input, animation stages deferred moves, views render state, layout maps squares to pixels, and independent board/piece theme specifications load assets. The dependency direction is strictly `app → src`; never import `app` or Pygame from `src`. Experimental hex logic is isolated in `hex/`. Runtime artwork belongs in `graphics/`.

Read [`.agents/PROJECT_CONTEXT.md`](.agents/PROJECT_CONTEXT.md) before structural work; it records the runtime flow, invariants, and current limitations.

## Build, Test, and Development Commands

- `uv sync` installs the core and development tools.
- `uv sync --extra app` also installs the optional Pygame frontend.
- `uv run --extra app python -m app.main` launches the game from the repository root.
- `uv run python -m compileall src app hex` performs a syntax check.
- `uv run pytest` runs core tests; `uv run --extra app pytest` includes frontend tests.
- `uv run --extra app pylint src app hex tests` and `uv run --extra app pyright src app hex` run static checks.

Pygame loads assets through repository-relative paths, so run development commands from the project root.

## Coding Style & Naming Conventions

Use tabs, type annotations on public interfaces, and `from __future__ import annotations` in typed modules. Use `snake_case` for functions and variables, `UPPER_CASE` for constants and enum members, and `PascalCase` for normal classes. Lowercase algebra types (`file`, `rank`, `array`) are intentional. Keep domain interactions chess-readable and graphical wrappers thin. Pylint policy is in `pyproject.toml`; avoid unrelated reformatting.

## Testing Guidelines

Add pytest tests under `tests/` as `test_<module>.py` with `test_<behavior>()` functions. Core tests must run without Pygame. Keep rendering and controller tests separate; use dummy SDL drivers for display initialization. Preserve the architecture test that rejects `pygame` and `app` imports from `src/`.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Refine graphics` and `Remove some deprecations`. Keep each commit scoped to one coherent change and explain non-obvious design decisions in the body. Pull requests should summarize behavior changes, list verification commands, and link relevant issues. Include before/after screenshots for board, piece, or layout changes, and call out any new or replaced files under `graphics/`.
