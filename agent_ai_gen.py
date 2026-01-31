"""Modular dictionary agent

Provides a simple, importable `DictionaryAgent` class with JSON
persistence and a minimal CLI for interactive use.

Features:
- load/save JSON dictionary file
- lookup, add, remove, list words
- simple CLI with subcommands

This file is intentionally self-contained so it can be used as a
module or run as a script for quick demos.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Optional


class DictionaryAgent:
	"""A small modular dictionary agent using an in-memory dict.

	Methods are intentionally simple so the class can be imported and
	used in other programs or extended.
	"""

	def __init__(self, storage_path: Optional[str] = None) -> None:
		self._dict: Dict[str, str] = {}
		self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), "dictionary.json")

	def load(self) -> None:
		"""Load dictionary from JSON file at `self.storage_path`.

		If the file doesn't exist, starts with an empty dictionary.
		"""
		try:
			with open(self.storage_path, "r", encoding="utf-8") as f:
				data = json.load(f)
			if isinstance(data, dict):
				# Ensure all keys/values are strings
				self._dict = {str(k): str(v) for k, v in data.items()}
			else:
				self._dict = {}
		except FileNotFoundError:
			self._dict = {}

	def save(self) -> None:
		"""Save the current dictionary to `self.storage_path` as JSON.
		"""
		directory = os.path.dirname(self.storage_path)
		if directory and not os.path.exists(directory):
			os.makedirs(directory, exist_ok=True)
		with open(self.storage_path, "w", encoding="utf-8") as f:
			json.dump(self._dict, f, ensure_ascii=False, indent=2)

	def lookup(self, word: str) -> Optional[str]:
		"""Return the definition for `word` or None if missing."""
		return self._dict.get(word)

	def add(self, word: str, definition: str, overwrite: bool = False) -> bool:
		"""Add a `word` with `definition`.

		Returns True if added, False if already exists and overwrite is False.
		"""
		if word in self._dict and not overwrite:
			return False
		self._dict[word] = definition
		return True

	def remove(self, word: str) -> bool:
		"""Remove `word` from dictionary. Returns True if removed."""
		return self._dict.pop(word, None) is not None

	def list_words(self) -> Dict[str, str]:
		"""Return a shallow copy of the dictionary."""
		return dict(self._dict)


def build_parser() -> argparse.ArgumentParser:
	p = argparse.ArgumentParser(prog="dictionary-agent", description="Simple modular dictionary agent CLI")
	sub = p.add_subparsers(dest="cmd", required=False)

	sub.add_parser("list", help="List all words")

	lp = sub.add_parser("lookup", help="Lookup a word")
	lp.add_argument("word", help="Word to lookup")

	ap = sub.add_parser("add", help="Add a word")
	ap.add_argument("word", help="Word to add")
	ap.add_argument("definition", help="Definition for the word")
	ap.add_argument("--overwrite", action="store_true", help="Overwrite existing entry")

	rp = sub.add_parser("remove", help="Remove a word")
	rp.add_argument("word", help="Word to remove")

	sp = sub.add_parser("save", help="Save dictionary to file")
	sp.add_argument("--path", help="Path to save JSON file (overrides default)")

	lp2 = sub.add_parser("load", help="Load dictionary from file")
	lp2.add_argument("--path", help="Path to JSON file (overrides default)")

	return p


def run_agent(argv: Optional[list[str]] = None) -> int:
	"""Entry point for CLI. Returns exit code (0 success)."""
	parser = build_parser()
	args = parser.parse_args(argv)

	agent = DictionaryAgent()
	# Attempt to load existing dictionary silently
	agent.load()

	if not args.cmd:
		# Interactive prompt if no command provided
		print("Dictionary Agent (interactive). Type 'help' for commands, 'exit' to quit.")
		try:
			while True:
				raw = input("> ").strip()
				if not raw:
					continue
				if raw.lower() in {"exit", "quit"}:
					break
				if raw.lower() == "help":
					print("Commands: list, lookup <word>, add <word> <definition>, remove <word>, save, load, exit")
					continue
				parts = raw.split(maxsplit=2)
				cmd = parts[0].lower()
				if cmd == "list":
					for w, d in agent.list_words().items():
						print(f"{w}: {d}")
				elif cmd == "lookup" and len(parts) >= 2:
					res = agent.lookup(parts[1])
					if res is None:
						print("(not found)")
					else:
						print(res)
				elif cmd == "add" and len(parts) >= 3:
					added = agent.add(parts[1], parts[2])
					print("added" if added else "exists (use overwrite)")
				elif cmd == "remove" and len(parts) >= 2:
					removed = agent.remove(parts[1])
					print("removed" if removed else "not found")
				elif cmd == "save":
					agent.save()
					print(f"saved to {agent.storage_path}")
				elif cmd == "load":
					agent.load()
					print("loaded")
				else:
					print("unknown or malformed command; type 'help'")
		except (KeyboardInterrupt, EOFError):
			print()
		return 0

	# Non-interactive CLI commands
	cmd = args.cmd
	if cmd == "list":
		for w, d in agent.list_words().items():
			print(f"{w}: {d}")
		return 0

	if cmd == "lookup":
		res = agent.lookup(args.word)
		if res is None:
			print("(not found)")
			return 2
		print(res)
		return 0

	if cmd == "add":
		added = agent.add(args.word, args.definition, overwrite=args.overwrite)
		if not added:
			print("exists")
			return 3
		agent.save()
		print("added")
		return 0

	if cmd == "remove":
		removed = agent.remove(args.word)
		if not removed:
			print("not found")
			return 2
		agent.save()
		print("removed")
		return 0

	if cmd == "save":
		if args.path:
			agent.storage_path = args.path
		agent.save()
		print(f"saved to {agent.storage_path}")
		return 0

	if cmd == "load":
		if args.path:
			agent.storage_path = args.path
		agent.load()
		print(f"loaded from {agent.storage_path}")
		return 0

	parser.print_help()
	return 1


if __name__ == "__main__":
	raise SystemExit(run_agent())

