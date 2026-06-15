"""Tests for src.consensus.read_signal — the Loop Signal parser."""

import unittest

from src.consensus import read_signal

# A realistic consensus body the orchestrator might emit, used to confirm the
# parser finds the signal among other content rather than only in isolation.
CONSENSUS_TEMPLATE = """## Last Updated
2026-06-15T00:00:00Z

## Current Phase
Finalize

## What We Did This Cycle
- copied approved draft to cv-final.md

## Key Decisions
- ship it

## Next Action
none

## Team State
done

## Open Questions
(none)
{signal}"""


def _doc(signal_line: str = "") -> str:
    return CONSENSUS_TEMPLATE.format(signal=signal_line)


class ReadSignalTest(unittest.TestCase):
    def test_absent_returns_none(self):
        self.assertIsNone(read_signal(_doc()))

    def test_done(self):
        self.assertEqual(read_signal(_doc("\n## Loop Signal: done")), "done")

    def test_stop(self):
        self.assertEqual(read_signal(_doc("\n## Loop Signal: stop")), "stop")

    def test_block_with_reason_preserves_reason(self):
        self.assertEqual(
            read_signal(_doc("\n## Loop Signal: block - candidate name required")),
            "block - candidate name required",
        )

    def test_unknown_token_returned_verbatim(self):
        # The parser stays dumb; token recognition is loop.py's job.
        self.assertEqual(read_signal(_doc("\n## Loop Signal: foo")), "foo")

    def test_empty_signal_returns_empty_string_not_none(self):
        # The bare-heading case that crashed the loop before the truthiness guard.
        self.assertEqual(read_signal(_doc("\n## Loop Signal:")), "")

    def test_whitespace_only_signal_returns_empty_string(self):
        self.assertEqual(read_signal(_doc("\n## Loop Signal:    ")), "")

    def test_value_is_stripped(self):
        self.assertEqual(read_signal(_doc("\n## Loop Signal:   done  ")), "done")

    def test_first_match_wins(self):
        body = _doc("\n## Loop Signal: stop\n## Loop Signal: done")
        self.assertEqual(read_signal(body), "stop")

    def test_signal_in_isolation(self):
        self.assertIsNone(read_signal("no headings here at all"))


if __name__ == "__main__":
    unittest.main()
