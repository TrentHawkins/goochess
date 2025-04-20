# Graphical Object-Oriented Chess

Start the game with:

```sh
python -m src.main
```

## How to play

Regular moves:

- Click on a piece of your side (it is your turn to play), to select it and see all valid _squares_ for the piece.
  - _green_ marks all possible squares the piece can go to.
  - _red_ marks all the possible captures for that piece.
  - _blue_ marks special moves for the piece (either pawns or kings have them).
- Click on any of the valid squares for the piece to _move_ the piece.
- Click anywhere else to _cancel_ the selection.
- This works for captures too.
- Squares marked account for _king safety_. This means that when checkmated, none of your pieces will have any valid squares.

Special moves:

- When _enpassant_ is active for a selected pawn, you will see it as a target for that pawn.
- If castling on a side is allowed, it can be invoked as a _king move_ (click on the king to reveal the possibility)>
- Both _pawn rush_ (option for double step initial move for pawns) and _king castling_ are marked as special moves.

When bringing a pawn on the final rank of your side, it triggers _pawn promotion_:

- Click on a pawn ready to promote.
- Click one of its valid squares as usual. The pawn will not move. Instead it will switch to a _ghostly_ queen.
- Click on your pawn (now a ghostly queen) to cycle through other officer piece types (rook, bishop, knight).
- When you are satisfied with your choice, _reclick_ on the target square to confirm the move (and promotion).
- Click anywhere else to cancel the promotion sequence and start again.

## `TODO`

- Game states are stored in a `FEN`-like format, but miss storing history for full game reproducibility.
- Game crucially misses handling of game terminating conditions:
  - checmkate
  - stalemate
  - resignation
  - proposed draw (with option to ignore/cancel)
  - 3-fold move repetition draw
  - 50-move draw
- Game lacks a menu (shown at game start and invokable with the `ESC` key) where player(s) can:
  - start a new game from scratch
  - load a previously saved game
  - save a current ongoing game
  - exit the game
- Game is graphically robust, but could use piece movement animations.
