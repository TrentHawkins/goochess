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

`Board` owns the white and black sides. Construct pieces with their actual side, then place them on the board:

```python
from goochess.engine import Board
from goochess.geometry import Index
from goochess.material import Pawn

board = Board("8/8/8/8/8/8/8/8")
pawn = Pawn(board.white)
board[Index.E2] = pawn
```

Placement maintains the side's active roster and the piece's index. A piece derives its board from its side. `Game` currently inherits board behavior as an extension point for later game rules.

Tests live in `tests`, with one test file per source module. The `graphics` directory holds the project's artwork.
