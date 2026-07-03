from __future__ import annotations


from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import pygame

import src.algebra
import src.material

from app.layout import LayoutSpec


type RGB = tuple[int, int, int]


@dataclass(frozen = True, slots = True)
class BoardPalette:

	background: RGB = (0x44, 0x33, 0x22)
	flash     : RGB = (0xCC, 0xCC, 0xCC)
	label     : RGB = (0xCC, 0xCC, 0xCC)
	move      : RGB = (0x22, 0x33, 0x11)
	capture   : RGB = (0x66, 0x00, 0x00)
	special   : RGB = (0x11, 0x22, 0x33)
	white     : RGB = (0xAA, 0x99, 0x88)
	black     : RGB = (0x77, 0x66, 0x55)


@dataclass(frozen = True, slots = True)
class PieceEffects:

	high    : RGB = (0xFF, 0xFF, 0xFF)
	selected: RGB = (0x33, 0x33, 0x33)

	hidden_alpha: int = 0
	ghost_alpha: int = 170
	promotion_alpha: int = 170


@dataclass(frozen = True, slots = True)
class PieceKey:

	color: src.algebra.Color
	piece: type[src.material.Piece]


@dataclass(frozen = True, slots = True)
class PieceStyle:

	asset: Path
	offset: tuple[int, int] = (0, 0)
	capture_width: int = 1


@dataclass(frozen = True, slots = True)
class BoardThemeSpec:

	name: str
	palette: BoardPalette
	background: Path
	square: Path
	frame: BoardFrameSpec | None = None


@dataclass(frozen = True, slots = True)
class BoardFrameSpec:

	corner: Path
	file: Path
	rank: Path
	depth_divisor: int = 6


@dataclass(frozen = True, slots = True)
class PieceThemeSpec:

	name: str
	effects: PieceEffects
	styles: Mapping[PieceKey, PieceStyle]


def _image(theme_kind: str, theme_name: str, path: Path, label: str, *, alpha: bool = False) -> pygame.Surface:
	if not path.is_file():
		raise FileNotFoundError(f"{theme_kind} theme {theme_name!r} asset {label!r} not found: {path}")

	loaded = pygame.image.load(path)
	return loaded.convert_alpha() if alpha else loaded.convert()


@dataclass(frozen = True, slots = True)
class BoardTheme:

	spec: BoardThemeSpec
	background: pygame.Surface
	square: pygame.Surface
	font: pygame.font.Font
	frame: BoardFrame | None = None


	@classmethod
	def load(cls, spec: BoardThemeSpec, layout: LayoutSpec) -> BoardTheme:
		background = pygame.transform.smoothscale(
			_image("Board", spec.name, spec.background, "background"),
			layout.window,
		)
		square = pygame.transform.smoothscale(
			_image("Board", spec.name, spec.square, "square"),
			layout.square_size,
		)
		font = pygame.font.SysFont(None, layout.square_size[1] // 4,
			bold = True,
		)
		frame = None

		if spec.frame is not None:
			square_w, square_h = layout.square_size
			corner_size = (
				square_w // spec.frame.depth_divisor,
				square_h // spec.frame.depth_divisor,
			)

			frame = BoardFrame(
				corner = pygame.transform.smoothscale(_image("Board", spec.name, spec.frame.corner, "frame corner"), corner_size),

				file   = pygame.transform.smoothscale(_image("Board", spec.name, spec.frame.file  , "frame file"), (square_w, corner_size[1])),
				rank   = pygame.transform.smoothscale(_image("Board", spec.name, spec.frame.rank  , "frame rank"), (corner_size[0], square_h)),
			)

		return cls(spec, background, square, font, frame)

	@property
	def palette(self) -> BoardPalette:
		return self.spec.palette


@dataclass(frozen = True, slots = True)
class BoardFrame:

	corner: pygame.Surface

	file: pygame.Surface
	rank: pygame.Surface


@dataclass(frozen = True, slots = True)
class PieceTheme:

	spec: PieceThemeSpec
	surfaces: Mapping[PieceKey, pygame.Surface]


	@classmethod
	def load(cls, spec: PieceThemeSpec, layout: LayoutSpec) -> PieceTheme:
		surfaces = {
			key: pygame.transform.smoothscale(
				_image(
					"Piece",
					spec.name,
					style.asset,
					f"{key.color.name.lower()} {key.piece.__name__.lower()}",
					alpha = True,
				),
				layout.piece_size,
			)
			for key, style in spec.styles.items()
		}

		return cls(spec, MappingProxyType(surfaces))

	@property
	def effects(self) -> PieceEffects:
		return self.spec.effects

	def piece_key(self, piece: src.material.Piece) -> PieceKey:
		return PieceKey(piece.color, type(piece))

	def style(self, piece: src.material.Piece) -> PieceStyle:
		return self.spec.styles[self.piece_key(piece)]

	def surface(self, piece: src.material.Piece) -> pygame.Surface:
		return self.surfaces[self.piece_key(piece)]

	def officer_surface(self, officer: src.material.Officer, color: src.algebra.Color) -> pygame.Surface:
		key = PieceKey(color, officer.value)
		surface = self.surfaces[key].copy()
		surface.fill((*self.effects.high, self.effects.promotion_alpha),
			special_flags = pygame.BLEND_RGBA_MULT,
		)

		return surface


@dataclass(frozen = True, slots = True)
class Appearance:

	board: BoardTheme
	pieces: PieceTheme


def _default_piece_styles() -> Mapping[PieceKey, PieceStyle]:
	styles: dict[PieceKey, PieceStyle] = {}
	asset_root = Path("graphics/piece")

	for color, folder in (
		(src.algebra.Color.BLACK, "black"),
		(src.algebra.Color.WHITE, "white"),
	):
		asymmetric = "r" if color else ""
		paths = {
			src.material.Pawn  : "pawn.png",
			src.material.Ghost : "pawn.png",
			src.material.Rook  : "rook.png",
			src.material.Knight: f"knight{asymmetric}.png",
			src.material.Bishop: f"bishop{asymmetric}.png",
			src.material.Queen : "queen.png",
			src.material.King  : "king.png",
		}
		details = {
			src.material.Pawn  : (( 0, -4),  2),
			src.material.Ghost : (( 0, -4),  2),
			src.material.Rook  : ((-1,  0),  6),
			src.material.Knight: (( 0,  0),  6),
			src.material.Bishop: ((-1,  0),  7),
			src.material.Queen : ((-1,  1), 10),
			src.material.King  : (( 0,  1), 10),
		}

		for piece, filename in paths.items():
			offset, capture_width = details[piece]
			styles[PieceKey(color, piece)] = PieceStyle(
				asset = asset_root / folder / filename,
				offset = offset,
				capture_width = capture_width,
			)

	return MappingProxyType(styles)


WOOD_BOARD = BoardThemeSpec(
	name = "wood",
	palette = BoardPalette(),
	background = Path("graphics/board/oak-wood.jpg"),
	square = Path("graphics/bevel/square.png"),
)

BEVEL_BOARD = BoardThemeSpec(
	name = "bevel",
	palette = BoardPalette(
		background = (0xDD, 0xCC, 0xBB),
		flash = (0x33, 0x33, 0x33),
		label = (0x33, 0x33, 0x33),
	),
	background = Path("graphics/board/oak-wood.jpg"),
	square = Path("graphics/bevel/square.png"),
	frame = BoardFrameSpec(
		corner = Path("graphics/bevel/corner.png"),
		file = Path("graphics/bevel/file.png"),
		rank = Path("graphics/bevel/rank.png"),
	),
)

DEFAULT_PIECES = PieceThemeSpec(
	name = "default",
	effects = PieceEffects(),
	styles = _default_piece_styles(),
)

DEFAULT_BOARD_THEME = BEVEL_BOARD.name
DEFAULT_PIECE_THEME = DEFAULT_PIECES.name

BOARD_THEMES: Mapping[str, BoardThemeSpec] = MappingProxyType({
	WOOD_BOARD.name: WOOD_BOARD,
	BEVEL_BOARD.name: BEVEL_BOARD,
})
PIECE_THEMES: Mapping[str, PieceThemeSpec] = MappingProxyType({
	DEFAULT_PIECES.name: DEFAULT_PIECES,
})


def board_theme_spec(name: str = DEFAULT_BOARD_THEME) -> BoardThemeSpec:
	try:
		return BOARD_THEMES[name]

	except KeyError as error:
		available = ", ".join(sorted(BOARD_THEMES))

		raise ValueError(f"Unknown board theme {name!r}; available board themes: {available}") from error


def piece_theme_spec(name: str = DEFAULT_PIECE_THEME) -> PieceThemeSpec:
	try:
		return PIECE_THEMES[name]

	except KeyError as error:
		available = ", ".join(sorted(PIECE_THEMES))

		raise ValueError(f"Unknown piece theme {name!r}; available piece themes: {available}") from error


def load_board_theme(name: str, layout: LayoutSpec) -> BoardTheme:
	return BoardTheme.load(board_theme_spec(name), layout)


def load_piece_theme(name: str, layout: LayoutSpec) -> PieceTheme:
	return PieceTheme.load(piece_theme_spec(name), layout)


def load_appearance(
	layout: LayoutSpec,
	board: str = DEFAULT_BOARD_THEME,
	pieces: str = DEFAULT_PIECE_THEME,
) -> Appearance:
	return Appearance(
		board  = load_board_theme(board , layout),
		pieces = load_piece_theme(pieces, layout),
	)
