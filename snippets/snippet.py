"""Pick the best window of a document for a query and highlight the matches."""
from typing import Callable, NamedTuple

from .tokenize import Token, tokenize

DEFAULT_WINDOW = 24
LEAD_TOKENS = 3
MARK_OPEN = "**"
MARK_CLOSE = "**"
ELLIPSIS = "..."


class Snippet(NamedTuple):
    text: str
    start: int
    end: int
    score: float
    matched: tuple[str, ...]


def best_snippet(
    text: str,
    terms: list[str],
    idf: Callable[[str], float],
    window: int = DEFAULT_WINDOW,
) -> Snippet:
    if window < 1:
        raise ValueError(f"window must be >= 1, got {window}")
    tokens = tokenize(text)
    if not tokens:
        return Snippet("", 0, 0, 0.0, ())
    wanted = set(terms)
    weights = {t: idf(t) for t in wanted}

    def covered(lo: int, hi: int) -> set[str]:
        return {tok.term for tok in tokens[lo:hi] if tok.term in wanted}

    size = min(window, len(tokens))
    best_lo, best_score = 0, -1.0
    for lo in range(len(tokens) - size + 1):
        score = sum(weights[t] for t in covered(lo, lo + size))
        # Strict > keeps the earliest window on ties, which reads most naturally.
        if score > best_score:
            best_lo, best_score = lo, score

    lo = _trim_lead(tokens, best_lo, size, wanted)
    hi = lo + size
    start, end = tokens[lo].start, tokens[hi - 1].end
    return Snippet(text[start:end], start, end, max(best_score, 0.0), tuple(sorted(covered(lo, hi))))


def _trim_lead(tokens: list[Token], lo: int, size: int, wanted: set[str]) -> int:
    """Start a few tokens before the first match instead of on arbitrary filler."""
    for i in range(lo, min(lo + size, len(tokens))):
        if tokens[i].term in wanted:
            # Never move left of lo, and the window only slides right, so
            # every token the scored window covered stays covered.
            new_lo = max(lo, i - LEAD_TOKENS)
            return min(new_lo, len(tokens) - size)
    return lo


def highlight(text: str, snippet: Snippet, terms: list[str]) -> str:
    wanted = set(terms)
    body = snippet.text
    out, cursor = [], 0
    for tok in tokenize(body):
        if tok.term not in wanted:
            continue
        out.append(body[cursor:tok.start])
        out.append(f"{MARK_OPEN}{body[tok.start:tok.end]}{MARK_CLOSE}")
        cursor = tok.end
    out.append(body[cursor:])
    rendered = "".join(out)
    prefix = ELLIPSIS if snippet.start > 0 else ""
    suffix = ELLIPSIS if snippet.end < len(text.rstrip()) else ""
    return f"{prefix}{rendered}{suffix}"
