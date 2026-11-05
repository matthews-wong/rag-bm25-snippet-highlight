import json
import unittest

from snippets.evaluate import FIXTURES, evaluate

CORPUS = json.loads((FIXTURES / "corpus.json").read_text())
CASES = json.loads((FIXTURES / "queries.json").read_text())


class EvaluateTest(unittest.TestCase):
    def test_biased_window_beats_leading_words(self):
        result = evaluate(CORPUS, CASES, window=24)
        self.assertGreater(result["biased"], result["lead"])

    def test_every_answer_is_in_its_document(self):
        for case in CASES:
            self.assertIn(case["answer"].lower(), CORPUS[case["doc"]].lower(), case["query"])


if __name__ == "__main__":
    unittest.main()
