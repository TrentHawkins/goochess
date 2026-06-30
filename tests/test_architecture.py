from __future__ import annotations


import ast
from pathlib import Path


def test_core_does_not_import_pygame_or_app():
	for path in Path("src").glob("*.py"):
		tree = ast.parse(path.read_text(), filename = str(path))

		for node in ast.walk(tree):
			if isinstance(node, ast.Import):
				imports = {alias.name.split(".", 1)[0] for alias in node.names}
			elif isinstance(node, ast.ImportFrom) and node.module is not None:
				imports = {node.module.split(".", 1)[0]}
			else:
				continue

			assert imports.isdisjoint({"pygame", "app"}), f"{path} imports {imports & {'pygame', 'app'}}"


def test_core_imports_when_pygame_is_unavailable(monkeypatch):
	import builtins
	import importlib
	import sys

	real_import = builtins.__import__

	def without_pygame(name, *args, **kwargs):
		if name == "pygame" or name.startswith("pygame."):
			raise ModuleNotFoundError("pygame deliberately unavailable")

		return real_import(name, *args, **kwargs)

	for name in tuple(sys.modules):
		if name == "src" or name.startswith("src."):
			del sys.modules[name]

	monkeypatch.setattr(builtins, "__import__", without_pygame)

	engine = importlib.import_module("src.engine")
	game = engine.Game.from_forsyth_edwards()

	assert len(game) == 64
