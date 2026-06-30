# Goochess Project Context

This is a durable architecture snapshot of `main` at `bf215e0` (2026-06-30). Recheck it when the implementation changes.

## Purpose and Status

Goochess is a local, two-player chess GUI whose design emphasizes semantic Python objects: squares, vectors, pieces, and moves carry behavior rather than being plain records. The standard 8×8 game is playable and implements legal-move highlighting, king-safety filtering, castling, en passant, and interactive promotion. It does not implement AI, networking, persistence, menus, clocks, or game-ending conditions.

`hex/` is an independent experiment in traceless/cube coordinates and regular-polygon geometry. It is not connected to the playable game. `src/sand.py` is scratch code and has no runtime imports.

## Environment and Entry Point

- Python: `>=3.14` (`.python-version` is `3.14`). The code uses PEP 695 generic/type-alias syntax.
- Runtime dependency: Pygame 2.6.1, locked by `uv.lock`.
- Development dependency group: Pylint, Pyright, and pytest.
- Setup: `uv sync`
- Launch from the repository root: `uv run python -m src.main`
- Syntax check: `uv run python -m compileall src hex`

Pylint is configured in `pyproject.toml` for tabs, 132-character lines, error/fatal diagnostics only, and ignoring Pygame's dynamically exported members; Pyright remains responsible for Pygame type checking. There is no build backend, console-script entry point, formatter, Pyright/pytest configuration, CI workflow, release tag, or license file. `requirements.txt` duplicates the runtime `pygame` dependency, while `pyproject.toml` and `uv.lock` are the primary environment description.

Always run from the repository root. Importing `src.algebra`, `src.engine`, or `src.material` reaches `src.theme`, which creates a 2160×1440 display and eagerly loads relative paths under `graphics/`. Headless checks require `SDL_VIDEODRIVER=dummy` and usually `SDL_AUDIODRIVER=dummy`.

## Repository Map

| Path | Role |
| --- | --- |
| `src/__init__.py` | Typed set-like `collection`, tuple-like `array`, and vector-set primitives. |
| `src/algebra.py` | Colors, board coordinates, vectors, square geometry, click detection, and square highlighting. |
| `src/engine.py` | `Board`, per-color `Side` indexes, `History`, FEN-like loading, game state, drawing, and click dispatch. |
| `src/material.py` | Piece hierarchy, movement generation, sprites, material values, and promotion choices. |
| `src/rules.py` | Executable move objects and specializations for capture, rush, en passant, promotion, and castling. |
| `src/theme.py` | Fixed layout/color constants, import-time display creation, asset cache, and drawable bases. |
| `src/main.py` | Uncapped Pygame event/render loop; F12 overwrites `game/screenshot.png`. |
| `graphics/` | Runtime piece/bevel images plus board sources (`.jpg`, `.png`, `.xcf`, `.drawio`, `.svg`). |
| `game/` | Checked-in reference screenshot. |
| `hex/` | Unwired hex-grid and polygon experiments. |

## Domain Model and Invariants

Squares use compact octal-style indexes: `A8 == 0o00`, `H8 == 0o07`, and `A1 == 0o70`. Rank occupies the high three bits and file the low three. `Square + Vector` validates board bounds through `File` and `Rank` enum construction, raising `ValueError` off-board.

`Color.BLACK` is `+1`/truthy and `Color.WHITE` is `-1`/falsey. Movement vectors and stock squares are declared from Black's perspective; multiplication by color leaves Black coordinates unchanged and vertically mirrors White coordinates. Preserve this convention when adding movement logic.

`Game` subclasses the 64-element `Board` list. Assigning a piece updates `piece.square`; `Game.__setitem__` and `__delitem__` also maintain `Side` indexes. Each `Side` groups pieces by concrete class and caches its king, corner rooks, and temporary en-passant `Ghost`. Avoid mutating the underlying list through methods that bypass these overrides.

Turn is derived solely from `len(game.history)`: even is White, odd is Black. `History` contains executed `Move` objects, with `None` placeholders when loading a later move number.

## Move and Input Flow

1. `Game.clicked()` maps a left-click to a `Square`.
2. Clicking a current-side piece stores it as `game.selected`.
3. `Piece.targets` creates pseudo-legal `Move`/`Capt` objects; `Piece.squares` temporarily executes each move as a context manager and removes moves that expose its king.
4. Clicking a highlighted target calls `game += rule`; this executes the rule, appends it to history, advances the turn, and expires the previous en-passant ghost.
5. Promotion is staged: choose a target, click the source repeatedly to cycle `Queen/Rook/Knight/Bishop`, then click the target to commit.

Move objects subclass square behavior, so a highlighted destination also carries execution and notation state. `rules.specialize()` dynamically composes modifiers onto an existing move. Castling moves the rook inside `King.__call__`; pawn rush creates a `Ghost`, and en passant removes the pawn behind that ghost.

The render order is board labels/squares/background, selected-square highlights, then pieces. `theme.Main` preloads and scales all active images. Piece sprite lookup is convention-based (`BPAWN`, `WQUEEN`, etc.); asymmetric bishops/knights select `*R` variants by color.

## Known Limitations and Risk Areas

- No committed test source or coverage policy exists. Add deterministic pytest tests under `tests/` before deep rule refactors.
- The FEN-like path is not a reliable round trip. `Board.forsyth_edwards` currently mishandles empty runs and leading separators, and `Game.forsyth_edwards` emits castling/en-passant fields in a different order from the parser.
- A piece's `_moved` flag is initialized but not set during moves. `moved` is inferred from whether the piece occupies a stock square, so returning a king, rook, or pawn to its origin can restore special-move eligibility.
- `Side.targets` unions occupancy-dependent pseudo-legal targets. Pawn forward moves can appear as attacks while empty diagonal attacks do not, making king-safety and castling changes especially sensitive.
- Checkmate, stalemate, resignation, draw rules, save/load UI, and animation remain TODOs in `README.md`.
- Rendering, rules, and state are tightly coupled through back-references and import-time Pygame setup. Refactors should preserve side-index synchronization and validate both move generation and drawing.

## Change Guidance

For rule changes, test ordinary movement plus capture, self-check rejection, castling through check, en passant expiry, and all promotion choices. For state changes, verify the board list, both `Side` indexes, cached king/rook/ghost references, history parity, and serialization together. For visual changes, retain source assets, update the runtime derivative intentionally, launch from the root, and include a screenshot in review.

Recent commit subjects are short and imperative (`Refine graphics`, `Remove some deprecations`). Keep commits focused and do not reformat unrelated code; established source uses tabs and deliberate alignment.
