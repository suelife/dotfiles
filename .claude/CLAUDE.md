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
- **WebFetch and WebSearch summaries are NOT facts.** They are model-generated and frequently wrong, incomplete, or misleading.
- **Never present a search/fetch summary as a confirmed fact.** Always verify with a primary source before stating anything as true.
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

## Task Management

### 唯一 task 系統：Notion Actions Engine
- **跨 session、跨專案的任務一律建在 Notion Actions Engine**（DB ID: `2f021f4e-14f0-8041-9289-e27da0f79ef3`）
- `TaskCreate`（session task）**只能用於當次對話的 planning**，對話結束後即消失
- **對話結束前**，若有未完成的 session task，必須詢問使用者：「要建到 Notion 還是放棄？」
- 必填欄位：`Name`（命名規則）、`Status: To do`、`Type`。`Energy` 由使用者自行填寫，不代填

### Task 命名規則
格式：`具體動詞＋對象（脈絡）`，Type 用欄位設定，不放標題。

- **動詞**：具體可執行（調查、修復、建立、確認、規劃、申報…），不用「處理」、「弄一下」等模糊詞
- **對象**：明確指出做什麼
- **脈絡**：括號選填，說明觸發原因或所屬系統

範例：
```
調查並修復 NotebookLM 頻繁 session timeout   → Type: Dev
確認供應商主檔幣別欄位（BPM 外幣功能）        → Type: Work
申報遺產稅                                  → Type: Life
```

### Actions Engine Schema（已驗證，勿動態查詢）
- **MCP data_source_id**：`2f021f4e-14f0-8062-ac82-000b46f8db2e`
- **REST database_id**：`2f021f4e-14f0-8041-9289-e27da0f79ef3`
- **Type 選項**：`Idea` / `Life` / `Work` / `Dev`
- **Status 選項**：`To do` / `In progress` / `Done`
- **Energy 選項**：`High` / `Medium` / `Low`（使用者自填，Claude 不代填）
- **必填欄位**：`Name`、`Status`、`Type`

## Git Commit Convention
- Format: Conventional Commits — `type(scope): subject`
- Types: `feat` / `fix` / `chore` / `docs` / `refactor`
- Keep subject under 72 characters.
- Body: explain **why**, not what.
- Never amend published commits; create a new one instead.
