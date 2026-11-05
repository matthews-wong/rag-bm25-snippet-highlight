"""Minimal BM25 index; just enough to rank documents and expose IDF."""
import math
from collections import Counter

from .tokenize import tokenize

K1 = 1.5
B = 0.75


class Index:
    def __init__(self, docs: dict[str, str]) -> None:
        self.docs = docs
        self._tf = {
            doc_id: Counter(t.term for t in tokenize(text)) for doc_id, text in docs.items()
        }
        self._len = {doc_id: sum(tf.values()) for doc_id, tf in self._tf.items()}
        self._avg_len = sum(self._len.values()) / max(len(docs), 1)
        df: Counter[str] = Counter()
        for tf in self._tf.values():
            df.update(tf.keys())
        self._df = df

    def idf(self, term: str) -> float:
        n = len(self.docs)
        df = self._df.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def search(self, terms: list[str], k: int = 3) -> list[tuple[str, float]]:
        scores = []
        for doc_id, tf in self._tf.items():
            norm = 1 - B + B * self._len[doc_id] / (self._avg_len or 1)
            score = sum(
                self.idf(t) * tf[t] * (K1 + 1) / (tf[t] + K1 * norm) for t in terms if t in tf
            )
            if score > 0:
                scores.append((doc_id, score))
        # Tie-break on id so equal scores rank deterministically.
        scores.sort(key=lambda x: (-x[1], x[0]))
        return scores[:k]
