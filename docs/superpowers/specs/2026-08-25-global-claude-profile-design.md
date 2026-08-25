# Global Claude Profile Design

- Status: Accepted in conversation on 2026-08-25
- Owner: Wind
- Scope: `00.claudedotfile`, selected non-secret `~/.claude` configuration, and global `/verify`

## Problem

The Dropbox profile and live Claude home have drifted. The current bootstrap silently skips conflicts, overwrites complete settings branches, lacks backup/rollback, and verifies only part of what it manages. The global profile also grants SecondBrain paths and runs a SecondBrain inbox hook in every project. The live and Dropbox `/verify` copies contain different useful rules.

## Global boundary

The portable global profile keeps rules Wind wants in every Claude project: language, safety, primary-source verification, Git discipline, Matt/Superpowers arbitration, model routing, Pulse project-task policy, and report/diagram conventions. Project credentials, dataset identifiers, repository-specific commands, and SecondBrain lifecycle automation stay in their project.

The August 2026 Pulse policy supersedes the May 2026 note that all task management must be project-local. The May note remains historical evidence but will be marked superseded rather than deleted.

## Portable profile

Dropbox remains the source for:

- global `CLAUDE.md`;
- `statusline.sh`;
- explicit custom skills `fp`, `notebooklm`, and `verify`;
- explicit top-level agent files;
- hook scripts and operator documentation.

Claude credentials, history, project sessions, settings, caches, backups, and runtime state remain local.

## Bootstrap contract

`python bootstrap.py` exposes exactly one explicit mode:

- `--dry-run`: report exact actions without mutation;
- `--apply`: preflight, create a timestamped local backup, converge links/settings, rollback on failure, and verify;
- `--verify`: read-only exact-target and managed-settings verification.

Tests call the public CLI with `--profile-root` and `--home` against temporary trees. A no-mode invocation prints help and performs no mutation.

The bootstrap classifies missing destinations, correct links, wrong/broken links, regular files, and directories. It reports an existing link target before replacement. Correct links are idempotent. Apply preflights source completeness, destination containment, duplicate mappings, forbidden portable state, JSON validity, and Windows symlink capability before moving user files.

## Settings convergence

The bootstrap owns only these settings fragments:

- `statusLine` pointing to the portable statusline;
- removal of the two formerly managed global `additionalDirectories` entries;
- removal of the formerly managed SecondBrain `check_inbox.py` SessionStart hook;
- the two global citation PostToolUse hooks.

Unrelated additional directories and hooks are preserved. Managed PostToolUse hooks are replaced by stable command identity, not appended repeatedly. The entire pre-change settings file is backed up locally before a changed file is written.

## Verify skill contract

`/verify` is a thin evidence orchestrator. It does not duplicate Matt, Superpowers, browser, security, or stack-specific skills. Every verdict contains:

1. a claim map from intended outcome to outcome-specific observable proof;
2. TDD evidence at pre-agreed public seams with independent expected values and vertical red-green slices;
3. focused checks during implementation and the repository's complete final gates;
4. runtime evidence for claims static checks cannot observe, including changed UI journeys from the real entry point;
5. pinned Standards and Spec review evidence;
6. a verdict whose scope does not exceed fresh evidence, with gaps stated explicitly.

HTTP success, process existence, or a test count cannot prove a configuration/provider/data-path change unless the observation distinguishes the new path from the old one. Browser-facing work checks console, network, accessibility, visible state, focus/navigation, duplicate controls, and the actual next action.

Failure-oriented Playwright trace/screenshot retention is the default when the project uses Playwright. Successful screenshots are retained only when an acceptance contract, audit requirement, or human visual review needs them. Unsupported prevalence claims are removed.

## Recovery and integration

Existing uncommitted profile edits were checkpointed before the feature branch. Apply reports one local backup root. Rollback restores only paths journaled by that apply. No remote push occurs without separate approval.

SecondBrain's stale Notion task block is documented as dependent project drift but is not edited in this work because that repository has unrelated uncommitted and untracked state.

## Acceptance

- Public CLI tests prove dry-run immutability, backup, wrong-link convergence, settings merge/removal, idempotence, forbidden-state rejection, rollback, and verify diagnostics.
- Skill contract tests reject missing claim maps, outcome-insensitive proof, missing public seams, missing runtime UI journey, missing Standards/Spec review, and over-broad completion verdicts.
- Hook self-tests remain green.
- Real `--dry-run`, guarded `--apply`, and `--verify` pass against the live profile.
- Live settings retain unrelated values while removing only the two path grants and the managed SecondBrain SessionStart hook.
- The live `verify` path becomes an exact symlink to the researched portable source.
