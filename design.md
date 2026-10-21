# Design record

This is the working reference for Goochess design discussions: what we have chosen, why we chose it, what the code currently implements, and what still needs a decision. It records the model we are building together rather than prescribing the rest of the implementation.

Jump to [decisions](#decisions-and-retained-baseline), [open questions](#open-decisions), or [implementation gaps](#known-implementation-gaps-at-the-start-of-this-record).

## Reading and maintaining this record

- **Agreed** means an explicit design choice. It can still be awaiting implementation.
- **Baseline** describes a retained contract in the current framework, without declaring every implementation detail permanent.
- **Open** means no alternative has been selected. Recommendations are labelled as recommendations.
- **Deferred** means the subject has deliberately been left for later.
- A checked alternative means **selected**, not necessarily implemented. An unchecked alternative in a closed decision is historical; in an open decision it remains under consideration.
- When we change a decision, update its existing entry and retain a short explanation of the superseded choice. Keep the identifiers stable so later discussions can refer to them.
- An experimental edit, a passing test, or an assistant recommendation does not by itself settle a design question. Record disagreements between the intended model and the implementation explicitly.

The historical starting point is `develop` at `7fb69e20e4a0df819a4adc37039c785483d37a03`. Earlier code is a source of inspiration, not the specification for this framework. The initial record was reviewed on 2026-10-21 against `50f5c06` and the working changes to `Side` on the `side` branch. The mathematical framework already present at `develop` is retained as baseline context; this record does not reconstruct its earlier development.

## Responsibility map

| Component | Responsibility | References |
| --- | --- | --- |
| `array`, `index`, mathematical collections, `fraction` | Reusable mathematics without chess knowledge | [mathematics.py](src/goochess/mathematics.py), [mathematics tests](tests/test_mathematics.py) |
| `Index`, `Color`, `Compass` | Standard chess board geometry and directions | [geometry.py](src/goochess/geometry.py), [geometry tests](tests/test_geometry.py) |
| `rank`, `board`, `serial` | Placement notation and its decoded representations | [notation.py](src/goochess/notation.py), [notation tests](tests/test_notation.py) |
| `Piece` and its subclasses | Piece identity, location/context references, and movement patterns | [material.py](src/goochess/material.py), [material tests](tests/test_material.py) |
| `Move`, `Capt`, and related classes | Move targets, move records, validation predicates, and move notation | [algebra.py](src/goochess/algebra.py), [algebra tests](tests/test_algebra.py) |
| `Board` | Square occupancy and placement import/export | [engine.py](src/goochess/engine.py), [engine tests](tests/test_engine.py) |
| `Game` and `Side` | Game context and the two participating rosters; further state is being designed | [engine.py](src/goochess/engine.py) |

## Decisions and retained baseline

### D01. Standard chess, mutable positions, and explicit move records

**Status: Agreed direction; execution and search are not implemented.**

The current scope is standard chess. `Board` represents a position through mutable square occupancy. `Game` extends it with sides and game context, while a plain board remains usable independently. A move describes a transition around one moving piece and its destination, rather than requiring a newly constructed board for every candidate.

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

`Index.file` and `Index.rank` expose human-readable chess coordinates. Its textual form is the lowercase square name. `Color.WHITE = 1` and `Color.BLACK = -1` support direction reversal; color truth means white. An index's truth also means its square is white. Missing pieces or positions must therefore be tested with `is None`.

`Compass` holds direction arrays and the rank/file direction sets. These are reusable movement constants, not an enum that must contain every arithmetic result.

- [x] Direct FEN-order square encoding.
- [ ] Earlier file-major or transposed layouts.
- [x] Direction constants usable in ordinary array arithmetic.
- [ ] A finite vector enum required to absorb arbitrary operation results.

The coordinate encoding was settled in `169bf45`; the current `Index` name supersedes `Square`.

### D06. A piece has identity independently of its position

**Status: Agreed and implemented.**

Distinct piece instances remain distinct even when their type, color, and position-related attributes agree. Equality and hashing use object identity, allowing a side to contain multiple otherwise identical pawns, rooks, or promoted pieces.

`Piece(color)` and `Piece.fromnotation(symbol)` construct an unplaced piece. Its `index` is initially `None`; its `board` reference is assigned when it is placed. `Roster` resolves the canonical FEN symbols to piece classes, while `Officer` enumerates promotion choices.

Removing a piece clears its `index` while retaining its board context. An unplaced or removed piece produces no movement targets. Absence of a piece from the board is distinct from the representation of an empty board slot; the latter is being revisited in O06.

- [x] Color-only piece construction, followed by placement-time binding.
- [ ] Construct every piece with a side and derive all context from it.
- [ ] Require board and optional position arguments in the piece constructor.

This construction boundary was settled in `081a665`. Whether further game/side access should be derived or assigned belongs to O01 and O03.

### D07. Board assignment owns the basic occupancy binding

**Status: Agreed and implemented for pointwise assignment.**

`Board` is the occupancy source of truth. Its present backend is a 64-slot list of `Piece | None`. Assigning a piece through `Board.__setitem__` binds both its `board` and its concrete `Index`. Replacing a piece clears the outgoing piece's index. Deletion empties a slot without shrinking the board.

`Board.get` translates a slot to a piece symbol or `-`; `Board.set` translates a symbol and delegates to normal assignment. Placement construction uses those same surfaces. `Board.__repr__` returns the FEN placement field, not a full game FEN.

These operations are low-level occupancy changes, not complete legal moves. They do not currently relocate an incoming piece out of its previous slot, maintain side rosters after initialization, or update castling/history state. The next ownership boundary is O01. Guards against inherited list resizing/reordering methods have been discussed but are deferred.

### D08. A side is an active roster and a game participant

**Status: Agreed; partly implemented.**

Each side holds the distinct pieces active for its color. Captured pieces do not remain members of that active roster. A fixed list of original piece identities is unnecessary and fits custom positions poorly. Material difference can be reported without inventing a capture history for an imported position.

- [x] Plain `set[Piece]` as the side's container base.
- [ ] `mathematics.collection[Piece]` preserving `Side` as an operation result.
- [ ] A positional list encoding each piece's original identity.
- [ ] Use the captured-piece collection as the side's main roster.

A union, difference, or copy of a roster is an ordinary set of pieces; it is not another participating side. The side is identified by its role as `game.white` or `game.black`, with color and the opposing side derived from that role.

The plain-set change is present in the current working code. `Game` currently fills its two rosters after placement construction; mutation-time synchronization remains open. Switching bases also requires adapting the set initializer, tracked in the implementation gaps below.

### D09. Each valid game side has a dedicated king reference

**Status: Agreed target; binding and validation pending.**

The scope is standard chess, and each side of a valid playable `Game` must have exactly one king. `Side.king` refers to the same king object contained in its roster; its position remains `king.index`.

The current annotation does not assign or validate that reference. Choosing the update and validation surfaces is O01/O02. Lower-level `Board` construction can still represent partial positions; that need not weaken the intended valid-`Game` invariant.

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

`Board` uses the flat representation to enumerate squares and delegates formatting back through these notation objects. Symbol-to-piece conversion belongs to the material/board boundary, not to the rank codec. The current APIs intentionally avoid requiring callers to assemble a second collection of `from_fen`/`from_flat` factories.

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

## Open decisions

### O01. Which mutation surface maintains game-level consistency?

**Status: Open; next design discussion. Related: D06–D09.**

`Board.__setitem__` already handles square occupancy and piece location. We need a single clear responsibility for adding/removing active roster membership, binding the king reference, and coordinating game context.

- [ ] Override `Game.__setitem__` to coordinate the outgoing and incoming pieces, delegating basic occupancy binding to `Board`.
- [ ] Give `Side.add`/removal responsibility for side-local metadata, with the game coordinating occupancy separately.
- [ ] Perform these updates through an explicit position/move operation, keeping direct assignment lower-level.

The first two can collaborate, but should not both initiate the same placement or recurse through one another. **Current recommendation:** let `Game` coordinate board changes and let a side perform only local roster bookkeeping if a helper proves useful. This is a recommendation, not an agreed implementation.

Questions to settle include replacement, capture, promotion, setup edits, and clearing a source square before setting a destination. Updating only `Side.add` would leave removal and other inherited set mutations unresolved. Coordinate edits also must not accidentally consume historical castling rights as though a legal move had been played; O04/O08 need an explicit boundary.

### O02. When is the king invariant validated?

**Status: Invariant agreed; validation boundary open. Related: D09.**

- [ ] Validate each complete `Game` after construction and maintain the reference through controlled mutations.
- [ ] Provide a distinct completion/validation step for position editing.
- [ ] Require every individual game assignment to preserve the king-presence/reference invariant.

The first option is the current recommendation. An individual square write may be one intermediate step of construction or a move, so rejecting every temporary absence is likely to interfere with ordinary mutation. Missing and duplicate kings both need consideration at the completed-position boundary. An ordinary king move retains the same `Side.king` object; changing its position is different from replacing the king during setup editing.

Existing tests construct empty or partial `Game` objects. They document the prototype, not acceptance of kingless playable games. Once enforcement is implemented, use `Board` for occupancy-only tests and complete positions where game semantics are needed. Exactly one king is only one validity check; it does not establish full position legality.

### O03. How are game and side references bound?

**Status: Open. Related: O01.**

- [ ] Keep the explicit `Side(..., game = game)` constructor argument.
- [ ] Construct sides and assign their `game` reference when `Game` installs them as white/black, analogous to piece placement.
- [ ] Introduce a broader owner-binding surface if a concrete need appears.

Indirect binding is possible without a descriptor or other class machinery: the owning game can assign the reference. Both sides and their owner references must exist before parsing invokes any overridden game assignment that uses them. Current color/other properties also depend on the installed white/black identities.

Pieces presently store `board`, not separate `game` and `side` references. Whether those additional accessors should be derived or stored is unresolved. A plain `Board` is not necessarily a `Game`, so a piece's board reference alone does not universally establish a side.

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

An explicit empty object can make selected operations uniform, but it does not by itself make a ghost transparent to rays yet selectively capturable by a pawn. Missing occupancy, geometric attacks, and en passant eligibility still need distinct meanings. Also settle color/side ownership, whether empties enter rosters, and how empty values serialize before choosing this representation. A shared empty singleton cannot carry a distinct position for every board slot.

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

## Known implementation gaps at the start of this record

These are observations, not authorization to fix unrelated code whenever this file is edited.

- `Side` now subclasses built-in `set`, but still calls `super().__init__(*pieces)`. The built-in initializer takes one iterable: the intended forwarding is `super().__init__(pieces)`. Empty construction happens to work; nonempty construction does not follow the intended API.
- `Side.king` is only an annotation. No reference assignment or exactly-one-king validation exists yet.
- Side membership is assembled once in `Game.__init__`; subsequent board writes do not synchronize rosters.
- `Side.game` currently uses explicit constructor binding; whether to change this remains open in O03.
- No castling-rights state, castling move, `Game.ghost` slot, ghost expiry, move executor, or king-safety query exists yet.
- En passant tests currently place `Ghost` in board occupancy manually. That is prototype coverage, not closure of O05/O06.
- Existing empty/partial `Game` fixtures will need review when D09's invariant is enforced; occupancy-only `Board` fixtures remain useful.
- The README still contains older `Square`/`vector` names and coordinate/layout descriptions. It needs synchronization after the active design work; it is not authority over D05.

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
| Working discussion, 2026-10-21 | Plain-set Side, required king reference, curated castling eligibility, one Game ghost; ownership and occupancy choices remain open |
