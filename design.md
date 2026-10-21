# Design record

This is the working reference for Goochess design discussions: what we have chosen, why we chose it, what the code currently implements, and what still needs a decision. It records the model we are building together rather than prescribing the rest of the implementation.

Jump to [decisions](#decisions-and-retained-baseline), [open questions](#open-decisions), or [implementation gaps](#current-implementation-gaps).

## Reading and maintaining this record

- **Agreed** means an explicit design choice. It can still be awaiting implementation.
- **Baseline** describes a retained contract in the current framework, without declaring every implementation detail permanent.
- **Open** means no alternative has been selected. Recommendations are labelled as recommendations.
- **Deferred** means the subject has deliberately been left for later.
- A checked alternative means **selected**, not necessarily implemented. An unchecked alternative in a closed decision is historical; in an open decision it remains under consideration.
- When we change a decision, update its existing entry and retain a short explanation of the superseded choice. Keep the identifiers stable so later discussions can refer to them.
- An experimental edit, a passing test, or an assistant recommendation does not by itself settle a design question. Record disagreements between the intended model and the implementation explicitly.

The historical starting point is `develop` at `7fb69e20e4a0df819a4adc37039c785483d37a03`. Earlier code is a source of inspiration, not the specification for this framework. The initial record was reviewed on 2026-10-21 against `50f5c06` and the working changes to `Side` on the `side` branch; it now includes the authorized side-ownership fusion in D18. The mathematical framework already present at `develop` is retained as baseline context; this record does not reconstruct its earlier development.

## Responsibility map

| Component | Responsibility | References |
| --- | --- | --- |
| `array`, `index`, mathematical collections, `fraction` | Reusable mathematics without chess knowledge | [mathematics.py](src/goochess/mathematics.py), [mathematics tests](tests/test_mathematics.py) |
| `Index`, `Compass` | Standard chess board geometry and directions | [geometry.py](src/goochess/geometry.py), [geometry tests](tests/test_geometry.py) |
| `rank`, `board`, `serial` | Placement notation and its decoded representations | [notation.py](src/goochess/notation.py), [notation tests](tests/test_notation.py) |
| `Piece` and its subclasses | Piece identity, location/context references, and movement patterns | [material.py](src/goochess/material.py), [material tests](tests/test_material.py) |
| `Move`, `Capt`, and related classes | Move targets, move records, validation predicates, and move notation | [algebra.py](src/goochess/algebra.py), [algebra tests](tests/test_algebra.py) |
| `Board` and `Side` | Square occupancy, participating rosters, allegiance/orientation, and placement import/export | [engine.py](src/goochess/engine.py), [engine tests](tests/test_engine.py) |
| `Game` | Empty Board subclass reserved for later temporal game context | [engine.py](src/goochess/engine.py) |

## Decisions and retained baseline

### D01. Standard chess, mutable positions, and explicit move records

**Status: Agreed direction; execution and game-tree search are not implemented.**

The current scope is standard chess. `Board` represents a position through mutable square occupancy and owns its two sides. `Game` is currently an empty subclass reserved for later temporal game context; a plain board remains usable independently. A move describes a transition around one moving piece and its destination, rather than requiring a newly constructed board for every candidate.

That compact move model must still accommodate effects involving other pieces: captures, the rook in castling, promotion, and en passant. It does not imply that every transition changes only two board slots. Execution, reversal, and game-tree traversal remain open in O08.

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

`collection` provides set operations that preserve its concrete collection class. Its construction and reconstruction convention is variadic items. `arrays` and `indices` build on that mathematical contract.

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

`Index.file` and `Index.rank` expose human-readable chess coordinates. Its textual form is the lowercase square name. An index's truth means its square is white; that geometric shade convention remains independent of participant ownership. Missing pieces or positions must therefore be tested with `is None`.

`Compass` holds direction arrays and the rank/file direction sets. These are reusable movement constants, not an enum that must contain every arithmetic result.

- [x] Direct FEN-order square encoding.
- [ ] Earlier file-major or transposed layouts.
- [x] Direction constants usable in ordinary array arithmetic.
- [ ] A finite vector enum required to absorb arbitrary operation results.

The coordinate encoding was settled in `169bf45`; the current `Index` name supersedes `Square`. D18 removes `geometry.Color` and `Index.color`, while retaining the parity-based truth convention.

### D06. A piece has identity independently of its position

**Status: Agreed and implemented.**

Distinct piece instances remain distinct even when their type, side, and position-related attributes agree. Equality and hashing use object identity, allowing a side to contain multiple otherwise identical pawns, rooks, or promoted pieces.

`Piece(side)` and `Piece.fromnotation(symbol, board)` construct an unplaced piece affiliated with an actual side. Its `index` is initially `None`; constructing it does not add it to the active roster. Its read-only `board` property derives context from `side.board`, so a piece constructed with a board's side already has board context before placement. `Roster` resolves the canonical FEN symbols to piece classes, while `Officer` enumerates promotion choices.

Removing a piece clears its `index` and active roster membership while retaining its side and derived board context. An unplaced or removed piece produces no movement targets. Absence of a piece from the board is distinct from the representation of an empty board slot; the latter is being revisited in O06.

- [x] Construct every piece with a side and derive board context from it.
- [ ] Color-only piece construction, followed by placement-time board binding.
- [ ] Require board and optional position arguments in the piece constructor.

The color-only construction boundary in `081a665` was superseded by D18. Indirect side ownership binding remains settled in D16, now with `Board` as owner.

### D07. Board assignment owns the basic occupancy binding

**Status: Agreed and implemented for pointwise assignment.**

`Board` is the occupancy source of truth. Its present backend is a 64-slot list of `Piece | None`, with board-owned white and black sides. Assigning a piece through `Board.__setitem__` sets its concrete `Index` and adds it to its side's active roster. Replacing a piece removes the outgoing piece from its roster and clears its index. Deletion empties a slot without shrinking the board.

Keys are normalized to `Index` before mutation. Cross-board assignment validation is explicitly deferred. Assignment performs no side transfer or rebinding; the current setter leaves ownership context with the piece's existing side.

`Board.get` translates a slot to a piece symbol or `-`; `Board.set` translates a symbol and delegates to normal assignment. Placement construction uses those same surfaces. `Board.__repr__` returns the FEN placement field, not a full game FEN.

These operations are low-level position changes, not complete legal moves. They do not clear an incoming piece's previous slot automatically or update castling/history state. Later king-reference maintenance remains O01/O02. Guards against inherited list resizing/reordering methods have been discussed but are deferred.

### D08. A side is an active roster and a board participant

**Status: Agreed; partly implemented.**

Each side holds its distinct active pieces. Captured pieces retain their affiliation but do not remain members of that active roster. A fixed list of original piece identities is unnecessary and fits custom positions poorly. Material difference can be reported without inventing a capture history for an imported position.

- [x] Plain `set[Piece]` as the side's container base.
- [ ] `mathematics.collection[Piece]` preserving `Side` as an operation result.
- [ ] A positional list encoding each piece's original identity.
- [ ] Use the captured-piece collection as the side's main roster.

A union, difference, or copy of a roster is an ordinary set of pieces; it is not another participating side. The board's `white` and `black` attributes identify its participants. `bool(side)` means white or black: true for the installed white side and false for the black side. `other` and `forward` derive the opposing side and movement orientation from that role. This truth is independent of roster size, including during empty or partial board construction; use `len(side)` to inspect roster emptiness. Set equality and membership retain their ordinary meanings; side identity establishes allegiance.

`Side` uses built-in `set`, retaining its variadic piece interface by passing the collected pieces as one iterable to the set initializer. Its board binding is described in D16. `Board.__setitem__` updates roster membership during placement parsing and subsequent assignments. The set choice is being reconsidered against indexed lists in O11; no replacement has been selected.

### D09. Each valid game side has a dedicated king reference

**Status: Agreed; initial binding implemented, validation and later maintenance pending.**

The scope is standard chess, and each side of a valid playable `Game` must have exactly one king. `Side.king` refers to the same king object contained in its roster; its position remains `king.index`.

`Board.__init__` assigns each encountered king to its side during the post-parsing king scan. This establishes the reference for a normally populated position; it does not validate exactly one king. Missing kings leave the reference unset, and duplicate kings overwrite it. Choosing mutation-time updates and the validation boundary remains O01/O02. Lower-level `Board` construction can still represent partial positions; that need not weaken the intended valid-`Game` invariant.

### D10. Movement search uses generators and boundary exceptions

**Status: Agreed and implemented for the current candidate generation.**

Piece classes define displacement patterns. `Melee` and `Ranged` share the surrounding search machinery and override a small generator hook. A ranged search yields empty destinations along a ray and then tests the first blocker as a capture. Pawn forward movement, double advances, and diagonal captures have explicit paths.

Off-board point operations raise `ValueError`; search catches or suppresses it around an individual direction or other deliberately bounded sequence. Suppression exits its context on the first exception. It does not resume at the following statement inside the context, so independent search directions must remain independent.

Occupancy and later king-safety rejection are boolean validation outcomes, rather than exceptions. The pawn's single advance and double advance are checked independently: a future king-safety rejection of the intermediate destination must not by itself suppress a legal double advance.

These are currently geometric/occupancy candidates. Calling them fully legal moves would overstate the implementation. Attack detection and complete legality remain open in O07.

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

`Move` and `Capt` validate meaningfully different occupancy conditions. `Rush` remains an explicit special move because executing a double advance will create temporary game state. Castling is also expected to be explicit. Moving all move classification out of piece search was considered, then narrowed to this partial separation.

Promotion augments either an ordinary move or capture rather than replacing that distinction. The current `Promotion[Move]` and `Promotion[Capt]` select finite named classes, not freshly synthesized runtime classes. Each promotion instance owns its selected officer and its queen-first choice cycle. This implementation is retained as prototype context, not a requirement to emit all variants during square search.

`EnPassant` is capture-related, but its actual victim and occupancy rules depend on O05/O06. Ordinary pawn generation currently does not emit promotion or en passant variants. `Check` and `Checkmate` currently provide notation suffixes, not detection algorithms. The next classification/notation boundary is O10.

### D13. Placement notation has explicit decoded layers

**Status: Agreed and implemented; validation and full FEN deferred.**

| Type | Stored representation | Construction and output |
| --- | --- | --- |
| `notation.rank` | Expanded rank string, using `-` for empty squares | Constructor expands each empty-square digit; `str` compresses empty runs |
| `notation.board` | Tuple of expanded rank objects | Constructor accepts placement text or rank objects; `str` joins compressed ranks with `/` |
| `notation.serial` | Flat expanded board string | Constructor normalizes placement text or an already flat string; `str` uses rank/board conversion to emit placement text |

`Board` uses the flat representation to enumerate squares and delegates formatting back through these notation objects. Symbol-to-piece conversion belongs to the material/board boundary, not to the rank codec. `Piece.fromnotation(symbol, board)` resolves symbol case once to the board's actual white or black side. Both sides are installed and bound before parsing begins. The current APIs intentionally avoid requiring callers to assemble a second collection of `from_fen`/`from_flat` factories.

A symbol identifies a white or black role, but does not identify a per-board participant. The board argument supplies the context needed to select that actual side. Passing the board is the current convenience API; supplying the side context another way remains an unimplemented alternative, with none selected.

Only the placement field is currently supported by `Board`. `notation.game` is a placeholder. Runtime shape/symbol validation and the remaining game fields are O09. The direct placement order follows [FEN, section 16.1.3.1](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm).

### D14. Package and import boundaries

**Status: Baseline and implemented.**

`src/goochess` is the importable package; `src` itself is not the public package name. Target Python 3.14 or newer and use an editable installation for development. Tests import `goochess`; package code uses relative imports.

Cross-interacting modules need not be merged merely to remove every import cycle. Use module-qualified runtime references and deferred annotations where appropriate; imports used only for annotations belong under `TYPE_CHECKING`. This is not permission to execute cross-module lookups before initialization completes. The current `material`/`algebra` relationship still exists; complete decoupling has not been implemented or required.

### D15. Collaboration, code style, and tests

**Status: Agreed.**

Keep changes surgical and within the requested scope. A review or a request to fix named issues is not permission to redesign adjacent code or rewrite the user's prose. Update this record when an explicit discussion settles or changes a choice; do not silently promote a proposal to a decision.

Python source and tests use hard tabs, spaces around `=` including defaults/keywords, spaces around binary operators, and `...` rather than `pass`. Separate clauses/blocks with blank lines, except before the first clause in an enclosing body. Insert a blank line before `return`, `raise`, `break`, and similar statements unless they are the sole statement of the clause. The surrounding user-written code is the reference for ambiguous placement.

Use one test module per source module, grouping tests in classes by the tested type. Put reusable supporting data/helpers at class level, without unnecessary `ClassVar` annotations. Tests should describe the selected contract rather than preserve every abandoned implementation. Pyright uses basic checking, matching the project's intended strictness.

### D16. The owner binds its sides after construction

**Status: Agreed and implemented. Resolves O03's side-ownership question.**

`Side(*pieces)` initializes a roster without requiring an owner argument. Its `board` annotation declares the reference that the owning board will supply after constructing it.

`Board` creates its white and black sides, then assigns itself to both sides' `board` references before placement parsing. Both installed side identities and owner references therefore exist before contextual piece construction can use them. A standalone side can hold pieces; its role-based truth, opposing side, and forward direction require board binding.

- [x] The owning board binds its two sides after constructing them.
- [ ] Require an owner in the side constructor.
- [ ] Introduce descriptors or a generic owner-binding framework for this assignment.

This retains the indirect binding decision first applied to `Side.game`; D18 moves the owner to `Board` and replaces that backlink with `Side.board`. The separate king scan registers initial references as described in D09. Roster synchronization and pending king-reference maintenance are tracked in O01; validation remains O02.

### D17. A game indexes its sides by color

**Status: Superseded by the selected and implemented fusion in D18.**

The evaluated prototype used `Game.sides` to map each `Color` to its participating `Side`, with `white` and `black` as derived aliases. `Side.color` was an explicit construction value, and `Side.other` resolved the opposite color through the mapping.

That made participant selection explicit while pieces still carried separate color and board references. The subsequent fusion removed that routing step: a piece now refers directly to its actual side, and `Board` owns those sides. `Color`, `Game.sides`, and `Side.color` are no longer current APIs.

### D18. Board-owned sides carry affiliation and direction

**Status: Agreed and implemented. Resolves the fusion question in O12.**

Each `Board`, including a plain board, owns actual white and black `Side` objects. Pieces refer directly to a `Side`. Affiliation and movement orientation come from that side rather than a separate `Color` value. `Side.board` links the participant to its owner; `Piece.board` derives through that link instead of storing another owner reference.

`Side.__bool__` identifies its installed role: white is true and black is false, regardless of roster size. This supersedes the earlier `is_white` property. `Side.other` returns the opponent, and `Side.forward` supplies the appropriate compass vector. Pawn direction delegates to `Side.forward`. Captures compare side identity; notation and rank predicates use side truth. Set equality and membership remain unchanged.

- [x] Board-owned participants, with pieces referring directly to their actual side.
- [ ] Retain a separate `Color` value and the color-to-side mapping from D17.
- [ ] Restrict participant ownership and contextual piece construction to `Game`.

This deliberately replaces color-only piece construction and an occupancy-only board with no participants. Unplaced pieces still have no active square or automatic roster membership, but pieces constructed with a board's sides already have affiliation and board context. A foreign-side assignment guard was initially added, then explicitly deferred; no transfer or rebinding operation replaces it. `geometry.Color` and `Index.color` are removed; square-shade truth remains geometric parity.

`Game` is now an empty `Board` subclass reserved for later temporal state and game rules. This fusion adds no king-count or nonempty-roster validation. Later king-reference maintenance, castling rights, ghost lifecycle, and attack detection remain unimplemented.

## Open decisions

### O01. Which mutation surface maintains position consistency?

**Status: Board assignment selected and implemented for occupancy, location, and rosters; king-reference maintenance remains open. Related: D06–D09, D18.**

`Board.__setitem__` coordinates square occupancy, piece indices, and active roster membership. Construction uses that same assignment surface, so the initial rosters are already populated before the final scan that registers kings. The earlier `Game.__setitem__` prototype has moved into the shared board layer.

- [x] Use `Board.__setitem__` to coordinate outgoing and incoming pieces and their active membership.
- [ ] Restrict roster coordination to a `Game.__setitem__` override.
- [ ] Add side-local bookkeeping helpers if later king or rights handling needs them.

Giving a side further local bookkeeping remains a possible refinement, not a selected requirement. A helper must not initiate the same placement again or recurse into the board setter. Direct set mutation is not a position operation.

The setter handles ordinary placement, replacement, deletion, and self-assignment. Index normalization happens before roster mutation, preserving state when an index is rejected. Cross-board assignment checks are explicitly deferred, and no ownership transfer or rebinding is implemented. The remaining post-construction scan registers kings until their update seam is chosen. These behaviors have dedicated engine tests.

The remaining question is how king references follow later setup replacement or removal, and how complete moves coordinate multiple square writes. Coordinate edits must not accidentally consume historical castling rights as though a legal move had been played; O04/O08 need an explicit boundary. The pointwise setter does not replace a move executor.

### O02. When is the king invariant validated?

**Status: Invariant agreed; validation boundary open. Related: D09.**

- [ ] Validate each complete `Game` after construction and maintain the reference through controlled mutations.
- [ ] Provide a distinct completion/validation step for position editing.
- [ ] Require every individual game assignment to preserve the king-presence/reference invariant.

The first option is the current recommendation. An individual square write may be one intermediate step of construction or a move, so rejecting every temporary absence is likely to interfere with ordinary mutation. Missing and duplicate kings both need consideration at the completed-position boundary. An ordinary king move retains the same `Side.king` object; changing its position is different from replacing the king during setup editing.

Tests use empty or partial `Board` objects for occupancy and movement, and a complete position for the current `Game` inheritance check. `Game` still inherits the board's permissive construction until its validation boundary is implemented. Exactly one king is only one validity check; it does not establish full position legality.

### O04. How are castling rights represented and updated?

**Status: Curated eligible-rook subset accepted; final representation and mutation API open.**

The useful reference set is the rooks that retain castling rights, not a duplicate collection of every active rook. Presence on an original square and a default `moved = False` do not reconstruct imported history. Initialize imported eligibility from declared FEN rights; the standard initial game can grant both rights per side explicitly. A bare placement does not prove either right. Do not grant eligibility to a replacement or promoted rook merely because it reaches a corner.

- [ ] Use eligible-rook membership itself as the authoritative rights state.
- [ ] Store separate kingside/queenside rights flags and look up the relevant rook when needed.
- [ ] Store named optional eligible-rook references for the two wings.

The first option most directly follows the accepted subset idea. Avoid storing flags and membership as independently mutable copies of the same fact unless an actual need justifies it.

**Required distinction:** persistent rights and present legality are separate. Blocking pieces and attacks can temporarily prevent castling without destroying a right. Both rights exist in the initial position even though castling is blocked. A failed current legality test must therefore not permanently clear a right. King/eligible-rook movement, and loss of the eligible rook, remove eligibility in forward play; undo must restore the previous state. [FIDE, articles 3.8.2.1–2](https://handbook.fide.com/chapter/e012023)

A false rights flag can skip further checks. A true flag still requires position-dependent validation; reading a validation predicate should not consume the right. Recomputing or caching that temporary result is a separate, deferred performance choice. [FEN distinguishes rights from immediate feasibility](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm).

### O05. How does the single ghost interact with occupancy and captures?

**Status: One game-level reference agreed; representation open and deferred until the side/king/castling choices above are settled.**

- [x] One optional `Game.ghost` reference.
- [ ] Independently stored live ghost references on both sides.
- [ ] Store side ghosts and rotate a second authoritative game reference between them.

The slot is agreed but does not yet exist in code. Any side-level convenience view could be derived from it; such a property has not been required. The opportunity is limited to the opponent's immediate reply. [FIDE, articles 3.7.3.1–2](https://handbook.fide.com/chapter/e012023)

The physical representation is a different, still open decision:

- [ ] Keep the ghost outside occupancy as metadata describing the passed square and actual rushed pawn. This was the assistant's recommendation, not an accepted choice.
- [ ] Keep a ghost in the occupancy model, with explicit semantics distinguishing transparent/empty behavior from en passant capturability.

The second option must account for ordinary moves, sliding rays, blockers, ordinary captures, attacks, side membership, and placement export. Adding `is None or is Ghost` to one predicate alone does not resolve all those consumers. Conversely, separate metadata requires `EnPassant` to consult that metadata instead of inheriting ordinary occupied-target validation unchanged.

Execution must identify the actual pawn victim, which occupies a different square from the destination. The current `other` snapshot points to the manually placed ghost in the prototype, not automatically to that pawn. The fields or references connecting the two remain open.

Expiry, creation on a committed rush, restoration during undo, and initialization from full FEN are not implemented. The FEN target can be present even without an available capturing pawn; do not confuse serialization of that target with legal capture availability. [FEN, section 16.1.3.4](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm)

### O06. What represents an empty square?

**Status: Reopened; discuss together with O05 after the preceding ownership choices.**

The current implementation uses `None`. The earlier decision to keep it is being reconsidered explicitly; it should not be treated as permanent merely because current code/tests use it.

- [ ] Retain `None` as the representation of an ordinary empty square.
- [ ] Introduce an `Empty(Piece)` or another explicit empty-square value with a deliberate shared occupancy protocol.

An explicit empty object can make selected operations uniform, but it does not by itself make a ghost transparent to rays yet selectively capturable by a pawn. Missing occupancy, geometric attacks, and en passant eligibility still need distinct meanings. With actual side ownership now selected in D18, an empty-object alternative must explain whether it has a side, whether it enters a roster, and how it serializes. A shared empty singleton cannot carry a distinct position for every board slot.

The unplaced-piece convention `piece.index is None` in D06 is a separate question; changing empty board slots need not change it.

### O07. What query establishes attacks and king safety?

**Status: Required behavior identified; API and implementation open.**

Attacks cannot be defined as the opponent's fully legal destinations: pinned pieces still attack, and pawn forward moves differ from pawn diagonal attacks. Validating each side through the other's legal moves would also create a circular definition. [FIDE, articles 3.1.3 and 3.9](https://handbook.fide.com/chapter/e012023)

- [ ] A direct piece/side `attacks(square)` predicate or corresponding game query.
- [ ] A generated collection of attacked squares, independent of legal-move filtering.
- [ ] Cached attack information with explicit invalidation, only if later justified.

The current recommendation is the smallest direct query that serves king safety and castling, reusing geometry where appropriate. Evaluate safety against the position resulting from the complete candidate move, including special-move effects. Do not introduce attack-map caching just to select the initial API.

### O08. Where do execution, simulation, and history live?

**Status: Deferred design; required before complete king-safety filtering.**

We have selected mutable occupancy and compact move records, but not the execution/reversal API. It must preserve or restore occupancy, piece positions, roster membership, king references, relevant movement history, castling rights, the ghost, and turn state when those features exist.

- [ ] Move-owned execution/reversal coordinated with the game.
- [ ] Game-owned application/reversal of move records.
- [ ] A separate operation/undo record if a concrete need appears.

Do not treat `Board.__setitem__` alone as that API. Do not assume a destination-index hash identifies a complete executable choice or a game state. Game-position keys, transpositions, repetition, complete object-graph serialization, and search strategy are separate later decisions. Snapshot fields from D11 must not be silently changed into live history lookups.

### O09. Where do full FEN and validation belong?

**Status: Placement layering settled; remaining scope deferred.**

`Board` consumes/exports the placement field. The chosen `Game` layer is where the remaining game context will belong, but the complete notation object/API is not settled. Castling rights, active color, the en passant target, and counters cannot be reconstructed from occupancy alone.

- [ ] Complete `notation.game` to parse/format the remaining fields and wire it to `Game`.
- [ ] Use another small explicit full-FEN representation if the current placeholder proves unsuitable.

Rank widths, total dimensions, accepted symbols, malformed input behavior, and the relationship between setup validation and playable-game validation need deliberate coverage when implemented. Full FEN import cannot truthfully reconstruct every piece's complete movement history; use the fields that actually exist rather than inventing provenance.

### O10. When are special move choices and final notation attached?

**Status: Partial separation agreed in D12; the remaining boundary is deferred.**

Basic moves, captures, and rushes stay available to piece search. Castling will also require explicit behavior. Promotion/en passant enrichment and final check/disambiguation annotations still need to be placed deliberately.

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

### O03. How are game and side references bound?

**Status: Ownership resolved in D16/D18; identifier retained for history.**

`Board` installs and binds its two sides; `Side` takes no owner constructor argument. No extra binding machinery is needed. This works for a plain board as well as the currently empty `Game` subclass.

Pieces now store their actual `side`, and `board` is a read-only property derived from `side.board`. There is no separate stored piece color, board, or game reference. This supersedes the earlier color-only piece construction and game-only participant ownership boundaries.

### O12. Should participant ownership and color become one entity?

**Status: Fusion selected and implemented in D18; identifier retained for history.**

- [x] Let pieces refer directly to board-owned sides and derive allegiance and orientation from those participants.
- [ ] Retain a separate `Color` value and the game-specific participant mapping from D17.

Board parsing resolves symbol case to an actual side at piece creation. Plain boards now own participants too; unplaced pieces retain their affiliation and derived board context without joining an active roster until placement. `Side.forward` provides explicit direction. Side identity establishes allegiance, and side truth denotes white or black independently of roster size. Set equality and membership retain their ordinary meanings.

`geometry.Color` and `Index.color` are removed. An index's square-shade truth remains geometric parity, independent of either participant. Game-specific temporal state and the remaining king, castling, ghost, and attack decisions stay open in their existing entries.

## Current implementation gaps

These are observations, not authorization to fix unrelated code whenever this file is edited.

- King references are assigned during the initial `Board` king scan, but exactly-one-king validation is not implemented.
- `Board.__setitem__` synchronizes active side membership and piece indices. King references are still bound only during initialization; later replacement or removal does not maintain them.
- Cross-board assignment validation is explicitly deferred; no ownership transfer or side-rebinding operation is implemented.
- No castling-rights state, castling move, `Game.ghost` slot, ghost expiry, move executor, or king-safety query exists yet.
- En passant tests currently place `Ghost` in board occupancy manually. That is prototype coverage, not closure of O05/O06.

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
| Working discussion, 2026-10-21 | Plain-set Side, required king reference, curated castling eligibility, one Game ghost; ownership was subsequently settled in D18, while ghost occupancy remains open |
| Follow-up implementation, 2026-10-21 | D16 settles indirect side ownership binding and corrects plain-set constructor forwarding; the fusion later moves ownership from Game to Board |
| Mapping prototype, 2026-10-21 | D17 evaluates color-keyed participants and intrinsic side color, then is superseded by D18; key validation before roster mutation is retained |
| Side-ownership fusion, 2026-10-21 | D18 gives Board actual sides, binds pieces to Side, derives board/direction from affiliation, and removes Color and Index.color; the initial foreign-side guard is subsequently deferred, and Side truth now denotes its white/black role |
