# Skill Index

紀錄所有通用 skills，便於跨裝置初始化。

## Official Plugins (Claude Code Marketplace)

### superpowers@5.1.0
- **來源**：claude-plugins-official marketplace
- **Included Skills**：
  - using-superpowers
  - brainstorming
  - test-driven-development
  - writing-plans
  - systematic-debugging
  - verification-before-completion
  - finishing-a-development-branch
  - using-git-worktrees
  - receiving-code-review
  - dispatching-parallel-agents
  - requesting-code-review
  - executing-plans
  - subagent-driven-development
  - writing-skills

### code-review@claude-plugins-official
- **Included Skills**：code-review:code-review

### claude-md-management@claude-plugins-official
- **Included Skills**：claude-md-management:revise-claude-md, claude-md-management:claude-md-improver

### claude-code-setup@claude-plugins-official
- **Included Skills**：claude-code-setup:claude-automation-recommender

### microsoft-docs@claude-plugins-official
- **Included Skills**：microsoft-docs:microsoft-docs, microsoft-docs:microsoft-code-reference, microsoft-docs:microsoft-skill-creator

### azure-skills@claude-plugins-official
- **Included Skills**：azure:azure-ai, azure:azure-aigateway, azure:azure-cost, azure:azure-deploy, azure:azure-diagnostics, azure:azure-kubernetes, azure:azure-prepare, azure:azure-reliability, azure:azure-resource-lookup, azure:azure-storage, azure:entra-app-registration, azure:microsoft-foundry（及其他 azure:* skills）

### codex@openai-codex
- **來源**：openai/codex-plugin-cc marketplace（已 clone 至 `~/.claude/plugins/marketplaces/openai-codex-plugin-cc/`）
- **需求**：ChatGPT 帳號或 OpenAI API key + `npm install -g @openai/codex` + `codex login`
- **Included Skills**：codex:review, codex:adversarial-review, codex:rescue, codex:status, codex:result, codex:cancel, codex:setup

---

## Local Custom Skills (Symlinked from claudedotfile)

### fp (First Principles)
- **路徑**：`.claude/skills/fp/`
- **來源**：symlink → `claudedotfile/.claude/skills/fp`

### notebooklm
- **路徑**：`.claude/skills/notebooklm/`
- **來源**：symlink → `claudedotfile/.claude/skills/notebooklm`

### verify (驗證階梯)
- **路徑**：`.claude/skills/verify/`
- **來源**：symlink → `claudedotfile/.claude/skills/verify`
- **何時用**：交付前要回答「這批東西驗到什麼程度」「可以部署了嗎」，或被問「你有沒有真的測過」
- **重點**：薄型 evidence orchestrator；先做 Claim map，再依 Matt 的 TDD／debug／review seam 選 fresh evidence，區分自動化、隔離 runtime、production／使用者驗收三層。UI 必須從真實入口走完整旅程。

## Local Agents

- `agents/*.md` 會逐檔 symlink 到 `~/.claude/agents/`。
- 新增 agent 時更新來源檔後重新執行 bootstrap；本機其他未受管理 agent 不會被移除。

---

## Bootstrap Integration

bootstrap 有三個明確 mode：

1. `python bootstrap.py --dry-run`：只列出 link/settings 收斂計畫。
2. `python bootstrap.py --apply`：先備份，再建立 links 並合併 managed settings；失敗會 rollback。
3. `python bootstrap.py --verify`：唯讀檢查 exact link targets 與 managed settings。

它不安裝 marketplace plugins；手動步驟以本檔為準。

## Maintenance

- **新增 local skill**：在 `.claude/skills/` 下建立目錄，更新此檔案、bootstrap.py 與 tests
- **移除 skill**：先盤點 live consumers，再從 bootstrap 的 managed inventory 移除；不要直接刪除來源
- **更新官方 plugin**：通過 Claude Code marketplace，不由此管理
