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
class Palette:

	high: RGB = (0xFF, 0xFF, 0xFF)
	bright: RGB = (0x33, 0x33, 0x33)
	dark: RGB = (0x44, 0x33, 0x22)
	flash: RGB = (0xCC, 0xCC, 0xCC)
	label: RGB = (0xCC, 0xCC, 0xCC)
	red: RGB = (0x66, 0x00, 0x00)
	green: RGB = (0x22, 0x33, 0x11)
	gold: RGB = (0x33, 0x22, 0x11)
	blue: RGB = (0x11, 0x22, 0x33)
	white: RGB = (0xAA, 0x99, 0x88)
	empty: RGB = (0xDD, 0xCC, 0xBB)
	black: RGB = (0x77, 0x66, 0x55)


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
class ThemeSpec:

	name: str
	layout: LayoutSpec
	palette: Palette
	background: Path
	square: Path
	pieces: Mapping[PieceKey, PieceStyle]


@dataclass(frozen = True, slots = True)
class Theme:

	spec: ThemeSpec
	background: pygame.Surface
	square: pygame.Surface
	pieces: Mapping[PieceKey, pygame.Surface]
	font: pygame.font.Font


	@classmethod
	def load(cls, spec: ThemeSpec) -> Theme:
		def image(path: Path, label: str, *, alpha: bool = False) -> pygame.Surface:
			if not path.is_file():
				raise FileNotFoundError(f"Theme {spec.name!r} asset {label!r} not found: {path}")

			loaded = pygame.image.load(path)
			return loaded.convert_alpha() if alpha else loaded.convert()

		background = pygame.transform.smoothscale(
			image(spec.background, "background"),
			spec.layout.window,
		)
		square = pygame.transform.smoothscale(
			image(spec.square, "square"),
			spec.layout.square_size,
		)
		pieces = {
			key: pygame.transform.smoothscale(
				image(style.asset, f"{key.color.name.lower()} {key.piece.__name__.lower()}", alpha = True),
				spec.layout.piece_size,
			)
			for key, style in spec.pieces.items()
		}
		font = pygame.font.SysFont(None, spec.layout.square_size[1] // 4,
			bold = True,
		)

		return cls(spec, background, square, MappingProxyType(pieces), font)

	@property
	def layout(self) -> LayoutSpec:
		return self.spec.layout

	@property
	def palette(self) -> Palette:
		return self.spec.palette

	def piece_key(self, piece: src.material.Piece) -> PieceKey:
		return PieceKey(piece.color, type(piece))

	def piece_style(self, piece: src.material.Piece) -> PieceStyle:
		return self.spec.pieces[self.piece_key(piece)]

	def piece_surface(self, piece: src.material.Piece) -> pygame.Surface:
		return self.pieces[self.piece_key(piece)]

	def officer_surface(self, officer: src.material.Officer, color: src.algebra.Color) -> pygame.Surface:
		key = PieceKey(color, officer.value)
		surface = self.pieces[key].copy()
		surface.fill((*self.palette.high, 170),
			special_flags = pygame.BLEND_RGBA_MULT,
		)

		return surface


def _wood_piece_styles() -> Mapping[PieceKey, PieceStyle]:
	styles: dict[PieceKey, PieceStyle] = {}
	asset_root = Path("graphics/piece")

	for color, folder in (
		(src.algebra.Color.BLACK, "black"),
		(src.algebra.Color.WHITE, "white"),
	):
		asymmetric = "r" if color else ""
		paths = {
			src.material.Pawn  : f"pawn.png",
			src.material.Ghost : f"pawn.png",
			src.material.Rook  : f"rook.png",
			src.material.Knight: f"knight{asymmetric}.png",
			src.material.Bishop: f"bishop{asymmetric}.png",
			src.material.Queen : f"queen.png",
			src.material.King  : f"king.png",
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


WOOD = ThemeSpec(
	name = "wood",
	layout = LayoutSpec(),
	palette = Palette(),
	background = Path("graphics/board/oak-wood.jpg"),
	square = Path("graphics/bevel/square.png"),
	pieces = _wood_piece_styles(),
)

DEFAULT_THEME = WOOD.name
THEMES: Mapping[str, ThemeSpec] = MappingProxyType({
	WOOD.name: WOOD,
})


def theme_spec(name: str = DEFAULT_THEME) -> ThemeSpec:
	try:
		return THEMES[name]
	except KeyError as error:
		available = ", ".join(sorted(THEMES))
		raise ValueError(f"Unknown theme {name!r}; available themes: {available}") from error


def load_theme(name: str = DEFAULT_THEME) -> Theme:
	return Theme.load(theme_spec(name))
