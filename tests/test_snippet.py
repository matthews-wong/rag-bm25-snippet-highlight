import unittest

from snippets.snippet import best_snippet, highlight
from snippets.tokenize import query_terms, tokenize

TEXT = "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau"


def flat(_term: str) -> float:
    return 1.0


class TokenizeTest(unittest.TestCase):
    def test_offsets_slice_the_source(self):
        text = "Hello, World-wide Web"
        for tok in tokenize(text):
            self.assertEqual(text[tok.start:tok.end].lower(), tok.term)

    def test_query_terms_drop_stopwords_and_duplicates(self):
        self.assertEqual(query_terms("the Web and web"), ["web"])


class SnippetTest(unittest.TestCase):
    def test_window_covers_both_terms_when_close(self):
        snip = best_snippet(TEXT, ["kappa", "mu"], flat, window=6)
        self.assertEqual(snip.matched, ("kappa", "mu"))

    def test_rare_term_wins_over_repeated_common_one(self):
        text = "common common common common filler filler filler filler filler filler rare end"
        weights = {"common": 0.1, "rare": 5.0}
        snip = best_snippet(text, ["common", "rare"], weights.__getitem__, window=4)
        self.assertIn("rare", snip.matched)

    def test_repeated_term_counts_once(self):
        text = "x x x x y a b c d e f g z"
        snip = best_snippet(text, ["x", "y", "z"], flat, window=5)
        self.assertEqual(snip.matched, ("x", "y"))

    def test_no_match_returns_first_window_with_zero_score(self):
        snip = best_snippet(TEXT, ["absent"], flat, window=4)
        self.assertEqual((snip.start, snip.score, snip.matched), (0, 0.0, ()))

    def test_empty_text(self):
        self.assertEqual(best_snippet("", ["a"], flat).text, "")

    def test_short_text_is_returned_whole(self):
        snip = best_snippet("one two", ["two"], flat, window=10)
        self.assertEqual(snip.text, "one two")

    def test_invalid_window_names_the_value(self):
        with self.assertRaisesRegex(ValueError, "got 0"):
            best_snippet(TEXT, ["a"], flat, window=0)

    def test_offsets_slice_the_source(self):
        snip = best_snippet(TEXT, ["rho"], flat, window=5)
        self.assertEqual(TEXT[snip.start:snip.end], snip.text)


class HighlightTest(unittest.TestCase):
    def test_marks_terms_and_adds_ellipses(self):
        snip = best_snippet(TEXT, ["kappa"], flat, window=4)
        out = highlight(TEXT, snip, ["kappa"])
        self.assertTrue(out.startswith("...") and out.endswith("..."))
        self.assertIn("**kappa**", out)

    def test_preserves_original_casing(self):
        text = "The Kappa value"
        snip = best_snippet(text, ["kappa"], flat, window=10)
        self.assertEqual(highlight(text, snip, ["kappa"]), "The **Kappa** value")


if __name__ == "__main__":
    unittest.main()
