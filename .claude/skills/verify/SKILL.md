---
name: verify
description: Use when preparing to claim a change is complete, fixed, deployable, or ready, or when asked what has actually been verified.
---

# Verify

把「測試通過」轉換成與交付聲明相稱的 fresh evidence。這是一個薄型驗證協調層；它不取代專案指令，也不重寫 Matt 的 `tdd`、`diagnosing-bugs`、`implement`、`code-review`。

## 第一原則

驗證結論 must not exceed 當輪取得的證據。先列要說的話，再為每個聲明選擇能直接觀察其結果的證據；不能從一個綠燈外推另一個未觀察的結果。

### Claim map

開始前建立簡短表格：

| Claim | Risk if false | Observable proof | Fresh command or journey | Evidence gap |
|---|---|---|---|---|
| `<交付聲明>` | `<影響>` | `<結果本身>` | `<這一輪執行>` | `<未驗部分>` |

證據必須 outcome-specific。`HTTP 200` 只證明該請求有成功回應；它不證明新設定、新 provider、資料持久化或使用者看到了 new path。那些聲明各自需要設定讀回、重啟後狀態、資料查詢或實際旅程。

## 依工作類型選驗證迴圈

- 新功能或 bugfix：沿用 Matt `tdd`。測試走 public seam，以 independent source of truth 建立預期，採 vertical slice 的 RED → GREEN；不要讓測試複製 production 演算法。
- 困難 bug：先用 `diagnosing-bugs` 建立 deterministic、red-capable、能重現 exact symptom 的迴圈。
- 實作期間：只跑最接近改動的 focused checks；工作完成後才跑一次適用的 full suite。
- Review：以明確 base commit、merge-base 或其他 fixed point 鎖定範圍；分開檢查 Standards 與 Spec，不以其中一軸代替另一軸。

若專案提供驗證命令、CI gate 或 agent instructions，優先使用它們。先讀 `package.json`、`pyproject.toml`、`Makefile`、Compose、scripts 與相關設定，避免發明另一套開發迴圈。

## 三層證據

| 層 | 內容 | 能證明 | 不能證明 |
|---|---|---|---|
| 1 靜態與自動化 | unit、contract、typecheck、lint、build | 已覆蓋契約在測試環境成立 | 真 runtime、畫面、正式資料 |
| 2 隔離 runtime | 真 process、DB、API、瀏覽器、重啟 | 整合後的實際行為 | production 狀態與後果 |
| 3 production／使用者驗收 | 真部署、真資料、真使用路徑 | 僅正式環境可觀察的結果 | 未執行的其他情境 |

驗證深度由失敗風險決定：純文件或內部重構通常停在第 1 層；使用者可見功能至少到第 2 層；migration、權限、不可逆資料、對外端點或 production cutover 需要明確的人類 GO，再執行第 3 層。舊授權不能自動擴張成新的 production 授權。

## 執行流程

1. 固定範圍與版本：記錄 branch、HEAD、base／fixed point、dirty state；確認 runtime 真正載入這次變更，而非舊 image 或舊 process。
2. 寫 Claim map，逐項標明證據層級、負向案例、資料與環境前提。
3. 執行 focused checks；記錄完整命令、exit code、pass／fail／deselect／warning 數字，不從先前結果推算。
4. 對新測試保留 RED 證據，或用受控 mutation 證明它會抓到缺陷；禁止破壞使用者的 dirty worktree。
5. 執行適用的 full suite 與 build；若跳過昂貴 gate，寫成 evidence gap，不得默認通過。
6. 需要 runtime 時，以隔離資源、bounded timeout、可驗 cleanup、before／after guard 執行。不要把測試資源寫進 canonical data。
7. 使用者可見 UI 必須從 real entry point 走完整旅程，而不是直接跳內頁：
   - 實際點擊每個改動的互動與下一步，觀察 loading、empty、error、success；
   - 判斷 duplicate controls、無反應按鈕、關閉後 focus、鍵盤與 accessibility；
   - 讀 console、network、page errors；API 綠燈不能替代畫面與互動；
   - 每一步記錄「使用者看到什麼」，必要時截圖，不只量 DOM。
8. 重新讀 diff、範圍與清理結果，確認驗證本身未造成未授權 mutation。

## 證據留存

Playwright 官方支援 `trace: "retain-on-failure"` 與 `screenshot: "only-on-failure"`，但這是可用能力，不是所有專案的強制預設：

- https://playwright.dev/docs/test-use-options

是否留 trace、screenshot、HTML report 或 CI artifact，依 acceptance、除錯需求、敏感資料與團隊可取用性決定。GitHub Actions 官方文件說明 artifact 與 `retention-days`，不代表每個專案都必須上傳：

- https://docs.github.com/en/actions/tutorials/store-and-share-data

禁止用搜尋筆數、未驗證比例或「大家都這樣做」當規則。失敗證據通常最有除錯價值；但視覺驗收、稽核或人類 GO／NO-GO 可能需要成功證據。

## 回報格式

回報至少包含：

- 已驗證：claim → fresh evidence → 結果。
- 未驗證：每個 evidence gap 及其風險。
- 環境：版本、資料範圍、是否隔離、是否觸及 production。
- 終態：清理、git status、殘留資源與 rollback 狀態。
- 結論：只說 `verified at layer N`、`ready for human GO`、`blocked` 或 `not verified` 等與證據相稱的話。

禁止用「應該可以」「看起來正常」代替證據。若 fresh evidence 失敗或缺失，就先修正或如實標記，不得宣稱完成。
