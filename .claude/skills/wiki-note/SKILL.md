---
name: wiki-note
description: 從任何 project 快速寫一筆記錄到 SecondBrain wiki。不需要在 SecondBrain 資料夾內也能用。
---

# /wiki-note

從當前 project 快速寫一條記錄到 SecondBrain wiki。

## SecondBrain 路徑

路徑透過環境變數或 home 目錄推導，不 hardcode：

```
SECONDBRAIN = ~/Dropbox/00.SecondBrain
（Windows: %USERPROFILE%/Dropbox/00.SecondBrain）
```

在 Bash 指令中使用 `$HOME/Dropbox/00.SecondBrain` 或直接用 Python `pathlib.Path.home() / "Dropbox/00.SecondBrain"`。

## 步驟

### 1. 確認內容

argument 就是要寫的內容。若沒有 argument，問使用者：「要記什麼？」

### 2. 判斷類型，決定放哪

| 內容類型 | 放在哪 | 檔名格式 |
|---------|--------|---------|
| 概念、方法、技術 | `wiki/concepts/` | `kebab-case.md` |
| 工具、產品、服務 | `wiki/entities/` | `kebab-case.md` |
| 來自當前 project 的洞見、決策 | `wiki/concepts/` | `YYYY-MM-DD-slug.md` |

若已有相關頁面 → 更新該頁，不建新頁。

### 3. 寫頁面

Frontmatter 必填：
```yaml
---
title: <標題>
type: concept | entity
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

內容簡潔，重點在「為什麼重要」和「怎麼用」。加上與現有頁面的 `[[wiki-link]]`。

### 4. 更新 index.md

在 `~/Dropbox/00.SecondBrain/wiki/index.md` 的對應 section 加一行。更新頁數。

### 5. 更新 FTS5 index

```bash
python "$HOME/Dropbox/00.SecondBrain/scripts/wiki_index.py"
```

### 6. 寫入 v4 event stream

```bash
poetry run python "$HOME/Dropbox/00.SecondBrain/scripts/write_event.py" \
  --source "manual-note" \
  --content "<page title>：<one-line summary>" \
  --dedup-key "note-<slug>"
```

驗證回饋（必須在回報中顯示）：
- exit 0 且有 ULID → 「✓ 已同步 events.db」
- SKIP（去重命中）→ 「✓ 已存在 events.db」
- 失敗 → 「⚠️ events.db 寫入失敗，需手動補寫」

### 7. 回報

說明建立或更新了哪個頁面，附上 events.db 同步狀態。
