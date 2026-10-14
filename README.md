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
from goochess.geometry import Square
from goochess.mathematics import vector

Square.A1 + vector((1, 1))  # Square.B2
```

Board coordinates are `(rank, file)`, starting at `(0, 0)` for `A1`.

Tests live in `tests/test_mathematics.py` and `tests/test_geometry.py`. The `graphics` directory holds the project's artwork.
