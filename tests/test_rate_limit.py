"""Tests for loop.is_rate_limited - rate-limit detection on failed cycles."""

import json
import unittest

from loop import is_rate_limited

# A stream-json transcript whose agent content mentions billing/quota words.
TRANSCRIPT = "\n".join(
    json.dumps(obj)
    for obj in [
        {"type": "assistant", "message": {"content": "Drafting the billing quota report (HTTP 429 section)."}},
        {"type": "user", "message": {"content": "tool result: usage limit table written"}},
    ]
)


class IsRateLimitedTest(unittest.TestCase):
    def test_clean_exit_never_rate_limited(self):
        # A validation failure or no-op cycle: CLI succeeded, agents talked about billing.
        result = {"type": "result", "subtype": "success", "is_error": False, "result": "Updated billing docs."}
        raw = TRANSCRIPT + "\n" + json.dumps(result)
        self.assertFalse(is_rate_limited(raw, 0, result))

    def test_transcript_words_ignored_on_unrelated_crash(self):
        result = {"type": "result", "subtype": "error_during_execution", "is_error": True, "result": "Tool crashed"}
        raw = TRANSCRIPT + "\n" + json.dumps(result)
        self.assertFalse(is_rate_limited(raw, 1, result))

    def test_error_result_with_rate_limit_text(self):
        result = {"type": "result", "subtype": "success", "is_error": True, "result": "API Error: 429 rate limit exceeded"}
        self.assertTrue(is_rate_limited(json.dumps(result), 0, result))

    def test_usage_limit_error_result(self):
        result = {"type": "result", "is_error": True, "result": "Claude AI usage limit reached"}
        raw = TRANSCRIPT + "\n" + json.dumps(result)
        self.assertTrue(is_rate_limited(raw, 1, result))

    def test_plain_stderr_on_nonzero_exit(self):
        raw = TRANSCRIPT + "\nError: Too Many Requests"
        self.assertTrue(is_rate_limited(raw, 1, {}))

    def test_plain_unrelated_stderr(self):
        self.assertFalse(is_rate_limited("Error: invalid flag", 1, {}))

    def test_empty_output(self):
        self.assertFalse(is_rate_limited("", 1, {}))


if __name__ == "__main__":
    unittest.main()
