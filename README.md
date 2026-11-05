# rag-bm25-snippet-highlight

Query-biased snippets for search results. Given a query and a retrieved
document, pick the window of text that covers the most query evidence and
mark the matching terms, instead of showing the first N words.

Pure standard-library Python, no model, no network.

## Idea

A result list is only useful if each hit shows *why* it matched. The snippet
picker tokenizes the document with character offsets, weights each query term
by IDF over the corpus, and slides a fixed-size word window to find the one
with the highest weighted coverage. Repeated terms count once, so a window with
three different query terms beats one that repeats a single term.

## Layout

- `snippets/` - tokenizer, BM25 index, snippet picker, CLI
- `fixtures/` - small markdown-style corpus and queries with expected answers
- `tests/` - unit tests

## Usage

```
python3 -m snippets <directory-of-.txt-files> "how long are snapshots kept" -k 2 --window 24
```

Matches are wrapped in `**`, and `...` marks text cut from either side. Exit
code is 0 with results, 1 with none, 2 for bad input.

## Check

`make validate` runs the unit tests and `python3 -m snippets.evaluate`, which
asks whether the answer string appears in the snippet for the top-ranked
document. Results on the bundled fixtures (6 runbook-style documents,
8 queries; fixture numbers, not a benchmark):

| window (words) | top-1 doc | query-biased | first N words |
| --- | --- | --- | --- |
| 12 | 1.000 | 0.625 | 0.000 |
| 24 | 1.000 | 1.000 | 0.125 |
| 40 | 1.000 | 1.000 | 0.125 |

The fixture documents bury the answer after an introduction, which is the case
snippets exist for. Real corpora with answers near the top will show a smaller gap.

## Caveats

- Windows are counted in words, not sentences, so a snippet can start mid-sentence.
- Matching is exact on lowercased tokens; there is no stemming.
