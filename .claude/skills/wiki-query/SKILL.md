---
name: wiki-query
description: 從任何 project 查詢 SecondBrain wiki，用 FTS5 搜尋後合成答案。
---

# /wiki-query

從當前 project 查詢 SecondBrain wiki。

## SecondBrain 路徑

路徑透過 home 目錄推導，不 hardcode：

```
SECONDBRAIN = ~/Dropbox/00.SecondBrain
DB          = ~/Dropbox/00.SecondBrain/.db/wiki.db
```

## 步驟

### 1. FTS5 搜尋

```python
import sqlite3, pathlib
db = pathlib.Path.home() / "Dropbox/00.SecondBrain/.db/wiki.db"
conn = sqlite3.connect(db)
rows = conn.execute(
    "SELECT path, title FROM wiki_fts WHERE wiki_fts MATCH ? ORDER BY rank LIMIT 5",
    ("<query>",)
).fetchall()
```

若 DB 不存在或搜尋無結果，改讀 `wiki/index.md` 手動找。

### 2. 讀相關頁面

讀 Step 1 找到的路徑（相對於 SecondBrain 根目錄）。

### 3. 合成答案

直接回答問題，附上引用：`[[page-name]]`。

### 4. 提議存入 wiki（選擇性）

若答案包含新的分析或連結，問：「要存進 wiki 嗎？」
若是 → 用 `/wiki-note` 存。
