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

## Subagent／Workflow 派工（分級指定模型，別全用繼承的主模型）
派 subagent／Workflow 時**依任務分級指定 `model`**（準則：用能勝任的**最小**模型，省成本、加速）；不要全留預設＝繼承主模型（拿 Opus 跑機械活是浪費）。`/workflows` UI 不顯示 model，故**撒 workflow 時要在訊息裡標明每段用哪個**，讓使用者看得到。
- **Haiku**：純機械、規格明確、1–2 檔（文案/用詞替換、regen 型別、跑測試回報、樣板小元件、簡單接線）
- **Sonnet**：標準功能實作、多檔整合、照 pattern 擴充——implementer 預設
- **Opus**：migration／跨切面、架構／設計、規劃／研究／synthesis、**對抗式/嚴格審查（品質關卡不降級）**
- **Fable**：定位未確認，先不用；要用先查證
- 第二槓桿 `effort`（low→max）：機械段 low、難審查段 high/xhigh。
- 預設配比：implementer=Sonnet（機械降 Haiku、難的升 Opus）｜審查=Opus｜fixer 同 implementer｜規劃/研究/critic 型 workflow=Opus。

## Git Commit Convention
- Format: Conventional Commits — `type(scope): subject`
- Types: `feat` / `fix` / `chore` / `docs` / `refactor`
- Keep subject under 72 characters.
- Body: explain **why**, not what.
- Never amend published commits; create a new one instead.

## Reference Docs (按需查閱,非常駐)
- 要裝/用 **spec-kit + superpowers + bridge**（spec 先行→TDD 開發）時，參考 `00.claudedotfile/references/speckit-superpowers-install.md`（含 Windows cp950 與 Dropbox 鎖檔兩個必踩雷的對策）。

## 視覺化圖表風格
- 需要畫**結構性圖**時（限系統架構／流程／資料模型／領域地圖，見 `visualization-scope` memory），一律套 `00.claudedotfile/references/diagram-style.md` 的視覺規格（色彩 token／字體角色／元件詞彙／設計原則），**不臨場自訂**。
- 交付走 **HTML 檔＋Artifact**（此環境 `show_widget` 無效、CSP 內聯一切、禁 CDN／外部字型）；決策清單／審查摘要／metrics 速覽（commits・測試數）／一般回覆一律**純文字**。
- 該規格元件分「基元（恆用）」與「可選敘事裝置（ecg／heart／loop／run，僅內容真有核心／循環／指令時才用）」；**預設只用基元**，不要把來源圖的敘事家具原封搬到每張圖（那會製造 AI 味）。
- accent 用靛藍是**刻意**與 app 青綠 UI 區隔（架構圖非產品截圖）；細節見規格。此段只觸發風格，「要不要畫」的界線仍由 `visualization-scope` memory 決定。
