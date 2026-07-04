from __future__ import annotations


from dataclasses import dataclass, field
from math import cos, pi

import src.algebra
import src.material
import src.rules


@dataclass(frozen = True, slots = True)
class AnimationSpec:

	duration: float = 1 / 4  # seconds


	def __post_init__(self) -> None:
		if self.duration <= 0:
			raise ValueError("Animation duration must be positive")

	def ease(self, elapsed: float) -> float:
		phase = min(max(elapsed / self.duration, 0.0), 1.0)
		return (1.0 - cos(pi * phase)) / 2.0


@dataclass(frozen = True, slots = True)
class PieceMotion:

	piece: src.material.Piece
	source: src.algebra.Square
	target: src.algebra.Square


@dataclass(slots = True)
class MoveAnimation:

	rule: src.rules.Move
	motions: tuple[PieceMotion, ...]
	spec: AnimationSpec
	elapsed: float = 0.0


	@classmethod
	def from_rule(cls, rule: src.rules.Move, spec: AnimationSpec) -> MoveAnimation:
		motions = [PieceMotion(rule.piece, rule.source, rule.target)]

		if isinstance(rule, src.rules.Cast):
			rook = rule.rook
			assert rook is not None

			direction = src.algebra.Vector.W if rule.target.file > rule.source.file else src.algebra.Vector.E
			motions.append(PieceMotion(rook, rook.square, rule.target + direction))

		return cls(rule, tuple(motions), spec)

	@property
	def progress(self) -> float:
		return self.spec.ease(self.elapsed)

	@property
	def finished(self) -> bool:
		return self.elapsed >= self.spec.duration

	def advance(self, seconds: float) -> bool:
		if seconds < 0:
			raise ValueError("Animation time cannot move backwards")

		self.elapsed = min(self.elapsed + seconds, self.spec.duration)
		return self.finished


@dataclass(slots = True)
class MoveAnimator:

	spec: AnimationSpec = field(default_factory = AnimationSpec)
	current: MoveAnimation | None = None


	@property
	def active(self) -> bool:
		return self.current is not None

	def start(self, rule: src.rules.Move) -> MoveAnimation:
		if self.current is not None:
			raise RuntimeError("Cannot start a move while another move is animating")

		self.current = MoveAnimation.from_rule(rule, self.spec)
		return self.current

	def advance(self, seconds: float) -> src.rules.Move | None:
		if self.current is None or not self.current.advance(seconds):
			return None

		rule = self.current.rule
		self.current = None
		return rule
