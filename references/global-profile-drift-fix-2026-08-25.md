# Global Claude profile drift fix — 2026-08-25

## Outcome

Big Sister's portable Dropbox profile is now the canonical source for every explicitly managed global file. The live Claude home was converged through the tested `bootstrap.py` flow, not by copying an entire `.claude` directory.

- Portable implementation range: `77f7383..152081c`.
- Live apply backup: `C:\Users\wind.kuo\.claude\portable-backups\20260825T083905.917374Z`.
- Remote push: not performed.
- SecondBrain repository: not modified because it contains unrelated dirty state.

## Corrected pre-activation evidence

The live state immediately before activation was re-read on 2026-08-25. It had one `SessionStart` group, not zero. That group invoked SecondBrain's `check_inbox.py`; earlier evidence that described the hook as missing was stale and must not be used as the current state.

| Surface | Before | After |
|---|---:|---:|
| Global `additionalDirectories` | 2 managed entries | 0 |
| `SessionStart` groups | 1 SecondBrain inbox group | 0 |
| `PostToolUse` groups | 2 citation groups | 2 citation groups |
| Live `skills/verify` | ordinary directory | exact symlink to portable source |
| Other managed links | correct symlinks | unchanged correct symlinks |

The pre-change `settings.json` SHA-256 was `8a5dacc0e1dddb3d54fefaf75fc468e379a282e221be6f82e95312a7571f3589`. Post-apply read-back was exactly equal to running the managed merge over the backed-up JSON (`SETTINGS_EXACT_EXPECTED=True`). A separate one-off projection that did not call the production merge function stripped only the declared managed identities from both files and returned `INDEPENDENT_UNMANAGED_EQUAL=True`. Together they prove unrelated top-level settings, permissions, plugins, marketplaces, hooks, effort, and local warning preferences were preserved.

## Verify integration

The old live and Dropbox variants were replaced by one portable skill. The merged design keeps the lived UI-journey lessons while adopting Matt-compatible module boundaries:

- map each intended claim to outcome-specific proof;
- test through a public seam with an independent source of truth;
- use vertical RED → GREEN slices;
- run focused checks during implementation and the applicable full suite at the end;
- review from a fixed point and keep Standards separate from Spec;
- walk user-visible changes from the real entry point, including duplicate controls, focus, keyboard/accessibility, console, network, and the actual next action.

Primary-source research and pinned revisions are recorded in `references/verify-skill-research-2026-08-25.md`. Unsupported prevalence claims such as a GitHub-wide ratio were removed. Playwright trace/screenshot retention is conditional on acceptance, debugging, privacy, and audit needs rather than declared universal.

## Bootstrap and portability changes

`bootstrap.py` now requires exactly one explicit mode:

- `--dry-run`: read-only plan;
- `--apply`: preflight, timestamped backup, link/settings convergence, rollback, and read-back;
- `--verify`: exact-link and managed-settings verification.

Temporary-home tests prove ordinary/wrong links, settings preservation, managed removal, idempotence, forbidden portable state, rollback after a controlled link failure, and symlink-capability failure before backup or user-path movement. Cache directories are ignored. The pre-existing `.mypy_cache` and the run-generated `__pycache__` were moved into the activation backup under `generated-cache/`; neither was deleted.

## Live activation evidence

1. `python bootstrap.py --dry-run` reported only the ordinary `verify` directory and managed settings.
2. `python bootstrap.py --apply` returned `APPLY_OK` and the backup root above.
3. `python bootstrap.py --verify` returned `VERIFY_OK`.
4. A second `python bootstrap.py --apply` returned `BACKUP_ROOT=none`, `UNCHANGED`, and `APPLY_OK`.
5. Exact link read-back passed for `CLAUDE.md`, `statusline.sh`, `fp`, `notebooklm`, `verify`, and `agents/learn.md`.

## Intended operational effects

- Claude sessions outside SecondBrain no longer receive blanket SecondBrain/claudedotfile directory grants.
- Every new global session no longer runs the SecondBrain inbox hook. SecondBrain lifecycle automation must be owned by that project.
- Citation hooks remain global.
- `verify` will often request stronger runtime or UI evidence for user-visible claims, but it does not reuse an old production authorization; production still needs a current human GO.
- New computers can reproduce the profile using the documented dry-run/apply/verify flow without syncing credentials, history, sessions, settings, or caches.

## Recovery

The activation backup contains the complete pre-change `settings.json`, the old ordinary `skills/verify` directory, and both generated caches. Recovery should be performed with Claude Code stopped: restore only the journaled paths from that backup, then run the pre-change bootstrap version or inspect the links manually. No rollback was needed during activation.

## Deferred project drift

SecondBrain's May global-profile note and its stale Notion task block remain dependent project drift. They were deliberately not edited in this work because that repository had unrelated modified and untracked files. The August global Pulse decision is the active global rule; the May note is historical evidence, not the current authority.
