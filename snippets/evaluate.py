"""Answer-in-snippet rate: query-biased window vs. the first N words of the document."""
import json
import sys
from pathlib import Path

from .index import Index
from .snippet import DEFAULT_WINDOW, best_snippet
from .tokenize import query_terms, tokenize

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def contains_answer(snippet_text: str, answer: str) -> bool:
    return answer.lower() in snippet_text.lower()


def lead_text(text: str, window: int) -> str:
    tokens = tokenize(text)[:window]
    return text[tokens[0].start:tokens[-1].end] if tokens else ""


def evaluate(corpus: dict[str, str], cases: list[dict], window: int) -> dict[str, float]:
    index = Index(corpus)
    top1 = biased = lead = 0
    for case in cases:
        terms = query_terms(case["query"])
        hits = index.search(terms, k=1)
        if not hits or hits[0][0] != case["doc"]:
            continue
        top1 += 1
        text = corpus[case["doc"]]
        snip = best_snippet(text, terms, index.idf, window)
        biased += contains_answer(snip.text, case["answer"])
        lead += contains_answer(lead_text(text, window), case["answer"])
    n = len(cases)
    return {"queries": n, "top1": top1 / n, "biased": biased / n, "lead": lead / n}


def main() -> int:
    corpus = json.loads((FIXTURES / "corpus.json").read_text())
    cases = json.loads((FIXTURES / "queries.json").read_text())
    print(f"fixture corpus: {len(corpus)} docs, {len(cases)} queries")
    print("window  top1   biased  lead")
    for window in (12, DEFAULT_WINDOW, 40):
        r = evaluate(corpus, cases, window)
        print(f"{window:>6}  {r['top1']:.3f}  {r['biased']:.3f}   {r['lead']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
