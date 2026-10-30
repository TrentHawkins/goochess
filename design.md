# Design record

This is the working reference for Goochess design discussions: what we have chosen, why we chose it, what the code currently implements, and what still needs a decision. It records the model we are building together rather than prescribing the rest of the implementation.

Jump to [decisions](#decisions-and-retained-baseline), [open questions](#open-decisions), [future directions](#future-directions), or [implementation gaps](#current-implementation-gaps).

## Reading and maintaining this record

- **Agreed** means an explicit design choice. It can still be awaiting implementation.
- **Baseline** describes a retained contract in the current framework, without declaring every implementation detail permanent.
- **Open** means no alternative has been selected. Recommendations are labelled as recommendations.
- **Deferred** means the subject has deliberately been left for later.
- A checked alternative means **selected**, not necessarily implemented. An unchecked alternative in a closed decision is historical; in an open decision it remains under consideration.
- When we change a decision, update its existing entry and retain a short explanation of the superseded choice. Keep the identifiers stable so later discussions can refer to them.
- An experimental edit, a passing test, or an assistant recommendation does not by itself settle a design question. Record disagreements between the intended model and the implementation explicitly.

The historical starting point is `develop` at `7fb69e20e4a0df819a4adc37039c785483d37a03`. Earlier code is a source of inspiration, not the specification for this framework. The initial record was reviewed on 2026-10-21 against `50f5c06` and the working changes to `Side` on the `side` branch. The color/context revision on 2026-10-23 supersedes D18's board-owned participant fusion. The state/progression revision on 2026-10-24 renames that rule context to `Position` and reserves `Game` for a future runner, while retaining intrinsic boolean color. The mathematical framework already present at `develop` is retained as baseline context; this record does not reconstruct its earlier development.

## Responsibility map

| Component | Responsibility | References |
| --- | --- | --- |
| `pair`, `seq`, `switch`, `collection` | Reusable tuple aliases, parity-based pair selection, and set operations preserving the concrete collection type | [structs.py](src/goochess/structs.py), [structure tests](tests/test_structs.py) |
| `array`, `index`, mathematical collections, `fraction` | Reusable mathematics without chess knowledge | [mathematics.py](src/goochess/mathematics.py), [mathematics tests](tests/test_mathematics.py) |
| `Index`, `Compass` | Standard chess board geometry and directions | [geometry.py](src/goochess/geometry.py), [geometry tests](tests/test_geometry.py) |
| `rank`, `board`, `serial` | Placement notation and its decoded representations | [notation.py](src/goochess/notation.py), [notation tests](tests/test_notation.py) |
| `Piece` and its subclasses | Piece identity, location/context references, and movement patterns | [material.py](src/goochess/material.py), [material tests](tests/test_material.py) |
| `Move`, `Capt`, and related classes | Move targets, records, predicates, notation, ordinary execution, and temporary placement contexts | [algebra.py](src/goochess/algebra.py), [algebra tests](tests/test_algebra.py) |
| `Board` | Square occupancy, piece locations, and placement notation without participant ownership | [engine.py](src/goochess/engine.py), [engine tests](tests/test_engine.py) |
| `Position(Board)` and `Side` | Current-position context, color-selected participants, active rosters, and initial king references; remaining rule-state fields are planned | [engine.py](src/goochess/engine.py), [engine tests](tests/test_engine.py) |
| Future `Game` | Own a current position and coordinate progression, history, and reversal; no runner class is implemented | D01, O08 |

## Decisions and retained baseline

### D01. Standard chess, mutable positions, and explicit move records

**Status: Agreed direction; ordinary execution and temporary placement implemented, complete transitions and game-tree search pending.**

The current scope is standard chess. `Board` handles mutable square occupancy and placement notation. `Position(Board)` extends it with participating sides and the context needed by piece and move queries. A piece stores its intrinsic boolean color and receives a `position` reference when placed on a position; its `side` is derived from that position's color-selected pair. A plain board remains usable for placement and export, but it does not supply full movement context.

The 2026-10-24 revision renames the former `Game` state class to `Position`. The intended complete current state belongs to `Position`, including the active color, castling rights, en passant availability, and relevant counters. Imported castling permission now lives in each king's `rooks` dictionary, whose stable partner references also identify the declared participants; remaining eligibility depends on their presence and movement flags. `Position` accepts a full six-field FEN during construction and currently processes its placement and castling fields. Applying the other fields and full-FEN export remain pending. A future `Game` runner will own a current position through composition and coordinate progression and history; no runner class exists yet. This restores the distinction between state and progression while retaining `Board` as the occupancy foundation and the boolean color model from 2026-10-23. Remaining FEN fields, complete legality, and complete transition effects remain open in O05/O07–O09; O08 records the initial execution and temporary-placement API. Context access does not require implementing every shared rule inside a piece.

A move describes a transition around one moving piece and its destination, rather than requiring a newly constructed board for every candidate.

That compact move model must still accommodate effects involving other pieces: captures, the rook in castling, promotion, and en passant. It does not imply that every transition changes only two board slots. O08 establishes ordinary, en passant, and castling execution and temporary placement for a one-move king-safety check; remaining special effects, history undo, and complete-state game-tree traversal remain pending.

Prefer small, meaningful responsibility boundaries and direct code. Do not add registries, generalized frameworks, or new abstractions merely to anticipate future features. This is also an exercise: implementation proceeds in understandable steps, with review between them.

### D02. Points and displacements have distinct arithmetic

**Status: Baseline, with agreed refinements.**

`array` is an immutable tuple of integer displacement components. Its dimension is dynamic. Component-wise operations between nonempty arrays use strict `zip`, so mismatched dimensions fail instead of silently trimming. Scalar operations infer their arity from the array; the empty array participates in the existing zero/identity conventions.

`index` is an immutable bounded integer encoding a point. Its concrete class supplies both `dimension` and `base`; coordinates are base digits, with the first component least significant. Specialization through `index[dimension, base]` creates and reuses runtime classes. The current registry and restoration machinery let instance copy/pickle restore the same specialized runtime type; generated classes themselves are not necessarily picklable. Changing that machinery is not a pending requirement.

Point plus displacement returns a point of the concrete point type. Point minus point returns an `array`. Point minus displacement returns a point. `array` arithmetic must leave point operands to point dispatch instead of treating an `index` as an ordinary flat integer vector.

Individual point construction and translation validate dimensions and bounds with `ValueError`. `index.middle` requires an exact integral midpoint; it does not round. Slicing an `index` projects its coordinates into an index with the resulting dimension and the same base. Array slicing uses ordinary tuple behavior.

Historical alternatives retained only as context:

- [x] Dynamic array dimensions with runtime consistency.
- [ ] Fixed or optionally fixed vector subclasses carrying a class dimension.
- [x] Bounded point arithmetic raises on an invalid result.
- [ ] Have collections silently discard failed point translations.

The current `indices.__mul__` is also strict: an invalid pair aborts the product. Piece search handles board boundaries separately in D10. `index.range` exists, but using it for piece search was deliberately set aside. The earlier `index.flip` experiment was removed; it is not a required feature.

### D03. Mathematical collections preserve mathematical collection types

**Status: Baseline, with agreed refinements.**

`structs.collection` provides set operations that preserve its concrete collection class. Its construction and reconstruction convention is variadic items. `mathematics.arrays` and `mathematics.indices` build on that reusable container contract.

The `structs` module also owns the `pair[T]` and `seq[T]` tuple aliases, formerly `mathematics.pair` and `mathematics.sequence`. Its `switch(false, true)` stores two values in that order: integer lookup selects the first value for even indices and the second for odd indices, so boolean lookup selects the corresponding named constructor argument. Iteration retains the underlying pair order.

The former `mathematics.collection`, `mathematics.pair`, and `mathematics.sequence` import paths are no longer provided. Existing pickles of plain `mathematics.collection` instances require a compatibility alias at the old module path before loading; the `arrays` and `indices` class paths remain unchanged.

`arrays` multiplication forms pairwise displacement sums for iterable operands and scales for integer operands, including negative integers. Positive powers form sums of repeated choices. Results are sets of resulting displacements, so they do not preserve path multiplicity or ordering. Nonpositive powers are currently unsupported.

Do not filter zero or falsey members during collection construction or ordinary set operations. Remove an unwanted stationary displacement explicitly where a movement rule requires it. Generic falsey filtering is unsuitable: an `Index` is falsey because of square color, not because it is absent. This does not change the distinct scalar-operation convention: multiplying an `arrays` collection by zero currently returns an empty collection.

Preserving mathematical collection types does not require game participants to use the same base class; see D08.

### D04. The custom fraction remains a separate mathematical utility

**Status: Baseline; extensions deferred.**

`fraction` retains integer numerator/denominator fields in reduced form, with denominator sign normalized. Zero denominators deliberately represent infinities and NaN. Arithmetic and comparisons follow that extended domain, including the exceptional comparison behavior of NaN.

The fraction fields are protected from ordinary reassignment and deletion after initialization. Supported operations preserve the concrete fraction subclass. Hashing and serialization have dedicated mathematical tests; this is not a claim of interoperability with every Python numeric type.

### D05. Geometry follows placement order directly

**Status: Agreed and implemented.**

`Index` enumerates all 64 standard board squares in FEN reading order: `A8 = 0` through `H1 = 63`. Iteration uses that same order. Decoded coordinates are `(file, row_from_top)`, so north is `(0, -1)` and south is `(0, 1)`. Human-readable ranks remain `1..8`; they are distinct from encoded row coordinates.

`Index.file` and `Index.rank` expose human-readable chess coordinates. Its textual form is the lowercase square name. An index's truth means its square is black; that geometric shade convention remains independent of participant ownership. Missing pieces or positions must therefore be tested with `is None`.

`Compass` holds direction arrays and the rank/file direction sets. These are reusable movement constants, not an enum that must contain every arithmetic result.

- [x] Direct FEN-order square encoding.
- [ ] Earlier file-major or transposed layouts.
- [x] Direction constants usable in ordinary array arithmetic.
- [ ] A finite vector enum required to absorb arbitrary operation results.

The coordinate encoding was settled in `169bf45`; the current `Index` name supersedes `Square`. `geometry.Color` and `Index.color` remain removed. The 2026-10-23 revision flips square truth to black, matching the new boolean piece-color convention without coupling squares to participants.

### D06. A piece has identity independently of its position

**Status: Agreed and implemented.**

Distinct piece instances remain distinct even when their type, color, and position-related attributes agree. Equality and hashing use object identity, allowing a side to contain multiple otherwise identical pawns, rooks, or promoted pieces.

`Piece(color)` and `Piece.fromnotation(symbol)` construct an unplaced piece. Color is a boolean: `False` means white and `True` means black, matching white's even and black's odd turn indices when counting from zero. Symbol case supplies color without requiring an owner. Its `index` is initially `None`, and its `position` reference is not bound until position placement. `Roster` resolves canonical FEN symbols to piece classes, while `Officer` enumerates promotion choices.

`Piece.side` is a read-only view of `piece.position.side[piece.color]`; there is no separate stored side or board reference. Position removal clears the index and active roster membership while retaining color and the existing position context. Unplaced or removed pieces produce no movement targets. A plain board can hold and export pieces without binding position context; placed movement queries require a position.

- [x] Color-only construction, followed by placement-time position binding.
- [ ] Construct every piece with a side and derive context from it, the superseded D18 model.
- [ ] Require owner context and an optional square in the piece constructor.

Color is intended to remain stable after construction so roster selection stays consistent. It remains an ordinary writable attribute; enforcement is explicitly deferred. Absence of a piece from the board is separate from the representation of an empty board slot in O06.

### D07. Board assignment owns the basic occupancy binding

**Status: Agreed and implemented for pointwise assignment.**

`Board` is the occupancy source of truth. Its present backend is a 64-slot list of `Piece | None`. Assigning a piece through `Board.__setitem__` sets its concrete `Index`; replacement clears the outgoing piece's index. Deletion empties a slot without shrinking the board. The base setter neither binds a position reference nor maintains participant rosters.

`Board.__setitem__` normalizes the key to `Index`, then performs the slot replacement inside `self.binding(key, value)`. The context uses a bare `yield`, exposing `None` as its bound value. `Board.binding` clears the outgoing piece's index before replacement and assigns the incoming index afterward. `Position.binding` wraps that context to remove the outgoing piece from its roster before replacement, then bind the incoming piece's `position` reference and add it to the color-selected roster afterward. `Position` inherits the setter unchanged.

Attachment after `yield` runs on successful completion. This context provides assignment bookkeeping, not rollback or atomicity; its body can observe an intermediate state before binding finishes. Cross-board assignment validation is explicitly deferred; assignment is not a coordinated transfer between positions.

`Board.get` translates a slot to a piece symbol or `-`; `Board.set` translates a symbol and delegates to normal assignment. Placement construction uses those same surfaces. `Board.__repr__` returns the FEN placement field, not a full game FEN.

These operations are low-level position changes, not complete legal moves. They do not clear an incoming piece's previous slot automatically, consume castling rights, or record history. Later king-reference maintenance remains O01/O02. Guards against inherited list resizing/reordering methods have been discussed but are deferred.

### D08. A side is an active roster and a game participant

**Status: Agreed; partly implemented.**

Each side holds its distinct active pieces. Captured pieces retain their affiliation but do not remain members of that active roster. A fixed list of original piece identities is unnecessary and fits custom positions poorly. Material difference can be reported without inventing a capture history for an imported position.

- [x] Plain `set[Piece]` as the side's container base.
- [ ] `structs.collection[Piece]` preserving `Side` as an operation result.
- [ ] A positional list encoding each piece's original identity.
- [ ] Use the captured-piece collection as the side's main roster.

A union, difference, or copy of a roster is an ordinary set of pieces; it is not another participating side. `position.side` contains white then black, with `position.white` and `position.black` as aliases. `bool(side)` is true for the installed black side and false for white. `other` resolves `position.side[not self]`. This truth is independent of roster size, including during empty or partial position construction; use `len(side)` to inspect roster emptiness. Set equality and membership retain their ordinary meanings; participant role uses identity rather than set equality.

`Side(position, *pieces)` stores its position and passes the collected pieces as one iterable to the set initializer. `Position.binding` updates roster membership during placement parsing and subsequent assignments through the inherited setter. Pawn direction uses piece color directly; `Side.forward` is no longer an API. The set choice is being reconsidered against indexed lists in O11; no replacement has been selected.

### D09. Each valid position side has a dedicated king reference

**Status: Agreed; initial binding implemented, validation and later maintenance pending.**

The scope is standard chess, and each side of a valid playable position must have exactly one king. `Side.king` refers to the same king object contained in its roster; its position remains `king.index`.

`Position.__init__` assigns each encountered king to its color-selected side during the post-parsing king scan, before binding declared castling partners in O04. This establishes the reference for a normally populated position; it does not validate exactly one king. Missing kings leave `Side.king` as `None`, and duplicate kings overwrite it. Choosing mutation-time updates and the validation boundary remains O01/O02. Plain boards and current positions can still represent partial setups; that need not weaken the intended playable-position invariant.

### D10. Movement search uses generators and boundary exceptions

**Status: Agreed and implemented for the current candidate generation.**

Piece classes define displacement patterns. `Melee` and `Ranged` share the surrounding search machinery and override a small generator hook. A ranged search yields empty destinations along a ray and then tests the first blocker as a capture. Pawn forward movement, double advances, and diagonal captures have explicit paths.

Off-board point operations raise `ValueError`; search catches or suppresses it around an individual direction or other deliberately bounded sequence. Suppression exits its context on the first exception. It does not resume at the following statement inside the context, so independent search directions must remain independent.

Occupancy and later king-safety rejection are boolean validation outcomes, rather than exceptions. The pawn's single advance and double advance are checked independently: a future king-safety rejection of the intermediate destination must not by itself suppress a legal double advance.

`targets` contains geometric/occupancy candidates. `squares` simulates each candidate and excludes those leaving an installed king unsafe; partial positions without a king retain their candidates. This is an initial king-safety filter, not complete legal-move validation. General attack queries and complete legality remain open in O07.

`King.squares` also adds validated castling candidates. Castling stays outside raw `King.targets`, preventing safety queries from recursively validating the opponent's castles.

Piece and side target collections, and filtered piece squares, use `algebra.Moves`, a specialization of `structs.collection[algebra.Move]`. Search already constructs `Move`, `Capt`, `Rush`, and `EnPassant` instances; filtering preserves those objects and their simulation context rather than upgrading plain indices. These chess collections need set operations, not the Cartesian operations supplied by the separate mathematical `indices` type.

### D11. A move is a target index with a recorded source and piece

**Status: Agreed and implemented for the current move model.**

`Move` subclasses the same bounded two-dimensional point specialization as `Index`; it cannot subclass the populated square enum. Its integer value represents the destination. `target` exposes that value as the named board square.

Construction records the moving piece, its source, and the target occupant at that time. `source` and `other` are snapshots rather than live properties. In contrast, the current boolean predicates deliberately inspect live occupancy. That distinction was made explicit in `854b906`.

- [x] Destination-oriented `Move`, based on `index`.
- [ ] Displacement-oriented `Move`, based on `array`.
- [x] Inherited equality/hash distinguish destinations only.
- [ ] Include piece, source, and move category in move equality/hash.

Destination equality is intentional when aggregating target squares. It does not make such a set a complete representation of distinct executable choices: promotion choices, different moving pieces, and path/history information may collapse. How execution and history use those distinctions is O08/O10.

Arithmetic on a contextual move is not a promise that a new move can be reconstructed from a destination alone. Coordinate calculations and move construction remain separate responsibilities.

### D12. Basic move distinctions stay available during search

**Status: Agreed direction; specialized behavior remains incomplete.**

`Move` and `Capt` validate meaningfully different occupancy conditions through the live `occupant(square)` hook. Ordinary moves treat ghosts as empty; ordinary captures ignore them. `EnPassant` overrides the hook to expose the actual occupant to inherited capture validation. `Rush` remains an explicit special move because a double advance creates a ghost on the intermediate square, during execution or simulation. `Castle(Spec)` similarly owns both king and rook movement. Moving all move classification out of piece search was considered, then narrowed to this partial separation.

`algebra.Pawn` supplies the shared pawn-only constructor and `piece: material.Pawn` annotation for `Rush`, `Promotion`, and `EnPassant`. `Rush` and `Promotion` retain their `Spec` role; `EnPassant` retains its `Capt` role.

`Jump(Spec)` supplies the midpoint and shared boolean checks for an unmoved piece with empty destination and midpoint. `Rush(Pawn, Jump)` and `Castle(Jump)` inherit those checks; geometry is supplied by their piece generators.

Promotion augments either an ordinary move or capture rather than replacing that distinction. The current `Promotion[Move]` and `Promotion[Capt]` select finite named classes, not freshly synthesized runtime classes. Each promotion instance owns its selected officer and its queen-first choice cycle. This implementation is retained as prototype context, not a requirement to emit all variants during square search.

Pawn diagonal search emits `EnPassant` when the target contains a `Ghost`, and `Capt` otherwise. `EnPassant` uses that ghost's `rusher` reference to validate the actual opposing pawn, removes it during execution or simulation, and restores it on simulation exit. `Rush` creates the ghost; expiry remains open in O05. Pawn generation does not emit promotion variants. `Check` and `Checkmate` currently provide notation suffixes, not detection algorithms. The next classification/notation boundary is O10.

### D13. Placement notation has explicit decoded layers

**Status: Placement layers and full-FEN notation codec implemented; engine integration, remaining state fields, position export, and validation deferred.**

| Type | Stored representation | Construction and output |
| --- | --- | --- |
| `notation.rank` | Expanded rank string, using `-` for empty squares | Constructor expands each empty-square digit; `str` compresses empty runs |
| `notation.board` | Tuple of expanded rank objects | Constructor accepts placement text or rank objects; `str` joins compressed ranks with `/` |
| `notation.serial` | Flat expanded board string | Constructor normalizes placement text or an already flat string; `str` uses rank/board conversion to emit placement text |
| `notation.position` | Named tuple with `board`, `bool`, `str`, `str`, `int`, `int` fields | Constructor decodes all six FEN fields; `str` reconstructs the full FEN |

`notation.position` exposes `placement`, `color` (black is true), `castling`, `en_passant`, `halfmove`, and `fullmove` properties. Castling declarations and the en passant target remain notation strings, including `"-"`; counters are integers. This codec owns no pieces or position bindings and adds no broader validation policy.

`Board` uses the flat representation to enumerate squares and delegates formatting back through these notation objects. Symbol-to-piece conversion belongs to the material/board boundary, not to the rank codec. `Piece.fromnotation(symbol)` resolves the type and boolean color without requiring a board or position. Normal assignment then supplies the location; a position's assignment additionally binds context and roster membership.

The `forsyth_edwards` argument intentionally differs between constructors: `Board` accepts only placement rows, while `Position` accepts a full six-field FEN. `Position` extracts the placement and castling fields, installs its side pair before passing placement to the base constructor, and binds declared partners after placement and king registration. The other input fields are not yet applied. Plain boards require no sides. The current APIs intentionally avoid requiring callers to assemble a second collection of `from_fen`/`from_flat` factories.

Only the placement field is currently supported by `Board`. `notation.position` replaces the earlier `notation.game` placeholder; `engine.Position` still splits its FEN directly and has not yet been wired to the codec. Runtime shape/symbol validation and the remaining position fields are O09. The direct placement order follows [FEN, section 16.1.3.1](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm).

### D14. Package and import boundaries

**Status: Baseline and implemented.**

`src/goochess` is the importable package; `src` itself is not the public package name. Target Python 3.14 or newer and use an editable installation for development. Tests import modules with `from goochess import module` and access objects through their module namespaces; package code uses relative module imports.

Cross-interacting modules need not be merged merely to remove every import cycle. Use module-qualified runtime references and deferred annotations where appropriate; imports used only for annotations belong under `TYPE_CHECKING`. This is not permission to execute cross-module lookups before initialization completes. The current `material`/`algebra` relationship still exists; complete decoupling has not been implemented or required.

### D15. Collaboration, code style, and tests

**Status: Agreed.**

Keep changes surgical and within the requested scope. A review or a request to fix named issues is not permission to redesign adjacent code or rewrite the user's prose. Update this record when an explicit discussion settles or changes a choice; do not silently promote a proposal to a decision.

Python source and tests use hard tabs, spaces around `=` including defaults/keywords, spaces around binary operators, and `...` rather than `pass`. Separate clauses/blocks with blank lines, except before the first clause in an enclosing body. Insert a blank line before `return`, `raise`, `break`, and similar statements unless they are the sole statement of the clause. The surrounding user-written code is the reference for ambiguous placement.

Use one test module per source module, grouping tests in classes by the tested type. Put reusable supporting data/helpers at class level, without unnecessary `ClassVar` annotations. Tests should describe the selected contract rather than preserve every abandoned implementation. Pyright uses basic checking, matching the project's intended strictness.

### D16. A position supplies its sides' owner context

**Status: Agreed and implemented. Resolves O03's side-ownership question.**

`Side(position, *pieces)` receives and stores its owning position during construction. `Position` creates both sides and installs the `side` pair before placement parsing begins. Role-based truth and opponent lookup require installation in that pair, not merely the presence of the owner reference.

- [x] Require the owning position in the side constructor.
- [ ] Bind the owner indirectly after side construction, the earlier selected approach.
- [ ] Introduce descriptors or a generic owner-binding framework for this assignment.

This retains the constructor binding introduced on 2026-10-23, now named `Side.position`, after the earlier indirect `Side.game` binding and its later `Side.board` version in D18. The separate position king scan registers initial references as described in D09. Roster synchronization and pending king-reference maintenance are tracked in O01; validation remains O02.

### D17. A position indexes its sides by color

**Status: Revised and implemented with boolean color and a side pair.**

`Position.side` is a `structs.switch` containing the actual white and black participants in that order. `False` selects white and `True` selects black. The `white` and `black` properties are derived aliases. A piece's intrinsic `color` selects its participant through its bound `position`; `Side.other` selects the opposing participant with `not self`.

The earlier prototype used `Game.sides`, a separate `Color` enum, and a stored `Side.color`; D18 then moved ownership into `Board`. Neither intermediate API is current. The 2026-10-23 model restored game-owned participants without restoring the enum or storing duplicate side color; the 2026-10-24 rename now places those participants on `Position`.

### D18. Board-owned sides carry affiliation and direction

**Status: Superseded by the 2026-10-23 color/context revision in D01/D06/D16/D17.**

This intermediate design gave every board its own participants, stored a piece's actual side, and derived board context and pawn direction from that affiliation. White was true and black was false. It removed the separate `Color` enum and `Index.color`.

The current model separates intrinsic boolean piece color from participating sides again: black is true, `Position` owns the sides, `Piece.position` is bound during position placement, and `Piece.side` is derived. Plain boards handle placement without participant context. `Color` and `Index.color` remain removed. The old fusion is history; the state/progression boundary is now explicit in D01. Remaining king, castling, ghost, and attack decisions stay open in their existing entries.

## Open decisions

### O01. Which mutation surface maintains position consistency?

**Status: Board assignment maintains occupancy/location; Position assignment adds context/rosters. King-reference maintenance remains open. Related: D06–D09, D16/D17.**

`Board.__setitem__` coordinates slot replacement through an overridable binding context. `Board.binding` maintains piece indices; `Position.binding` nests it and additionally maintains position context and the color-selected active rosters. Construction uses the same assignment surface, so position rosters are populated before the final scan that registers kings.

- [x] Keep key normalization and slot replacement in `Board.__setitem__`, with location handling in `Board.binding`.
- [x] Restrict position binding and roster coordination to a `Position.binding` override that nests the base context.
- [ ] Add side-local bookkeeping helpers if later king or rights handling needs them.

Giving a side further local bookkeeping remains a possible refinement, not a selected requirement. A helper must not initiate the same placement again or recurse into the board setter. Direct set mutation is not a position operation.

The inherited setter and binding contexts handle ordinary placement, replacement, deletion, and self-assignment. Index normalization happens before roster mutation, preserving state when an index is rejected. Position placement binds the incoming context, but cross-position validation and coordinated transfer remain explicitly deferred. The contexts expose no bound value beyond `None`, and their bodies do not promise a fully synchronized position; post-body attachment occurs only on success, without rollback on failure. The post-construction position scan registers kings until their later update seam is chosen. These behaviors have dedicated engine tests.

The remaining question is how king references follow later setup replacement or removal, and how complete moves coordinate multiple square writes. Position editing preserves the king's declared castling partners; movement flags and the presence of those same objects determine the remaining eligibility during play (O04/O08). There is no `departed` hook or separate rights mutation. FEN/setup binds declared partners after placement; later manual editing must curate partnerships and movement flags explicitly. The pointwise setter does not replace a move executor.

### O02. When is the king invariant validated?

**Status: Invariant agreed; validation boundary open. Related: D09.**

- [ ] Validate each completed position after construction and maintain the reference through controlled mutations.
- [ ] Provide a distinct completion/validation step for position editing.
- [ ] Require every individual board assignment to preserve the king-presence/reference invariant.

The first option is the current recommendation. An individual square write may be one intermediate step of construction or a move, so rejecting every temporary absence is likely to interfere with ordinary mutation. Missing and duplicate kings both need consideration at the completed-position boundary. An ordinary king move retains the same `Side.king` object; changing its position is different from replacing the king during setup editing.

Tests use empty or partial boards for occupancy and positions for contextual movement and rosters. Both currently permit partial positions; the ownership split does not select or implement a validation boundary. Exactly one king is only one validity check; it does not establish full position legality.

### O04. How are castling rights represented and updated?

**Status: Standard castling validation, application, and reversal implemented; king-owned partner dictionaries encode permission imported from full-FEN input. Remaining FEN field handling and full-FEN export remain pending.**

The 2026-10-27 revision replaces the fixed `Side.castle_short` and `Side.castle_long` flags with stable king-owned castling partners. Each king owns a `dict[mathematics.array, Rook]` named `rooks`. The keys are its existing relative starting offsets, `King.ᐊ = (-4, 0)` and `King.ᐅ = (3, 0)`, shared by both colors. A key records imported permission and its value identifies the particular eligible rook. The expected starting square is the king's recorded source plus that key; the rook's live `index` records its actual position. Side membership already supplies `rook.side.king`, so no reverse stored reference is added.

- [x] Keep designated rook identities in a king-owned dictionary keyed by relative starting offsets; membership records imported permission.
- [ ] Use an eligible-rook subroster as the authoritative rights state (earlier implementation).
- [ ] Mutate separate kingside/queenside remaining-rights flags during play and save them during simulation (earlier implementation).
- [ ] Keep separate fixed short/long setup flags and derive remaining eligibility from participant presence and movement flags (previous implementation).
- [ ] Store named optional eligible-rook references for the two wings.

Each king initializes its own empty dictionary. `Position(forsyth_edwards)` accepts a full six-field FEN and reads its third field after placement creates the actual pieces and the king scan establishes side references. The declarations `K`, `Q`, `k`, and `q` select a color, offset, and actual standard-position rook; `"-"` grants no partnerships. Construction asserts that declared participants have the expected king/rook types, color, and starting positions. The remaining fields are accepted but not yet applied, and full-FEN export from engine state remains pending.

Entries remain unchanged during play, validation, and simulation. Moving a recorded rook changes its `index` and `moved`; capturing it leaves the same partner reference with `index = None`. Replacing the corner occupant never automatically rebinds that reference, even if the replacement is a fresh unmoved rook. The dictionary is a castling partnership map, not the side's full rook roster; promotions may add unrelated rooks. No `departed` hook, rights mutation, or saved rights snapshot is needed. `Position.binding` remains a placement primitive, and `Piece.__call__` continues to assign the movement flag.

**Required distinction:** remaining rights and present legality are separate. Blocking pieces and attacks can temporarily prevent castling without destroying a right. Both rights exist in the initial position even though castling is blocked. A failed current legality test must therefore not remove a partnership. King/eligible-rook movement and loss of the eligible rook remove eligibility through movement flags or absence; reversal restores those values and placements. [FIDE, articles 3.8.2.1–2](https://handbook.fide.com/chapter/e012023)

`Castle.__bool__` returns false when the selected partnership was not granted. Permission still requires position-dependent validation; reading a validation predicate never changes the dictionary, even when its rook is missing or its path is blocked. Recomputing or caching that temporary result is a separate, deferred performance choice. Future full-FEN export must derive remaining rights from the partnerships and unmoved home participants, excluding temporary path clearance and attack feasibility; neither dictionary membership alone nor the full castle predicate represents that field. [FEN distinguishes rights from immediate feasibility](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm).

`King.squares` generates two-square horizontal targets (`C1`, `G1`, `C8`, or `G8` in the standard position); direct `Castle` callers share that geometry contract. The king's home square follows from the standard-position and consistent-movement-flag assumptions rather than a separate geometry check. `Castle.long` derives the wing from the target rather than storing another selector. `Castle(target, king)` retrieves its partner from the selected dictionary key or records `None` when permission is absent. It records the expected rook source from the move's source plus that key, without rediscovering the current corner occupant. Reversal uses that recorded square rather than the rook's live index after movement. Boolean validation inherits `Jump`'s empty destination/midpoint and unmoved-piece checks, then checks that the recorded rook exists, remains unmoved, and still occupies that corner, plus additional queenside B-file clearance. It checks source safety directly, crossing safety through an ordinary `Move` simulation, and destination safety through the complete castle simulation. Attacks on the rook or the queenside B-file alone do not prohibit castling. These probes restore the position even on early return.

`Castle.apply()` assumes the candidate has been validated in the current position, then moves the king and the rook. Application and reversal assert only that the recorded optional rook exists, without repeating castling eligibility checks. `Castle.undo()` reverses the rook before delegating to the king reversal; a valid castle requires an unmoved rook, so its previous flag is known to be `False`. The inherited simulation context preserves the king's prior movement flag and reverses placement; the unchanged partner dictionary needs no preservation. `King.squares` exposes castling while raw `King.targets` remains limited to ordinary adjacent moves, avoiding recursive safety queries.

### O05. How does the single ghost interact with occupancy and captures?

**Status: One shared reference in current-position context agreed; in-board ghosts and move-validation transparency implemented. Authoritative reference and lifecycle API remain open.**

- [x] One optional shared ghost reference rather than separate authoritative side references.
- [x] Current-position context on `Position`, consistent with D01's state/progression boundary.
- [ ] Put that reference on the future `Game` runner rather than in the position it runs.
- [ ] Put that reference on plain `Board`, the earlier selection when that class was intended to hold complete state.
- [ ] Independently stored live ghost references on both sides.
- [ ] Store side ghosts and rotate a second authoritative reference between them.

No authoritative ghost slot exists in code. En passant availability belongs to the complete current position, now named `Position`; the earlier owner names tracked the evolving state boundary. This identifies the owning context without finalizing a field name, the representation, or the lifecycle API. Any side-level convenience view could be derived rather than stored independently. The opportunity is limited to the opponent's immediate reply. [FIDE, articles 3.7.3.1–2](https://handbook.fide.com/chapter/e012023)

The physical representation is a different, still open decision:

- [ ] Keep the ghost outside occupancy as metadata describing the passed square and actual rushed pawn. This was the assistant's recommendation, not an accepted choice.
- [x] Keep a ghost in the occupancy model, with explicit semantics distinguishing transparent/empty behavior from en passant capturability.

`Move.occupant(square)` reads live occupancy and maps `Ghost` to `None`. Move and capture predicates use this hook, so ordinary pieces can land on ghosts and sliding rays continue through them. `EnPassant.occupant` returns the raw occupant, retaining inherited opposing-color capture validation. The saved `Move.other` remains the raw construction-time occupant for exact reversal. The earlier `Board.empty` experiment remains removed. Ghosts still participate in side rosters but generate no targets; their inherited `-` symbol hides them in placement export.

`EnPassant.other` is the construction-time destination occupant, required to be a `Ghost`. Its `rusher` reference identifies the captured pawn without a separate `victim` attribute. `middle` identifies the destination file and source rank and remains available for restoration after capture clears the rusher's index. Validation checks that the same opposing rusher occupies that square, and execution and simulation remove it through ordinary position assignment. Context exit restores all three affected squares, including the original ghost and pawn, with indices and rosters maintained by the binding machinery. This repairs the extra occupancy change needed for king safety without implementing the lifecycle API.

`Ghost(rusher)` retains a reference to the represented `Pawn` and takes its color at construction. `Rush` creates it on the intermediate square during execution or simulation; undo removes it before restoring the pawn. Standard-chess rushes do not cross existing ghosts, so the intermediate-square check requires `None` and no extra occupant snapshot is stored. The future `Game` runner will manage expiry as play advances, after the opponent's immediately following move; the ghost itself belongs to the current position state.

Expiry, history undo of availability, and initialization from full FEN are not implemented. The FEN target can be present even without an available capturing pawn; do not confuse serialization of that target with legal capture availability. [FEN, section 16.1.3.4](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm)

### O06. What represents an empty square?

**Status: Reopened; under active discussion together with O05.**

The current implementation uses `None`. The earlier decision to keep it is being reconsidered explicitly; it should not be treated as permanent merely because current code/tests use it.

- [ ] Retain `None` as the representation of an ordinary empty square.
- [ ] Introduce an `Empty(Piece)` or another explicit empty-square value with a deliberate shared occupancy protocol.

An explicit empty object can make selected operations uniform, but it does not by itself make a ghost transparent to rays yet selectively capturable by a pawn. Missing occupancy, geometric attacks, and en passant eligibility still need distinct meanings. An empty-object alternative must explain whether it has a color or position context, whether it enters a roster, and how it serializes. A shared empty singleton cannot carry a distinct position for every board slot.

The unplaced-piece convention `piece.index is None` in D06 is a separate question; changing empty board slots need not change it.

### O07. What query establishes attacks and king safety?

**Status: Initial occupied-king safety query and candidate filtering implemented; general attack API and complete legality open.**

Attacks cannot be defined as the opponent's fully legal destinations: pinned pieces still attack, and pawn forward moves differ from pawn diagonal attacks. Validating each side through the other's legal moves would also create a circular definition. [FIDE, articles 3.1.3 and 3.9](https://handbook.fide.com/chapter/e012023)

- [ ] A direct piece/side `attacks(square)` predicate or corresponding position query.
- [ ] A generated collection of attacked squares, independent of legal-move filtering.
- [ ] Cached attack information with explicit invalidation, only if later justified.

`King.safe` checks whether the occupied king square occurs in the opposing side's raw `targets`, without consulting their filtered `squares`. `Piece.squares` temporarily applies each candidate and retains it only when its side's installed king is safe; missing kings permit partial-position tests. En passant simulation includes removal of the actual pawn, so discovered attacks through either vacated pawn square are visible.

This narrow query concerns an occupied king square. It is not a general attack map: pawn forward movement and empty diagonals make raw targets unsuitable for arbitrary empty squares. Castling reuses this query by simulating the king on its crossing square, then simulating the complete castle for destination safety. Evaluate safety against the position resulting from the complete candidate move, including special-move effects. A general empty-square attack query remains open; no attack-map cache is introduced.

### O08. Where do execution, simulation, and history live?

**Status: Move-owned ordinary/en passant/castling execution, placement and movement-flag contexts, and initial king-safety filtering implemented; complete transitions and game coordination pending.**

`move.apply()` commits the move; moves are not callable. Rule developers implement forward effects in `apply()` and reversal in `undo(*, moved: bool)`, both returning the move. The base `simulated` property saves the previous movement flag locally. It calls `self.apply()` and yields the move inside a `try`/`finally` that passes that saved value to `self.undo`, including when the body raises. Direct callers of `undo` likewise supply the prior flag. Castling partner dictionaries are never mutated and need no snapshot. Each property access returns a fresh generator context manager. Subclasses override those hooks rather than the context. Construction-time `source` and `other` remain unchanged, allowing sequential simulation of the same move. Application asserts that the piece still occupies that source and the target still contains that same occupant.

`Piece.__call__` is the same relocation primitive in either direction and owns the movement-flag assignment: `piece(target)` applies placement and defaults to `moved = True`, while `piece(source, kept = other, moved = previous)` restores placement and the saved flag. The target is positional-only; `kept` and `moved` are keyword-only. It has no history responsibility. `Position.binding` maintains indices, context references, and rosters around all those assignments; simulation does not bypass roster updates. `Rush.apply()` creates a ghost after moving the pawn; `Rush.undo()` removes it before delegating to the base reversal. `EnPassant.apply()` removes its ghost-linked rusher after ordinary placement; `EnPassant.undo()` restores that pawn before delegating to the base reversal. `Castle` similarly applies and reverses the additional rook movement. Move-owned execution does not yet apply promotion effects.

The immediate purpose remains inspecting one candidate move for king safety, preserving its placement effects and previous movement flag, which also restore derived castling eligibility. It is not a complete reversible state transition or a faithful deeper-search simulator. `undo()` is an explicit reversal hook supplied with the prior state, not a history-navigation API. No execution record or saved movement flag is retained on the move; temporary preservation lives in the generator context. Complete-state simulation and history undo are deferred. F02 records the longer-term direction and the special-move limitations that already matter for standard chess.

`Position` supplies rule context. A future `Game` runner will own a current position and coordinate progression, history, and traversal (D01); no runner is implemented yet. Complete transitions must preserve or restore king references, castling rights, en passant availability, and turn state when those features exist. O07 records the initial king-safety filter and the remaining general attack-query boundary.

- [x] Move-owned execution and temporary placement for king-safety inspection, with future game coordination.
- [ ] Game-owned application/reversal of move records.
- [ ] A separate operation/undo record if a concrete need appears.

Do not treat `Board.__setitem__` alone as that API. Do not assume a destination-index hash identifies a complete executable choice or a game state. Game-position keys, transpositions, repetition, complete object-graph serialization, and search strategy are separate later decisions. Snapshot fields from D11 must not be silently changed into live history lookups.

### O09. Where do full FEN and validation belong?

**Status: Placement layering and full-FEN notation codec implemented; engine integration, remaining state fields, position export, and validation deferred.**

`Board(forsyth_edwards)` consumes only the placement rows and exports that same field. `Position(forsyth_edwards)` intentionally accepts a full six-field FEN instead: it extracts placement for the base constructor and uses the third field to bind the partners described in O04. The active-color, en passant, and counter fields are accepted but not yet applied. Castling rights and those remaining fields belong to the complete current position and cannot be reconstructed from placement alone. Full-FEN export remains unimplemented; `Position` currently inherits placement-only representation.

- [x] Implement `notation.position` as a six-field named tuple with full-FEN construction, named access, and formatting.
- [ ] Wire the codec into `engine.Position` and apply the remaining fields to position context.

Rank widths, total dimensions, accepted symbols, malformed input behavior, and the relationship between setup validation and playable-game validation need deliberate coverage when implemented. Full FEN import cannot truthfully reconstruct every piece's complete movement history; use the fields that actually exist rather than inventing provenance.

### O10. When are special move choices and final notation attached?

**Status: Partial separation agreed in D12; the remaining boundary is deferred.**

Basic moves, captures, rushes, and the current ghost-based en passant prototype stay available to piece search. Castling has explicit behavior exposed through `King.squares`. Promotion enrichment and final check/disambiguation annotations still need to be placed deliberately.

- [ ] Detect geometric/occupancy targets first, then enrich a selected move with its special behavior and notation.
- [ ] Generate the necessary specialized executable choices during legal-move enumeration.
- [ ] Use a small combination of those approaches, keeping ordinary search simple.

The existing promotion compositor is available; it is not proof that all classification must occur during candidate generation. Target-square aggregation intentionally collapses choices, so it cannot alone enumerate every promotion option. SAN disambiguation and actual check/checkmate detection remain deferred.

### O11. Does a side need ordered or stable piece slots?

**Status: Reopened discussion; the set remains the selected implementation pending a decision. Related: D08, O01.**

- [ ] Retain the identity set as the active roster.
- [ ] Use an ordered active-piece list without interpreting its positions as original chess identities.
- [ ] Introduce stable internal piece slots, with an explicit distinction between allocated pieces and active membership, if a concrete use requires them.

A list can load custom FEN positions if its indices are merely internal identifiers; the unsupported assumption is that those indices recover original piece identities. Stable slots may serve ordering or bookkeeping, but neither lists nor sets automatically follow replacement of a different container's square. Both retain object references and both require synchronization with occupancy changes.

No new need for stable slots has been established by the roster setter alone. Keeping the active set is the current recommendation; a different identity/order requirement should motivate any change.

## Resolved follow-ups

### O03. How are position and side references bound?

**Status: Ownership resolved in D06/D16/D17; identifier retained for history.**

`Position` constructs each `Side` with itself as owner and installs both participants before parsing placement. Placing a piece on the position binds `piece.position`; its read-only `side` property selects the corresponding participant by intrinsic boolean color. A piece stores neither a second side reference nor a board reference.

Plain boards do not bind position context or own sides. This revises the indirect owner binding and the later board-owned fusion, without introducing a descriptor or generic binding framework.

### O12. Should participant ownership and color become one entity?

**Status: The D18 fusion is superseded; boolean color and position-owned participants are selected.**

- [x] Store intrinsic boolean piece color and derive its participant from position context.
- [ ] Let pieces refer directly to board-owned sides and derive allegiance and orientation from those participants, the former D18 model.
- [ ] Restore a separate `Color` enum.

Symbol parsing supplies color without needing an owner. Position placement binds context and adds the piece to its active roster. Black is true for piece color, installed side identity, and square shade; the meanings remain distinct. Pawn direction and capture allegiance use piece color directly, while `piece.side.other` exposes the opposing participant. Set equality and membership retain their ordinary meanings.

`geometry.Color` and `Index.color` remain removed. No color immutability enforcement is requested. Representations and APIs for the remaining king, castling, ghost, and attack decisions stay open in their existing entries.

## Future directions

These are agreed longer-term goals, with implementation deliberately deferred. Standard chess remains the immediate scope in D01. The directions below should guide the responsibility boundaries we build together, without requiring a general framework before concrete needs establish its shape.

### F01. Custom rules and chess variants

**Status: Planned direction; API and implementation deferred.**

Support customizing game rules and constructing chess variants through a composable API. Movement patterns, validation, move effects, and position context should cooperate through explicit responsibilities, so extending a rule does not require duplicating the engine. Standard chess should be one supported rule configuration rather than a collection of hidden assumptions that every extension must satisfy.

The extension mechanism remains open. This goal does not yet select a registry, configuration format, inheritance scheme, or separate rules engine. It builds on the existing piece, move, and position boundaries, subject to further review as variants become concrete.

### F02. Faithful algebraic move simulation

**Status: Planned direction; full transition and reversal design deferred. Related: O05, O07, O08, F01, F03.**

Evolve `with move.simulated:` into faithful simulation of the complete move, with the same position effects as actual execution and exact restoration afterward. Compose and reverse all effects: relocation, captures on other squares, secondary piece movement, promotion, movement flags, castling rights, en passant availability, turn state, and relevant counters. Preserve piece identities and restore position bindings and rosters consistently. The eventual contract should support nested simulations and customized rules without relying on standard-chess shortcuts. The concrete representation of effects and saved state remains open.

The immediate development priority is one correctly applied and reversed move. Deeper playback and branching traversal are advanced future work in F04, to follow once that foundation is sound.

The current context restores placement, the displaced destination occupant, and the previous movement flag; these also restore derived castling eligibility without changing its partner dictionaries. En passant additionally removes and restores the pawn captured on another square. This is a deliberate intermediate step, not proof of complete standard-chess legality:

- **En passant already requires the extra occupancy change in standard chess.** With White Kh5/Pg5 and Black Ka8/Ra5/Pf7, `...f7-f5` is legal. But `g5xf6 e.p.` removes both f5 and g5, exposing Kh5 to Ra5. Moving only the white pawn leaves f5 blocking the rook and gives the wrong safety result. The current prototype now removes and restores that actual pawn during simulation. This counterexample follows [FIDE articles 3.7.3.1–2 and 3.9.2](https://handbook.fide.com/chapter/e012023).
- **Castling needs both validation probes and the complete move.** Standard rules require rights, clearance, and safety at the king's starting, crossing, and destination squares. The current `Castle` uses an ordinary king-placement probe for crossing safety and moves both king and rook for destination safety, application, and reversal. This implements standard castling; variant-specific starting arrangements and rules need their own validation and effects. See [FIDE articles 3.8.2–3.8.2.2](https://handbook.fide.com/chapter/e012023) and O04.

These limitations do not authorize implementing the larger simulator now. Correct special-move occupancy for immediate legality checks can be addressed before the full reusable transition API is selected.

### F03. Deterministic minimax engine

**Status: Planned exploration; implementation deferred. Depends on complete legal-move enumeration and F02.**

Explore a deterministic chess AI using minimax game-tree search. Faithful simulations should allow successive candidate moves to be applied, evaluated, and taken back without altering sibling branches or the actual game. This uses the intended separation between `Position` as current state and the future `Game` runner as progression/history coordination.

F04 records the shared history and traversal direction that should eventually support this exploration.

Evaluation, search depth, move ordering, and search optimizations remain future design questions. No particular algorithm refinements or caching strategy are selected. Variant support must obtain legal transitions and outcomes from the configured rules rather than assume that standard-chess displacement shortcuts remain valid.

### F04. Move history and branching traversal

**Status: Agreed advanced future direction; implementation deferred until single-move application, simulation, and reversal are correct. Related: O08, F02, F03.**

Develop history and playback in stages:

- [ ] Begin with a list of moves describing one linear game history.
- [ ] Upgrade history to a rooted tree of moves. Linear play remains a single path; undoing and choosing another continuation adds a branch without discarding the previous continuation.
- [ ] Support backtracking and following existing or new branches, keeping the current position synchronized with the selected path through move application and reversal.
- [ ] Retain traversal history, including backtracks, as well as the move branches themselves. A tree alone does not record the chronological order in which its branches were visited; the representation of that additional history remains open.
- [ ] Reuse the same application, reversal, and traversal mechanisms to explore hypothetical move trees for minimax and related search, while distinguishing speculative exploration from played game history.

This is a progression from the single-move foundation, not a requirement to implement deeper simulation, tree structures, or navigation APIs during the current development steps.

## Current implementation gaps

These are observations, not authorization to fix unrelated code whenever this file is edited.

- King references are assigned during the initial `Position` king scan, but exactly-one-king validation is not implemented.
- `Board.__setitem__` performs slot replacement within `Board.binding`; `Position.binding` extends index bookkeeping with position binding and active roster synchronization. Later king replacement or removal does not maintain king references. The contexts do not provide rollback or a complete-position invariant inside their bodies.
- Cross-board assignment validation and coordinated transfer between positions are explicitly deferred.
- Active-side state, relevant counters, an authoritative ghost reference, and full-FEN export still need concrete APIs on `Position`. Construction accepts a full six-field FEN and currently applies placement and castling declarations, binding stable king-owned partners; movement flags and those participants' presence determine remaining rights. Full-FEN export must derive those rights without path or attack checks.
- `move.apply()` commits execution, and the shared `move.simulated` context calls the move's `apply()` and `undo()` hooks to restore placement, captured pieces, and the previous movement flag afterward. Rush creates/removes a ghost; en passant also removes/restores its separate pawn victim; castling moves and restores its rook. Candidate filtering uses `King.safe`. History undo and faithful deeper-state simulation are deferred. Promotion effects, general attack queries, and ghost expiry remain unimplemented. `Position` owns participants and supplies piece context; the future `Game` runner and progression/history remain unimplemented.
- Ghost transparency is implemented through the move occupancy hook. Expiry and an authoritative availability reference remain unresolved in O05; O06 retains the separate ordinary-empty representation question.
- Color remains writable by explicit choice; changing a registered piece's color would leave its current roster stale.

## Selected history anchors

These commits explain retained choices. They are navigation aids, not a requirement to preserve intermediate designs.

| Commit | Relevance |
| --- | --- |
| `7fb69e2` (`develop`) | Historical baseline for this record |
| `854b906` | Separate recorded move source/occupant from live validation |
| `61d766c` | Shared basic movement generation and direction-set arithmetic |
| `7267d7a`, `16ec617` | Refine movement search and exact midpoint support |
| `a0d3c14` | Module-qualified imports and deferred references for interacting modules |
| `6aae033` | Per-instance promotion selection and officer cycling |
| `7c4b24a` | Finite promotion compositor and partial material/algebra separation |
| `169bf45` | Direct FEN board order |
| `1c1ec3f`, `081a665` | Piece-symbol construction, then color-only construction and placement-time binding |
| Working discussion, 2026-10-21 | Plain-set Side, required king reference, curated castling eligibility, and an initial Game-owned ghost proposal; side ownership was subsequently settled in D18, and ghost ownership later revised to Board while its occupancy semantics remain open |
| Follow-up implementation, 2026-10-21 | D16 settles indirect side ownership binding and corrects plain-set constructor forwarding; the fusion later moves ownership from Game to Board |
| Mapping prototype, 2026-10-21 | D17 evaluates color-keyed participants and intrinsic side color, then is superseded by D18; key validation before roster mutation is retained |
| Side-ownership fusion, 2026-10-21 | D18 gives Board actual sides, binds pieces to Side, derives board/direction from affiliation, and removes Color and Index.color; the initial foreign-side guard is subsequently deferred, and Side truth now denotes its white/black role |
| State/progression clarification, 2026-10-21 | D01 assigns complete current-position information to Board and progression/history to Game; O05 consequently moves the agreed ghost slot from Game to Board, without settling its representation or implementing the broader state model |
| Boolean color and game context, 2026-10-23 | Intrinsic piece color returns as a boolean with black true, matching zero-based turn parity and square truth. Game owns sides again, Piece.game is bound on game placement, Piece.side is derived, and Board retains placement/notation without participants. This supersedes D18 and the prior complete-state Board boundary; remaining ghost ownership and rule-state APIs need review |
| State/progression naming, 2026-10-24 | The former Game state class becomes Position(Board), Piece.position and Side.position supply current-state context, and a future Game runner is reserved for composition, progression, and history. Intrinsic boolean color is unchanged; remaining position fields and the runner are not yet implemented |
| Assignment binding context, 2026-10-24 | Board keeps the sole setter and exposes binding as a context manager; Position nests that context for roster/context bookkeeping. The unused Board.empty experiment is removed without settling ghost occupancy semantics |
| Lightweight move contexts, 2026-10-24 | `move()` performs relocation and sets `moved`; `with move:` temporarily changes placement without changing `moved`, then restores placement through the same Piece relocation helper. This supersedes the initial saved-flag/public-undo implementation; faithful deeper simulation and history undo remain deferred |
