from pathlib import Path
import re
import unittest


SKILL = (
    Path(__file__).resolve().parents[1]
    / ".claude/skills/verify/SKILL.md"
)


class VerifySkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_discovery_description_uses_trigger_only_shape(self) -> None:
        frontmatter = self.text.split("---", 2)[1]
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        self.assertIsNotNone(description)
        self.assertTrue(description.group(1).startswith("Use when"))

    def test_claims_require_outcome_specific_observable_proof(self) -> None:
        self.assertIn("Claim map", self.text)
        self.assertIn("outcome-specific", self.text)
        self.assertIn("HTTP 200", self.text)
        self.assertIn("new path", self.text)

    def test_matt_testing_contract_is_preserved_without_duplication(self) -> None:
        self.assertIn("public seam", self.text)
        self.assertIn("independent source of truth", self.text)
        self.assertIn("vertical slice", self.text)
        self.assertIn("focused", self.text)
        self.assertIn("full suite", self.text)

    def test_runtime_ui_journey_is_observed_from_the_real_entry_point(self) -> None:
        self.assertIn("real entry point", self.text)
        self.assertIn("duplicate controls", self.text)
        self.assertIn("focus", self.text)
        self.assertIn("console", self.text)
        self.assertIn("network", self.text)
        self.assertIn("accessibility", self.text)

    def test_review_is_pinned_and_keeps_standards_separate_from_spec(self) -> None:
        self.assertIn("fixed point", self.text)
        self.assertIn("Standards", self.text)
        self.assertIn("Spec", self.text)

    def test_evidence_policy_uses_primary_sources_without_prevalence_claim(self) -> None:
        self.assertIn("https://playwright.dev/docs/test-use-options", self.text)
        self.assertIn("https://docs.github.com/", self.text)
        self.assertIn('trace: "retain-on-failure"', self.text)
        self.assertIn('screenshot: "only-on-failure"', self.text)
        self.assertNotIn("10:1", self.text)
        self.assertNotIn("壓倒性", self.text)
        self.assertIn("acceptance", self.text)

    def test_verdict_cannot_exceed_fresh_evidence_and_names_gaps(self) -> None:
        self.assertIn("fresh evidence", self.text)
        self.assertIn("evidence gap", self.text)
        self.assertIn("must not exceed", self.text)


if __name__ == "__main__":
    unittest.main()
