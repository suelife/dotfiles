# Global Claude Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converge Big Sister's portable and live global configuration with recoverable settings/link changes and a researched evidence-driven `/verify` skill.

**Architecture:** A Python public CLI owns a declarative set of portable links and narrowly identified settings fragments. Temporary-home integration tests drive dry-run/apply/verify behavior; the live profile is changed only after local gates pass and a backup is recorded.

**Tech Stack:** Python 3, Windows symbolic links, JSON, Git, Dropbox

**Spec:** `docs/superpowers/specs/2026-08-25-global-claude-profile-design.md`

## Global Constraints

- Do not read, print, copy, or commit credentials, tokens, history, sessions, or project runtime state.
- Preserve unrelated links, settings keys, hooks, additional directories, and working-tree changes.
- Use public CLI tests against temporary directories; do not test only private helpers.
- No live mutation before focused and full local gates pass.
- No remote push without separate human approval.

---

### Task 1: Capture research and behavior contracts

**Files:**
- Create: `references/verify-skill-research-2026-08-25.md`
- Create: `tests/test_bootstrap.py`
- Create: `tests/test_verify_skill.py`

**Interfaces:**
- Consumes: accepted design and pinned primary GitHub sources.
- Produces: public CLI and skill-document assertions used by later tasks.

- [ ] Write CLI tests for explicit modes, dry-run immutability, backup, exact links, wrong links, settings preservation/removal, idempotence, rollback, and verify diagnostics.
- [ ] Run the tests against the current bootstrap and confirm RED for the missing CLI contract.
- [ ] Write skill contract tests for claim mapping, public seams, independent expectations, focused/full gates, runtime journey, outcome-sensitive proof, Standards/Spec review, evidence retention, and bounded verdicts.
- [ ] Run the skill tests against the current portable skill and confirm the intended missing-contract failures.
- [ ] Commit research and RED tests with `test(profile): define convergence contracts`.

### Task 2: Implement the transactional bootstrap

**Files:**
- Modify: `bootstrap.py`
- Test: `tests/test_bootstrap.py`

**Interfaces:**
- Consumes: `--dry-run|--apply|--verify`, optional `--profile-root`, and optional `--home`.
- Produces: exit `0` with `DRY_RUN_OK`, `APPLY_OK`, or `VERIFY_OK`; non-zero with path-specific diagnostics; `BACKUP_ROOT=<path|none>` on apply.

- [ ] Implement argument parsing and declarative mappings until the explicit-mode/dry-run slice is GREEN.
- [ ] Implement complete preflight and timestamped backup until regular/wrong-link slices are GREEN.
- [ ] Implement settings ownership by stable path/command identity until preservation/removal slices are GREEN.
- [ ] Implement rollback journal and exact read-back verification until failure/idempotence slices are GREEN.
- [ ] Run the full bootstrap test file twice and hook self-tests.
- [ ] Commit with `feat(profile): make bootstrap transactional`.

### Task 3: Integrate the researched verify skill

**Files:**
- Modify: `.claude/skills/verify/SKILL.md`
- Test: `tests/test_verify_skill.py`

**Interfaces:**
- Consumes: a requested completion/deployment/readiness claim and the repository's spec, standards, commands, and runtime surfaces.
- Produces: claim map, layered evidence, review findings, and an honest scoped verdict.

- [ ] Merge the live user-journey rules into the portable source without dropping the existing failure-artifact policy.
- [ ] Replace unsupported prevalence claims with pinned Playwright/GitHub facts and conditional evidence rules.
- [ ] Add Matt-compatible public seam, independent expected value, vertical-slice, focused/full gate, and Standards/Spec review requirements.
- [ ] Add outcome-sensitive configuration/data-path proof and explicit no-overclaim wording.
- [ ] Run focused skill contract tests to GREEN and inspect the complete skill for duplicated workflows.
- [ ] Commit with `docs(verify): integrate evidence-driven quality gates`.

### Task 4: Reconcile inventories and generated drift

**Files:**
- Create: `.gitignore`
- Modify: `skill_index.md`
- Modify: `references/speckit-superpowers-install.md`
- Modify: `C:\Users\wind.kuo\Dropbox\00.SecondBrain\memory\feedback_global_claude_config.md` only after its repository state receives a separate safe integration decision.

**Interfaces:**
- Consumes: the bootstrap manifest and current portable tree.
- Produces: one inventory matching every managed link and explicit local-only boundaries.

- [ ] Generate or validate the documented skills against the bootstrap manifest, including `notebooklm`.
- [ ] Mark `agents/auto` local-only.
- [ ] Ignore `.mypy_cache` and move the existing generated cache to the local apply backup rather than deleting it.
- [ ] Record the superseded May global-profile decision without changing the dirty SecondBrain worktree in this branch.
- [ ] Commit with `docs(profile): reconcile portable inventory`.

### Task 5: Activate and verify the live profile

**Files:**
- Modify through bootstrap: selected `~/.claude` links and managed `settings.json` fragments.
- Create locally: timestamped `~/.claude/portable-backups/<timestamp>`.

**Interfaces:**
- Consumes: tested branch worktree and current live profile.
- Produces: exact portable links, narrowed live settings, and a recoverable backup root.

- [ ] Run all Python tests, hook self-tests, compile checks, and `git diff --check`.
- [ ] Run real `--dry-run` and inspect all actions.
- [ ] Run real `--apply` once and record the backup root.
- [ ] Run real `--verify`, compare unrelated settings before/after, and confirm the second apply is idempotent.
- [ ] Run a fixed-point Standards and Spec review of the branch.
- [ ] Commit final docs/report with `docs(profile): record verified activation` and leave integration/push to the explicit branch handoff.
