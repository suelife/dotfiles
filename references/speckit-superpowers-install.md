# 〔已作廢 2026-08-14〕spec-kit + superpowers + bridge 安裝步驟

> **spec-kit 已全面移除**（Wind 裁定；specify-cli 已 uninstall、pulse 的 .specify 與 speckit skills 已清）。
> 本檔保留只因「⚠️ 兩個必踩的 Windows 雷」那一節是通用對策（cp950、Dropbox 鎖檔），其餘安裝步驟不要再照做。

# ~~spec-kit + superpowers + bridge 安裝步驟~~

WHAT 層用 GitHub **spec-kit**(spec→plan→tasks),HOW 層用 **superpowers**(TDD/subagent/review),
中間用第三方 **speckit-superpowers-bridge** 串接(tasks.md 交棒給 superpowers 執行)。

> 實測驗證於 2026-07-02(Windows 11、繁中 cp950 locale、專案在 Dropbox 內)。端到端跑通:
> constitution→specify→plan→tasks→handoff→guard 邊界防護→TDD RED/GREEN→finish→complete。

## ⚠️ 兩個必踩的 Windows 雷(先看這個,否則會被卡)

1. **每次跑 `specify` 都先設 `$env:PYTHONUTF8=1`**
   繁中 Windows(cp950)印成功訊息的「✓」會讓 specify 崩潰、**回傳假 exit 1(其實已成功)**。
   設了 UTF-8 就乾淨 exit 0。這是 spec-kit 作者自己也記錄過的坑。

2. **Dropbox 鎖檔 → init / 刪除會間歇性失敗**
   在 Dropbox 資料夾裡 `specify init` 或事後清除,會被 Dropbox 同步鎖住檔案而失敗
   (`[Errno 22] Invalid argument` 或 `being used by another process`)。
   **對策:重試(通常第二次就過)**,或裝之前暫停 Dropbox 同步,或先在非 Dropbox 目錄 init 再移入。

## 前置(版本需求,已驗證相容)

- `python` 3.11+、`uv`、`git`、`node`/`npm`、`claude`(Claude Code)
- bridge 硬性需求:**spec-kit >= 0.8.10**。superpowers 用 skill「名稱」呼叫,名稱在 5.1.0↔6.0.0 相同,
  且 bridge 不碰 Claude Code 內部 → 版本相容面很寬(實測 spec-kit 0.8.16 / superpowers 5.1.0 / claude 2.1.112 可用)。

## 安裝

```powershell
$env:PYTHONUTF8=1   # ← 每個 specify 指令前都要

# 1. spec-kit CLI(新機器才需要;本機已裝 specify 0.8.16 via uv tool)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@<latest-tag>

# 2. superpowers:已是全域 plugin(superpowers@claude-plugins-official),不需另裝

# 3. 在專案目錄初始化 spec-kit(Claude Code 整合,預設就裝 skills)
cd <project>
specify init --here --integration claude --force   # 非空目錄要 --force;會順便 git init、選 ps 腳本

# 4. 裝 bridge(第三方,從外部 URL 下載;/releases/latest/ 永遠抓最新)
specify extension add speckit-superpowers-bridge `
  --from https://github.com/lihan3238/speckit-superpowers-bridge/releases/latest/download/speckit-superpowers-bridge.zip
```

裝完 `.claude/skills/` 會有 speckit 指令 + 4 個 bridge skill,`.specify/extensions/speckit-superpowers-bridge/` 有腳本。
Claude Code 需在該專案重開 session 才會載入新指令。

## 使用流程

```
/speckit-constitution   → 建立原則(.specify/memory/constitution.md)
/speckit-specify        → 寫 spec(before_specify hook 自動建功能分支)
/speckit-plan           → 技術計畫(before_plan 的 bridge.guard 放行)
/speckit-tasks          → 產 tasks.md(after_tasks 自動建 .specify/superpowers-handoff.json)
/speckit-superpowers-bridge → 把 tasks.md 交棒給 superpowers 執行(TDD→verify→review→finish)
```

handoff 設為 `executing` 期間,bridge guard 會**擋掉** `speckit.implement`、`superpowers:writing-plans`、
`speckit.constitution`(防止越界改設計),只放行 `superpowers:executing-plans`;complete 後恢復放行。

## 注意

- **bridge 是第三方**(lihan3238),非 GitHub 官方。安裝會有「external URL, only install from sources you trust」警告。
- spec-kit 對 **brownfield 弱**(通用模板、不反向抽架構);既有大專案要另配 brownfield 擴充或人工核對 spec。
- 兩個工具都**不強制驗證**——防失真的最後閘門靠 superpowers 的 verify + code review + 人工看 spec。
