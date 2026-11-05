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

Usage and validation notes are added alongside the code.
