# Verify skill research — 2026-08-25

## Question

How should Wind's global `/verify` skill combine the useful parts of the current Dropbox and live copies while remaining compatible with Matt Pocock's modular engineering skills and Superpowers process gates?

## Primary sources reviewed

- Matt Pocock, `mattpocock/skills` at commit [`6654f6b`](https://github.com/mattpocock/skills/commit/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76): [`tdd`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/tdd/SKILL.md), [`tests.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/tdd/tests.md), [`implement`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/implement/SKILL.md), [`diagnosing-bugs`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/diagnosing-bugs/SKILL.md), and [`code-review`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/code-review/SKILL.md).
- Superpowers at commit [`b36e082`](https://github.com/obra/superpowers/commit/b36e0829c6d0140e93cfef2ca599b1b07d4a7797): [`verification-before-completion`](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/verification-before-completion/SKILL.md).
- Addy Osmani, `addyosmani/agent-skills` at commit [`5a5ea45`](https://github.com/addyosmani/agent-skills/commit/5a5ea45e806f82273549fd85e60adb95d55f510d): [`test-driven-development`](https://github.com/addyosmani/agent-skills/blob/5a5ea45e806f82273549fd85e60adb95d55f510d/skills/test-driven-development/SKILL.md), [`browser-testing-with-devtools`](https://github.com/addyosmani/agent-skills/blob/5a5ea45e806f82273549fd85e60adb95d55f510d/skills/browser-testing-with-devtools/SKILL.md), and [`code-review-and-quality`](https://github.com/addyosmani/agent-skills/blob/5a5ea45e806f82273549fd85e60adb95d55f510d/skills/code-review-and-quality/SKILL.md).
- Coco at commit [`992abf3`](https://github.com/coco-research/coco/commit/992abf3489adf5bb229b17a4a3036cd1690795f5): [`code-verification`](https://github.com/coco-research/coco/blob/992abf3489adf5bb229b17a4a3036cd1690795f5/skills/code-verification/SKILL.md).
- Playwright official docs: [configuration options](https://playwright.dev/docs/test-use-options) and [CI HTML report upload](https://github.com/microsoft/playwright/blob/main/docs/src/ci-intro.md).
- GitHub official docs: [workflow artifact storage and `retention-days`](https://docs.github.com/en/actions/tutorials/store-and-share-data).

## Findings

### Matt uses a chain, not a universal checklist

Matt separates responsibilities:

- `tdd` chooses a public seam, uses independent expected values, and advances one vertical red-green slice at a time.
- `diagnosing-bugs` first builds a deterministic red-capable feedback loop that reproduces the user's exact symptom.
- `implement` runs focused checks during development and the full suite once at the end.
- `code-review` independently checks Standards and Spec against a pinned fixed point.

The local `/verify` skill should therefore orchestrate and record these proofs, not duplicate the full contents of Matt's skills.

### Superpowers owns the completion-claim gate

`verification-before-completion` requires a fresh command, full output, exit code, failure count, and a claim no broader than the evidence. `/verify` should keep this as the final gate and add project-specific evidence selection before it.

An open Superpowers issue, [#1754](https://github.com/obra/superpowers/issues/1754), demonstrates a useful failure mode but is not an accepted upstream rule: HTTP 200 can prove that an endpoint responded while failing to prove that the intended provider or configuration actually changed. Wind's skill should explicitly require an observable outcome unique to the requested change.

### Runtime UI verification must cover the human journey

Addy's browser skill checks actual DOM, console, network, accessibility, performance, and screenshots. This supports the live `/verify` copy's newer rule: start at the real entry point, complete the changed user journey, and judge duplicate controls, focus return, navigation, empty/error states, and whether the next action is discoverable. Numeric DOM assertions alone cannot prove that the interaction makes sense.

### Avoid universal language-specific lint lists

Coco's seven-category checklist is useful for React-heavy repositories, but TDZ, React hooks, mock isolation, and CSS selectors do not apply globally. Those checks belong in project standards or stack-specific skills. `/verify` should discover and run the repository's own commands rather than hard-code a JavaScript checklist.

### Evidence retention claims need narrower wording

Playwright officially supports `screenshot: "only-on-failure"` and `trace: "retain-on-failure"`; its official GitHub Actions example uploads the HTML report with `if: !cancelled()` and `retention-days: 30`. GitHub documents configurable artifact retention. These facts establish available mechanisms, not a universal default. A project can select failure-oriented and CI-accessible evidence when its acceptance, debugging, privacy, and audit needs justify it.

The existing statement that this is an "industry overwhelming majority" and that GitHub usage is roughly `10:1` was not established by these primary sources. It should be removed rather than repeated as fact. Projects may retain successful visual evidence when the acceptance contract, audit requirement, or human review explicitly needs it.

## Integration decision

Keep `/verify` as a thin verification orchestrator with five required outputs:

1. **Claim map:** each intended claim mapped to an observable, outcome-specific proof.
2. **Development proof:** TDD red-green evidence at the pre-agreed public seam, focused checks, then repository full gates.
3. **Runtime proof:** actual service/data/browser behavior where static checks cannot observe the claim.
4. **Review proof:** pinned Standards and Spec review, with unresolved findings stated separately.
5. **Honest verdict:** fresh evidence, exact gaps, and no completion claim beyond the proven layer.

Retain both local additions after correcting their conflict: when automated artifacts are selected, failure-oriented modes are the recommended low-noise option; changed UI journeys are still walked and visually inspected. A required human-review screenshot is acceptance evidence, not debugging artifact noise.

## Out of scope

- Copying Matt, Superpowers, Addy, or Coco skills wholesale.
- Replacing stack-specific test commands with one global command list.
- Treating an open GitHub issue as an accepted upstream standard.
- Requiring production deployment for every change; the highest necessary layer depends on the claim and risk.
