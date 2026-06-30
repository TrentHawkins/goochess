# Goochess Project Context

This durable architecture snapshot reflects the Pygame application extraction completed on 2026-06-30. Recheck it when the implementation changes.

## Purpose and Status

Goochess is a behavior-rich chess core with an optional local, two-player Pygame frontend. Squares, vectors, pieces, and moves carry behavior rather than being plain records. The standard 8×8 game implements king-safety filtering, castling, en passant, and promotion; the frontend supplies input, highlighting, and rendering. It does not implement AI, networking, persistence, menus, clocks, or game-ending conditions.

`hex/` is an independent experiment in traceless/cube coordinates and regular-polygon geometry. It is not connected to the playable game. `src/sand.py` is scratch code and has no runtime imports.

## Design Philosophy

These principles are architectural constraints, not incidental traits to remove during cleanup:

1. **Model the chess ontology first.** Start from concepts that exist in chess—square, vector, piece, side, move, capture, promotion, history—and make them the primary units of the program. A helper abstraction must justify itself by clarifying that model; implementation convenience alone is not enough.
2. **Prefer behavior-rich domain entities.** Put an operation on the entity that knows and owns it. Pieces generate their moves, moves validate and execute themselves, sides know their material and opposition, and squares own coordinate behavior. Prefer asking an object to perform a chess operation over extracting its data into a procedural engine.
3. **Make interactions read as chess.** The public vocabulary and object relationships should form an executable chess language. Expressions such as `piece.targets`, `king.safe`, `side.other`, `game += move`, and `with move` should communicate domain meaning before implementation mechanics. Minimize algorithmic and infrastructural noise in rule code.
4. **Choose supertypes semantically.** Inheritance is part of the model, not merely a reuse mechanism. An entity should inherit from the most faithful behavioral or mathematical category available: boards are indexed collections, histories are sequences, squares are coordinates, ranged pieces extend shared ranged movement, and captures are specialized moves. Preserve this intent when static tooling or convenience pressures suggest flattening the hierarchy.
5. **Keep responsibilities at their narrowest natural boundary.** Place each rule with the entity that has the required knowledge, then compose those local responsibilities. `Game` coordinates; it should not absorb piece geometry, move semantics, notation, and rendering policy into a central god object.
6. **Optimize semantic clarity before runtime speed.** Direct traversal, temporary move execution, and object composition are acceptable when they make the chess rule evident. Optimize only after correctness and profiling establish a real constraint, and retain the semantic interface when changing an implementation.
7. **Remain Python-native and dependency-light.** Prefer Python's data model, standard library, inheritance, enums, context managers, properties, and operators over frameworks or foreign abstractions. Pygame exists to provide an immediate graphical smoke tester and playable shell; it should support rather than redefine the chess model.
8. **Treat correctness as compositional.** Local entities should maintain their own invariants so legal game behavior emerges from their interaction. Avoid distant corrective logic that compensates for an entity with an unclear contract.

## Recurring Architectural Patterns

- **Semantic specialization of native types.** `Square`/`Color` specialize integers and enums; vectors specialize tuples; `Squares`/`Vectors` specialize sets; `Board` and `History` specialize lists; `Side` specializes a mapping. Native operations remain available while gaining chess meaning.
- **An internal domain-specific language.** Operator overloads encode natural relations: vectors add, square differences produce vectors, color multiplication mirrors a position, set operations compose movement spaces, truth tests validate rules, calls execute entities, and representation methods emit notation.
- **Polymorphic movement taxonomy.** `Melee`, `Ranged`, and `Star` capture orthogonal movement traits. Concrete pieces obtain behavior through a hierarchy and deliberate multiple inheritance instead of switch statements in the engine.
- **Executable rule/command objects.** A `Move` is simultaneously a destination, a validity predicate, notation, an executable command, and a reversible context. `Capt`, `Rush`, `Promotion`, `EnPassant`, and castling refine that concept rather than returning detached flags.
- **Transactional rule probing.** `Piece.squares` enters a candidate move, asks whether the king remains safe, and restores state on exit. The same semantic operation supports both real execution and speculative legality checks.
- **Composable rule specialization.** `rules.specialize()` and `Mod` layer promotion or en-passant semantics onto an existing move. Cross-cutting chess conditions become combinations of rule types rather than branches inside every piece.
- **Perspective normalization.** Movement and stock positions are declared once from Black's orientation and transformed by `Color` for White. Symmetry is represented algebraically instead of duplicated across sides.
- **Derived state where practical.** Turn follows history parity; legality is derived from current targets and king safety; material and notation are computed views. `Side` indexes and king/rook/ghost references are deliberate caches that must remain synchronized with the board.
- **Thin orchestration.** The app controller translates physical input into domain moves, while `Game` delegates movement to rules and pieces. Coordinators sequence domain behavior but do not reimplement it.
- **Self-description at boundaries.** Domain entities provide chess symbols, algebraic-looking representations, and FEN-like state. The optional app maps those semantic identities to graphical styles without reverse dependencies.
- **Finite spaces made explicit.** Enums define the closed sets of colors, files, ranks, squares, directions, and promotion officers. Invalid coordinates fail through enum construction instead of requiring repeated range checks.
- **Explicit presentation mapping.** Typed app-side mappings associate piece type and color with graphical assets. The core retains relationships such as `side` and `other` without knowing asset names or display conventions.

## Design Decision Order

When extending the engine:

1. Name the chess concept and its invariant.
2. Identify the entity that naturally owns the required knowledge.
3. Choose the most semantically accurate existing or native supertype.
4. Design the interaction so a reader sees the chess rule in the call site.
5. Keep coordination, representation, and graphical concerns at explicit boundaries.
6. Add generic machinery or optimize only when the semantic model cannot express the requirement cleanly.

## Environment and Entry Point

- Python: `>=3.14` (`.python-version` is `3.14`). The code uses PEP 695 generic/type-alias syntax.
- Optional `app` dependency: Pygame 2.6.1, locked by `uv.lock`.
- Development dependency group: Pylint, Pyright, and pytest.
- Core setup: `uv sync`
- Frontend setup: `uv sync --extra app`
- Launch from the repository root: `uv run --extra app python -m app.main`
- Syntax check: `uv run python -m compileall src app hex`

Pylint and pytest are configured in `pyproject.toml`; Pyright remains responsible for Pygame type checking. There is no build backend, console-script entry point, formatter, CI workflow, release tag, or license file. `pyproject.toml` and `uv.lock` are the authoritative environment description.

Always run the frontend from the repository root because theme specifications use repository-relative asset paths. Importing `src` never initializes Pygame or reads assets. App display tests use `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`.

## Repository Map

| Path | Role |
| --- | --- |
| `src/__init__.py` | Typed set-like `collection`, tuple-like `array`, and vector-set primitives. |
| `src/algebra.py` | Colors, board coordinates, vectors, and square geometry. |
| `src/engine.py` | `Board`, per-color `Side` indexes, `History`, FEN-like loading, and game state. |
| `src/material.py` | Piece hierarchy, movement generation, material values, and promotion choices. |
| `src/rules.py` | Executable move objects and specializations for capture, rush, en passant, promotion, and castling. |
| `app/controller.py` | Pygame event translation plus selection and pending-promotion state. |
| `app/views.py` | Composed board, square, move, and piece views; rendering is read-only over core state. |
| `app/layout.py` | Display geometry, square rectangles, and hit-testing. |
| `app/theme.py` | Independent board/piece theme specifications and registries, validated loaders, and composed appearance. |
| `app/main.py` | Composition root and event/render loop; F12 overwrites `game/screenshot.png`. |
| `graphics/` | Runtime piece/bevel images plus board sources (`.jpg`, `.png`, `.xcf`, `.drawio`, `.svg`). |
| `game/` | Checked-in reference screenshot. |
| `hex/` | Unwired hex-grid and polygon experiments. |
| `tests/` | Core characterization, dependency-boundary, controller, layout, theme, and headless view tests. |

## Domain Model and Invariants

Squares use compact octal-style indexes: `A8 == 0o00`, `H8 == 0o07`, and `A1 == 0o70`. Rank occupies the high three bits and file the low three. `Square + Vector` validates board bounds through `File` and `Rank` enum construction, raising `ValueError` off-board.

`Color.BLACK` is `+1`/truthy and `Color.WHITE` is `-1`/falsey. Movement vectors and stock squares are declared from Black's perspective; multiplication by color leaves Black coordinates unchanged and vertically mirrors White coordinates. Preserve this convention when adding movement logic.

`Game` subclasses the 64-element `Board` list. Assigning a piece updates `piece.square`; `Game.__setitem__` and `__delitem__` also maintain `Side` indexes. Each `Side` groups pieces by concrete class and caches its king, corner rooks, and temporary en-passant `Ghost`. Avoid mutating the underlying list through methods that bypass these overrides.

Turn is derived solely from `len(game.history)`: even is White, odd is Black. `History` contains executed `Move` objects, with `None` placeholders when loading a later move number.

## Domain and Application Flow

1. `GameController` maps a Pygame click through `BoardLayout.square_at()`.
2. `InteractionState` owns the selected piece and any pending promotion; `Game` contains chess state only.
3. `Piece.targets` creates pseudo-legal `Move`/`Capt` objects; `Piece.squares` temporarily executes each move as a context manager and removes moves that expose its king.
4. The controller calls `game += rule`; this executes the rule, appends it to history, advances the turn, and expires the previous en-passant ghost.
5. The controller stages promotion, cycles `Officer`, and commits the explicitly configured core `Promotion`.

Move objects subclass square behavior, so a highlighted destination also carries execution and notation state. `rules.specialize()` dynamically composes modifiers onto an existing move. Castling moves the rook inside `King.__call__`; pawn rush creates a `Ghost`, and en passant removes the pawn behind that ghost.

`GameView` reads `Game` and `InteractionState`, then composes `BoardView`, `MoveView`, and `PieceView`. Rendering never mutates core objects. Layout is independent from appearance. `BoardThemeSpec` defines board assets and board/highlight colors; `PieceThemeSpec` defines explicit type/color styles and piece effects. Their separate registries currently provide the `wood` board and `default` pieces, which `Appearance` composes after Pygame initialization.

## Known Limitations and Risk Areas

- The test suite covers representative rules and the core/app boundary but has no coverage threshold.
- The FEN-like path is not a reliable round trip. `Board.forsyth_edwards` currently mishandles empty runs and leading separators, and `Game.forsyth_edwards` emits castling/en-passant fields in a different order from the parser.
- A piece's `_moved` flag is initialized but not set during moves. `moved` is inferred from whether the piece occupies a stock square, so returning a king, rook, or pawn to its origin can restore special-move eligibility.
- `Side.targets` unions occupancy-dependent pseudo-legal targets. Pawn forward moves can appear as attacks while empty diagonal attacks do not, making king-safety and castling changes especially sensitive.
- Checkmate, stalemate, resignation, draw rules, save/load UI, and animation remain TODOs in `README.md`.
- The frontend uses fixed 2160×1440 geometry and repository-relative asset paths; alternate resolutions and runtime theme selection are not implemented.

## Change Guidance

For rule changes, test ordinary movement plus capture, self-check rejection, castling through check, en passant expiry, and all promotion choices. For state changes, verify the board list, both `Side` indexes, cached king/rook/ghost references, history parity, and serialization together. For visual changes, retain source assets, update the runtime derivative intentionally, launch from the root, and include a screenshot in review.

Recent commit subjects are short and imperative (`Refine graphics`, `Remove some deprecations`). Keep commits focused and do not reformat unrelated code; established source uses tabs and deliberate alignment.
