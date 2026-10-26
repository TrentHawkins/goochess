# Goochess

Chess project with reusable mathematics and board geometry, targeting Python 3.14 or newer.

## Development

From the repository root, create the virtual environment and install the package and development tools:

```sh
uv venv --python 3.14
uv pip install --editable . --group dev
```

The editable installation uses the files in `src/goochess` directly, so source edits do not require reinstalling.

Run checks with the virtual environment's tools:

```sh
.venv/bin/python -m pytest
.venv/bin/pyright
.venv/bin/pylint src/goochess tests
```

## Imports and layout

`goochess` is the importable package; `src` is its source directory. Use relative imports within the package, such as `from . import mathematics`. Tests and other callers use the package name:

```python
from goochess.geometry import Index
from goochess.mathematics import array

Index.A1 + array(1, -1)  # Index.B2
```

Board coordinates are `(file, row_from_top)`, starting at `(0, 0)` for `A8`, matching FEN placement order.

`goochess.structs` provides the reusable `pair` and `seq` tuple aliases, the two-value `switch`, and the subclass-preserving set `collection`. `goochess.mathematics` builds its mathematical types on these structures, including the `arrays` and `indices` collections.

`Board` handles placement and placement notation. `Position(Board)` adds white and black sides and supplies the context used by piece movement. Construct pieces with their color (`False` for white, `True` for black), then place them on a position:

```python
from goochess.engine import Position
from goochess.geometry import Index
from goochess.material import Pawn

position = Position("8/8/8/8/8/8/8/8")
pawn = Pawn(False)
position[Index.E2] = pawn
```

Position placement sets the piece's index and position context and maintains the matching side's active roster. `piece.side` derives from `piece.position.side[piece.color]`; `position.white` and `position.black` are aliases for those two sides. Side truth identifies black independently of roster size, and `side.other` returns its opponent. Square truth likewise identifies a black square.

`Board.__setitem__` performs placement inside its `binding` context; `Position` overrides that context to add roster and position bookkeeping while inheriting the setter.

Call `move.apply()` to execute a move, or use `with move.simulated:` to inspect its temporary placement and restore it afterward. Both mark the piece as moved; simulation restores its previous `moved` flag on exit. Move subclasses implement `apply` and `undo`; the base simulation context calls these hooks.

`Piece.fromnotation(symbol)` constructs an unplaced piece without position context. A plain `Board` can place and export pieces, but movement queries require placement on a `Position`. King-safety validation and the remaining position state (active color, castling rights, en passant availability, and counters) remain unfinished. A future `Game` runner will own a current position and coordinate progression and history; no `Game` class is implemented yet.

Tests live in `tests`, with one test file per source module. The `graphics` directory holds the project's artwork.
