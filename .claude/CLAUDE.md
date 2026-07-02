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

## Fact Verification — CRITICAL, NO EXCEPTIONS
- **Any output that describes something else is not the thing itself**; it may be stale, wrong, incomplete, or misleading, so verify against the primary source it describes.
- **Never present such a claim as a confirmed fact.** Always verify with a primary source before stating anything as true.
- Verification methods (use the appropriate one):
  - Package/repo exists → `gh api repos/owner/name` or direct URL check
  - CLI flag or default behavior → read official docs directly, not a summary
  - Community claim → find the original post/issue/PR, not a third-party blog
- If verification is not possible in the current session, say "I can't confirm this" — do NOT state it as fact.
- **Past failures**: Claimed MCP is more token-efficient (wrong). Claimed Tool Search is enabled by default (wrong — only triggers above 10% context threshold). Both were read from summaries without verification.
- **WebFetch 結構分析失敗（2026-04-15）**：WebFetch Karpathy LLM Wiki gist 後，直接採用模型摘要回報「缺少 `syntheses/` 目錄」，未對照原文驗證。第二次 fetch 才確認原文根本沒有此規範。**正確流程：fetch 後必須針對具體聲明再次 fetch 原文確認，不可直接引用摘要內容。**

## Operation Safety
- Before any destructive operation (rm, force push, reset --hard, drop table, overwrite uncommitted changes): **report the plan and wait for confirmation**.
- Never skip git hooks (`--no-verify`) unless explicitly asked.
- Never force push to main/master.
- Never commit `.env`, credentials, or secret files.
- If unexpected state is found (unknown files, branches, config): investigate before overwriting.

## Investigation Before Action — CRITICAL
**Any file removal, gitignore, deprecation, or config change requires prior investigation:**
1. Who generates this file? (which script / hook / tool)
2. Who reads / consumes it? (grep all referencing files)
3. What breaks if it disappears?
Only after answering all three: propose the action, explain the reasoning, then execute.
**Past failure (2026-05-13):** gitignored `health/report.json` without checking that `actions_review.py` depends on it. The decision happened to be correct, but the process was wrong — acted first, investigated after being challenged. This is not acceptable.

## Task Management
- 跨 session、跨專案的任務一律記到 Notion Actions Engine，不塞進對話；session task（TaskCreate）只用於當次 planning，結束即棄。
- 命名：具體動詞＋對象（脈絡），Type 用欄位不放標題。
- 任務完成立刻標 Done，不拖到對話結束。
- 完整 schema／DB ID／對話式 CRUD 協定見 SecondBrain 專案 CLAUDE.md（單一真實來源，避免雙處 drift）。

## Git Commit Convention
- Format: Conventional Commits — `type(scope): subject`
- Types: `feat` / `fix` / `chore` / `docs` / `refactor`
- Keep subject under 72 characters.
- Body: explain **why**, not what.
- Never amend published commits; create a new one instead.

## Reference Docs (按需查閱,非常駐)
- 要裝/用 **spec-kit + superpowers + bridge**（spec 先行→TDD 開發）時，參考 `00.claudedotfile/references/speckit-superpowers-install.md`（含 Windows cp950 與 Dropbox 鎖檔兩個必踩雷的對策）。
