"""Search a directory of text files and print highlighted snippets."""
import argparse
import sys
from pathlib import Path

from .index import Index
from .snippet import DEFAULT_WINDOW, best_snippet, highlight
from .tokenize import query_terms


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="snippets", description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("query")
    parser.add_argument("-k", type=int, default=3, help="number of results")
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW, help="snippet length in words")
    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"not a directory: {args.directory}", file=sys.stderr)
        return 2
    docs = {p.name: p.read_text(encoding="utf-8") for p in sorted(args.directory.glob("*.txt"))}
    if not docs:
        print(f"no .txt files in {args.directory}", file=sys.stderr)
        return 2

    terms = query_terms(args.query)
    index = Index(docs)
    hits = index.search(terms, args.k)
    if not hits:
        print("no results")
        return 1
    for doc_id, score in hits:
        snip = best_snippet(docs[doc_id], terms, index.idf, args.window)
        print(f"{doc_id}  score={score:.2f}  chars={snip.start}-{snip.end}")
        print(f"  {highlight(docs[doc_id], snip, terms)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
