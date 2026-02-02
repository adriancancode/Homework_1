"""Modular dictionary agent with a built-in dictionary.

This single-file module provides a `DictionaryAgent` class that can be used
programmatically, and a small command-line interface for simple lookups and
edits. The built-in dictionary is contained entirely within this file so the
module is self-contained.

Usage examples:
  python agentv3.py define --word example
  python agentv3.py suggest --query examp
  python agentv3.py add --word foobar --definition "A placeholder word"

The class is intentionally small and modular so it can be imported and used
from other code in the workspace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import sys
from typing import Dict, List, Optional
import difflib


# A small built-in dictionary. Extend or modify as needed.
BUILT_IN_DICT: Dict[str, str] = {
	"algorithm": "A step-by-step procedure for calculations or problem-solving.",
	"binary": "A system using two states often represented as 0 and 1.",
	"cache": "A hardware or software component that stores data so future requests for that data can be served faster.",
	"dictionary": "A data structure that maps keys to values; also a reference book of words and meanings.",
	"example": "A representative form or pattern used to illustrate a rule.",
	"function": "A named section of a program that performs a specific task.",
}


@dataclass
class DictionaryAgent:
	"""A compact, modular dictionary agent.

	- Uses an internal dictionary (can be seeded with `BUILT_IN_DICT`).
	- Supports lookup, add, remove, list, and suggestion operations.
	"""

	data: Dict[str, str] = field(default_factory=lambda: dict(BUILT_IN_DICT))

	def define(self, word: str, case_sensitive: bool = False) -> Optional[str]:
		key = word if case_sensitive else word.lower()
		# Try exact match
		if case_sensitive:
			return self.data.get(key)
		# Non-case-sensitive: try lower-cased keys first
		for k, v in self.data.items():
			if k.lower() == key:
				return v
		return None

	def add(self, word: str, definition: str, overwrite: bool = False) -> bool:
		if word in self.data and not overwrite:
			return False
		self.data[word] = definition
		return True

	def remove(self, word: str) -> bool:
		if word in self.data:
			del self.data[word]
			return True
		# try case-insensitive removal
		for k in list(self.data.keys()):
			if k.lower() == word.lower():
				del self.data[k]
				return True
		return False

	def list(self, prefix: Optional[str] = None) -> List[str]:
		keys = sorted(self.data.keys())
		if prefix:
			return [k for k in keys if k.startswith(prefix)]
		return keys

	def suggest(self, query: str, max_results: int = 5) -> List[str]:
		# Use difflib to find close matches among keys
		keys = list(self.data.keys())
		return difflib.get_close_matches(query, keys, n=max_results, cutoff=0.4)


def _build_parser() -> argparse.ArgumentParser:
	p = argparse.ArgumentParser(description="DictionaryAgent CLI")
	sub = p.add_subparsers(dest="cmd", required=True)

	d_def = sub.add_parser("define", help="Define a word")
	d_def.add_argument("--word", required=True)

	d_sug = sub.add_parser("suggest", help="Suggest similar words")
	d_sug.add_argument("--query", required=True)
	d_sug.add_argument("--max", type=int, default=5)

	d_add = sub.add_parser("add", help="Add a word and definition")
	d_add.add_argument("--word", required=True)
	d_add.add_argument("--definition", required=True)
	d_add.add_argument("--overwrite", action="store_true")

	d_rm = sub.add_parser("remove", help="Remove a word")
	d_rm.add_argument("--word", required=True)

	d_list = sub.add_parser("list", help="List words")
	d_list.add_argument("--prefix", required=False)

	return p


def main(argv: Optional[List[str]] = None) -> int:
	argv = argv if argv is not None else sys.argv[1:]
	parser = _build_parser()
	args = parser.parse_args(argv)

	agent = DictionaryAgent()

	if args.cmd == "define":
		definition = agent.define(args.word)
		if definition:
			print(f"{args.word}: {definition}")
			return 0
		else:
			print(f"No definition found for '{args.word}'.")
			sugg = agent.suggest(args.word)
			if sugg:
				print("Did you mean:")
				for s in sugg:
					print(f"  - {s}")
			return 2

	if args.cmd == "suggest":
		for s in agent.suggest(args.query, max_results=args.max):
			print(s)
		return 0

	if args.cmd == "add":
		ok = agent.add(args.word, args.definition, overwrite=args.overwrite)
		if ok:
			print(f"Added '{args.word}'.")
			return 0
		else:
			print(f"Word '{args.word}' already exists. Use --overwrite to replace.")
			return 3

	if args.cmd == "remove":
		ok = agent.remove(args.word)
		if ok:
			print(f"Removed '{args.word}'.")
			return 0
		else:
			print(f"Word '{args.word}' not found.")
			return 4

	if args.cmd == "list":
		for k in agent.list(prefix=getattr(args, "prefix", None)):
			print(k)
		return 0

	return 1


if __name__ == "__main__":
	raise SystemExit(main())

