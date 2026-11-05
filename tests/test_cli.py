import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from snippets.cli import main


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class CliTest(unittest.TestCase):
    def test_prints_highlighted_hit(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.txt").write_text("the cache expires after ten minutes")
            Path(d, "b.txt").write_text("unrelated text about databases")
            code, out = run(d, "cache expires")
        self.assertEqual(code, 0)
        self.assertIn("a.txt", out)
        self.assertIn("**cache**", out)

    def test_no_match_exits_1(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.txt").write_text("hello")
            self.assertEqual(run(d, "zzz")[0], 1)

    def test_missing_directory_exits_2(self):
        self.assertEqual(run("/nonexistent-dir", "x")[0], 2)


if __name__ == "__main__":
    unittest.main()
