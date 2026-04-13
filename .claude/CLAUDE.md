# Global Claude Code Instructions

## Language
- **Always respond in Traditional Chinese (繁體中文)**.
- Code, variable names, comments, and technical identifiers remain in English.
- Error messages and terminal output can be quoted as-is (English), but explanations must be in Traditional Chinese.

## Behavior Rules
- Always read a file before editing it.
- Do not add features, refactoring, comments, or error handling beyond what was explicitly asked.
- Do not guess intent. If unclear, ask before acting.
- Prefer editing existing files over creating new ones.
- Do not delete files without explicit instruction.

## Operation Safety
- Before any destructive operation (rm, force push, reset --hard, drop table, overwrite uncommitted changes): **report the plan and wait for confirmation**.
- Never skip git hooks (`--no-verify`) unless explicitly asked.
- Never force push to main/master.
- Never commit `.env`, credentials, or secret files.
- If unexpected state is found (unknown files, branches, config): investigate before overwriting.

## Git Commit Convention
- Format: Conventional Commits — `type(scope): subject`
- Types: `feat` / `fix` / `chore` / `docs` / `refactor`
- Keep subject under 72 characters.
- Body: explain **why**, not what.
- Never amend published commits; create a new one instead.
