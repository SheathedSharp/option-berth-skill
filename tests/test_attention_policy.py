"""Static guardrails for the task attachment recipe; does not execute oberth."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]

class AttentionPolicy(unittest.TestCase):
    def test_enabled_runtime_task_does_not_require_an_extra_opt_in_phrase(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("read `oberth attn status --json` once", skill)
        self.assertIn("without waiting for the person", skill)
        self.assertNotIn("Do not arm a task-scoped attention session by default", skill)
    def test_attachment_is_bounded_owned_and_compatible(self):
        guide = (ROOT / "references/attention.md").read_text()
        for rule in ("scope.root", "quality.activity", "one-shot", "background tool handle", "same task and scope", "Do not share", "cancel/join", "Do not use broad", "no source code"):
            self.assertIn(rule, guide)
        self.assertIn("explicit choice before execution", guide)
        self.assertIn("No eligible event means no provider request", (ROOT / "SKILL.md").read_text())
    def test_event_wakeups_have_safe_ownership_calibration_and_fallback(self):
        guide = (ROOT / "references/attention.md").read_text()
        for rule in ("Do not start a second", "exact task worktree", "Resource samples", "low-frequency reconciliation", "offline fallback", "do not restart or start", "after model/cache return", "only the owned session/feed"):
            self.assertIn(rule, guide)
        cross = (ROOT / "references/cross-worktree.md").read_text()
        self.assertIn("Do not automatically restart", cross)
        self.assertIn("broader", cross)

    def test_disabled_configuration_is_not_changed_by_the_agent(self):
        guide = (ROOT / "references/attention.md").read_text()
        self.assertIn("do not enable, reconfigure, or probe credentials", guide)
        self.assertIn("Never copy credentials", guide)

if __name__ == "__main__":
    unittest.main()
