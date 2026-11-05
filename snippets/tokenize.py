"""Word tokenizer that keeps character offsets so snippets can slice the source."""
import re
from typing import NamedTuple

TOKEN_RE = re.compile(r"[a-z0-9]+(?:['_-][a-z0-9]+)*", re.IGNORECASE)

STOPWORDS = frozenset(
    "a an and are as at be by for from how in is it of on or that the to was what when where which with".split()
)


class Token(NamedTuple):
    term: str
    start: int
    end: int


def tokenize(text: str) -> list[Token]:
    # re.IGNORECASE instead of text.lower(): lower() can change the string
    # length for a few scripts, which would shift every offset.
    return [
        Token(m.group().lower(), m.start(), m.end())
        for m in TOKEN_RE.finditer(text)
    ]


def query_terms(query: str) -> list[str]:
    seen: dict[str, None] = {}
    for tok in tokenize(query):
        if tok.term not in STOPWORDS:
            seen.setdefault(tok.term)
    return list(seen)
