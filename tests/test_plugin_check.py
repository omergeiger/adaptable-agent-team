"""Tests for src.plugin_check - the agent/skill frontmatter preflight."""

import tempfile
import unittest
from pathlib import Path

from src.plugin_check import check_plugin

VALID_SKILL = "---\nname: rubric\ndescription: Score items. Apply when ranking.\n---\n\n# rubric\n"
VALID_AGENT = "---\nname: critic\ndescription: Reviews work.\nmodel: inherit\n---\n\nYou are the critic.\n"


class PluginCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "agents").mkdir()
        (self.root / "skills").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _skill(self, name, text):
        d = self.root / "skills" / name
        d.mkdir()
        (d / "SKILL.md").write_text(text)

    def _agent(self, name, text):
        (self.root / "agents" / f"{name}.md").write_text(text)

    def test_valid_plugin_passes(self):
        self._skill("rubric", VALID_SKILL)
        self._agent("critic", VALID_AGENT)
        self.assertEqual(check_plugin(self.root), [])

    def test_empty_plugin_passes(self):
        self.assertEqual(check_plugin(self.root), [])

    def test_skill_without_frontmatter_fails(self):
        self._skill("rubric", "# rubric - Scoring\n\nbody\n")
        problems = check_plugin(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("missing YAML frontmatter", problems[0])

    def test_unterminated_frontmatter_fails(self):
        self._skill("rubric", "---\nname: rubric\ndescription: x\n\n# rubric\n")
        self.assertIn("missing YAML frontmatter", check_plugin(self.root)[0])

    def test_invalid_yaml_reports_parse_error(self):
        self._skill("rubric", "---\nname: rubric\ndescription: Scoring: how items rank\n---\n")
        problems = check_plugin(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("invalid YAML (line 3)", problems[0])
        self.assertNotIn("missing", problems[0])

    def test_non_mapping_frontmatter_fails(self):
        self._skill("rubric", "---\n- just\n- a list\n---\n")
        self.assertIn("not a key/value mapping", check_plugin(self.root)[0])

    def test_missing_description_fails(self):
        self._skill("rubric", "---\nname: rubric\n---\n")
        self.assertIn("'description'", check_plugin(self.root)[0])

    def test_empty_name_fails(self):
        self._agent("critic", "---\nname: ''\ndescription: Reviews.\n---\n")
        self.assertIn("'name'", check_plugin(self.root)[0])

    def test_name_mismatch_fails(self):
        self._skill("rubric", VALID_SKILL.replace("name: rubric", "name: scoring"))
        self.assertIn("does not match 'rubric'", check_plugin(self.root)[0])

    def test_skill_dir_without_skill_md_fails(self):
        (self.root / "skills" / "orphan").mkdir()
        self.assertIn("missing SKILL.md", check_plugin(self.root)[0])

    def test_reports_every_bad_file(self):
        self._skill("a", "# a\n")
        self._skill("b", "# b\n")
        self._agent("critic", "You are the critic.\n")
        self.assertEqual(len(check_plugin(self.root)), 3)


if __name__ == "__main__":
    unittest.main()
