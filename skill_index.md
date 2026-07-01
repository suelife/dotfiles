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

---

## Bootstrap Integration

執行 `python bootstrap.py` 時會自動：
1. 建立 custom skills 的 symlinks
2. 驗證所有 skills 是否就位
3. 提示手動安裝官方 plugin 的步驟

## Maintenance

- **新增 local skill**：在 `.claude/skills/` 下建立目錄，更新此檔案和 bootstrap.py
- **移除 skill**：從 bootstrap.py 的 SYMLINKS 中移除，刪除物理目錄
- **更新官方 plugin**：通過 Claude Code marketplace，不由此管理
