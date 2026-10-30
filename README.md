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

`Board` accepts only FEN placement rows and handles placement notation. `Position(Board)` accepts a full six-field FEN, adds white and black sides, and supplies the context used by piece movement. The `forsyth_edwards` constructor argument intentionally has these different meanings at the two boundaries. Construct pieces with their color (`False` for white, `True` for black), then place them on a position:

```python
from goochess.engine import Position
from goochess.geometry import Index
from goochess.material import Pawn

position = Position("8/8/8/8/8/8/8/8 w - - 0 1")
pawn = Pawn(False)
position[Index.E2] = pawn
```

Position placement sets the piece's index and position context and maintains the matching side's active roster. `piece.side` derives from `piece.position.side[piece.color]`; `position.white` and `position.black` are aliases for those two sides. Side truth identifies black independently of roster size, and `side.other` returns its opponent. Square truth likewise identifies a black square.

`Board.__setitem__` performs placement inside its `binding` context; `Position` overrides that context to add roster and position bookkeeping while inheriting the setter.

Call `move.apply()` to execute a move, or use `with move.simulated:` to inspect its temporary placement and restore it afterward. Both mark the piece as moved; simulation restores its previous `moved` flag on exit. Move subclasses implement `apply` and `undo`; the base simulation context calls these hooks, passing the saved `moved` value to `undo`.

Standard castling is available through `Castle(target, king)` and `King.squares`. For example, `Position("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")` reads castling declarations from the third FEN field after creating the pieces and registering their kings; `"-"` grants no partnerships. Each king's instance dictionary, `rooks`, maps the relative starting offsets `King.ᐊ = (-4, 0)` and `King.ᐅ = (3, 0)` to the corresponding rook objects. Membership records imported permission, so no separate side flags are needed. Declared partners must be kings and same-color rooks in the standard starting squares. Entries remain unchanged after movement or capture, and a replacement rook does not become a partner automatically.

`Castle.long` derives the wing from its target, and construction retrieves the recorded partner rather than discovering the current corner occupant. Remaining eligibility checks that the king and that rook are unmoved and the rook still occupies its expected square. `King.squares` generates two-square horizontal targets, assuming the standard position and consistent movement flags rather than enforcing the king's home square separately. `Jump` shares the midpoint, clearance, and unmoved-piece checks between `Rush` and `Castle`; castling adds rook validation, queenside B-file clearance, and king safety at the source, crossing, and destination squares. Application assumes the candidate has been validated in the current position. A failed validation never removes a partnership: blocking pieces and attacks can prevent castling temporarily. Simulation restores placement and movement flags without changing the partner dictionary. Raw `King.targets` excludes castling to keep attack queries independent of castling validation.

`Piece.fromnotation(symbol)` constructs an unplaced piece without position context. A plain `Board` can place and export pieces, but movement queries require placement on a `Position`. `Position` currently processes the placement and castling fields of its full-FEN input; active color, en passant availability, and counters are accepted but not yet applied. Full legality and full-FEN export remain unfinished; representation still emits placement only. Future export must derive remaining rights from partners and movement flags, independently of temporary clearance or attacks. A future `Game` runner will own a current position and coordinate progression and history; no `Game` class is implemented yet.

`notation.position` decodes all six FEN fields into a `namedtuple` and formats them back through `str`. It uses black-as-true color, notation strings for castling and en passant, and integer counters. The engine still splits its input directly; wiring in this codec and exporting full FEN from engine state remain separate next steps.

Tests live in `tests`, with one test file per source module. The `graphics` directory holds the project's artwork.
