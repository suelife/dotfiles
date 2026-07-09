# 視覺化圖表風格規格

畫**結構性圖表**（系統架構／流程／資料模型／領域地圖）時的**視覺語言規格**：色彩 token、字體角色、版面元件詞彙、設計原則、起手骨架。
萃取自 project_managment 的 living-WBS 架構圖那一張——但**只保留其中可遷移的通用層**；那張圖獨有的敘事家具（心跳線、心臟列、四拍迴圈、部署指令）已隔離到「可選敘事裝置」小節，預設不畫，避免每張衍生圖都變成 living-WBS 圖的翻版。

> **邊界（HOW，不是 WHEN）**：本文件只管「已決定要畫之後、畫成什麼樣」。「要不要畫、畫什麼」由 `visualization-scope` memory 決定——只畫**結構性內容**（架構／流程／資料模型／領域地圖）；決策清單、審查摘要、metrics 速覽、一般回覆一律**純文字**。本規格**不鼓勵多畫圖**，只在已決定要畫之後統一風格。

> 實測驗證於 2026-07-09（Windows 11、Artifact viewer 明暗雙主題切換、CSP 內聯無外部請求）。端到端跑通：Write 單一 `.html` → Artifact 發佈 → viewer 明/暗切換不漏色（前提：`[data-theme]` 兩區塊完整填滿，見骨架）。

## ⚠️ 兩個必先知道的交付前提（先看這個，否則白畫）

1. **本環境 `show_widget` 無效** → 不要用它出圖。改走：**Write 寫一個單一 `.html` 檔** → 呼叫 **Artifact 工具**發佈成 claude.ai 網頁。同檔重發佈用**同一 file_path** 才更新同一 URL。
2. **檔案只寫內容、不寫外殼** → 發佈時系統自動包 `<!doctype html><head>…</head><body>`。檔案**直接**從 `<title>`＋`<style>`＋內容開始，**不要**自己寫 `<!DOCTYPE>`／`<html>`／`<head>`／`<body>`。

## CSP 鐵律（一切內聯，禁外部主機）

CSP 封鎖所有外部請求——**無 CDN script、無 remote stylesheet、無 webfont、無 remote image、無 fetch**。因此：

- **CSS** 全內聯在 `<style>`。
- **字型** 只用 system stack（見下），`@font-face` remote 會 silent fallback 成不可控字型。
- **圖形** 用內聯 SVG；需要圖片改 `data:` URI。
- **寬內容**（表格／程式碼）自己包 `overflow-x:auto`；**頁面本體絕不橫向捲動**。
- **Artifact 呼叫參數**：傳 emoji `favicon`（技術圖適合 📊／🗺️／🧩，心跳母題才用 💓）、一句 `description`、穩定 `<title>`。

## 色彩 Token 系統（雙套 CSS custom properties）

**元件從不寫死 hex，一律走 token。** 分中性階＋語意色兩組，語意色一律成對（前景＋`-soft` 底）。

### 中性階（ground → ink）

| Token | Light | Dark | 角色 |
|---|---|---|---|
| `--bg` | `#F5F6FB` | `#0C0E15` | 頁面地面 |
| `--surface` | `#FFFFFF` | `#151824` | 卡片/節點面 |
| `--surface-2` | `#FAFBFF` | `#11131D` | 次級凹面（cell/巢狀底） |
| `--border` | `#E4E7F1` | `#262B3B` | 一般描邊 |
| `--border-strong` | `#CBD1E2` | `#3A425C` | 強描邊/虛線計畫框 |
| `--ink` | `#181B27` | `#E9EBF4` | 主文字 |
| `--muted` | `#5A6175` | `#9CA3B8` | 次要文字 |
| `--faint` | `#8A91A5` | `#6D7488` | eyebrow/最弱標籤 |

> 中性階**每個值都帶刻意的冷藍紫色偏**（`#F5F6FB`／`#181B27` 不是純灰）。這是 taste 守則，不是巧合：擴充新增中性色時沿用此色偏，**禁用純中性灰**（`#888`／`#ccc`）——純灰是 AI 味的來源。

### 強調色 accent（三階，單一靛藍）

| Token | Light | Dark |
|---|---|---|
| `--accent` | `#4F46E5` | `#8983F2` |
| `--accent-deep` | `#4338CA` | `#A29BFF` |
| `--accent-soft` | `#EEF0FE` | `#20233B` |

> **accent 與專案 app UI 的關係（刻意分歧，非疏漏）**：本規格 accent 是**單一靛藍**，刻意與 living-WBS **app 本身的青綠 UI**（見 `ui-delivery-verification` memory）**區隔**。理由：架構圖是「對系統的後設說明」，不是 app 截圖；用不同色相讓讀者一眼分辨「這是說明圖，不是產品畫面」。
> 若某專案反而要讓架構圖與其產品色**一致**，accent 是**單一 token**：把 `--accent`／`--accent-deep`／`--accent-soft` 三階換成該產品色即可，其餘 token 不動。語意色（ok/warn/alert/ref）**不隨之變**——它們是狀態編碼，跨專案固定。

### 語意色（各帶 `-soft` 底，soft 供深色文字墊底保對比）

| 語意 | 前景 L / D | soft 底 L / D | 編碼意義 |
|---|---|---|---|
| `--ok` | `#0DA36C` / `#3DD892` | `#E2F5EC` / `#123227` | 已建/完成/健康 |
| `--warn` | `#DB9016` / `#E6A63C` | `#FAF0D9` / `#3A2E15` | 警示（備而少用） |
| `--alert` | `#DE4C4C` / `#F0736F` | `#FBE7E7` / `#3A1F1F` | 逾期/危險 |
| `--ref` | `#7B8296` / `#8C93A8` | `#EEF0F5` / `#20242F` | 外部引用系統（非內建） |

陰影也是 token：`--shadow` light 為 `0 1px 2px rgba(24,27,39,.04),0 8px 24px -12px rgba(24,27,39,.14)`；dark 換 `rgba(0,0,0,.3/.6)`＋加大 blur。

### 主題切換（三段，分別靠**順序**與**特異度**）

1. `:root{…}` 先定 **light 當預設**。
2. `@media (prefers-color-scheme:dark){:root{…}}` 覆蓋為 dark → 順應**系統設定**（無 JS 也對）。**stage 1→2 靠 source order**：兩者特異度相同，後寫者勝。
3. `:root[data-theme="dark"]{…}` 與 `:root[data-theme="light"]{…}` 兩條**手動覆蓋** → viewer 切換鈕在 root 打 `data-theme` 後勝出。**stage 3 靠特異度、不靠順序**：`:root[data-theme]` 特異度為 (0,2,0)，高於 media query 內 `:root` 的 (0,1,0)，故**無論寫在 media query 前或後**都勝過它。
   → 正因為 stage 3 是完整覆蓋，**dark/light 兩區塊必須各自完整重列所有 token**（骨架已填滿，**勿留空註解**——留空手動切換會失效），切換才不漏色。

## 字體角色（只有兩個 font stack，靠字族分工資訊層級）

- `--sans`：`-apple-system,"Segoe UI Variable Text","Segoe UI",system-ui,"Noto Sans TC",sans-serif`
- `--mono`：`ui-monospace,"Cascadia Code","SF Mono",Consolas,"Liberation Mono",monospace`

**為何全 system stack**：CSP 封外部字型，指定安裝字型會 silent fallback。system stack 每個 OS 都命中原生字（含中文 Noto Sans TC / Segoe UI），零網路、零 FOUT、跨平台一致。
> 這也是 taste 立場，不只是 CSP 副作用：**不預設 Inter／Space Grotesk 這類 AI 簡報慣用體**。就算哪天 CSP 放寬，仍走 system stack；此處 CSP 只是恰好把結果鎖成一致。

| 角色 | 字族 | 規格 | 用途 |
|---|---|---|---|
| **Display** | sans | `clamp(30px,6vw,44px)`、w800、`ls:-.03em`、`--accent` | 只有 `.brand` 一處 |
| **Heading** | sans | `clamp(19px,3vw,23px)`、w750、`-.01em`、`text-wrap:balance` | 區塊標題；掛 `.sub`（w450、muted、`.72em`）當副標 |
| **Body** | sans | `clamp(15px,2.4vw,17px)`、`lh:1.6`、`max-width:60ch` | 敘述；`<b>` 用 `--accent-deep`＋w650 |
| **Utility** | mono | 10.5–12.5px、w600–700、`ls:.05–.14em`、常 `uppercase` | eyebrow、狀態 chip、實體 chip、數據、路徑、run block |

**mono 鐵律**：只給「非散文」的機讀資訊——標籤/eyebrow/實體名/數字/路徑/指令。散文一律 sans。
→ 字族分工本身就在說「這是**資料** vs 這是**說明**」，省掉額外顏色標記。標題走**緊** tracking（負字距）＋重 weight 收成塊；utility 走**寬** tracking＋大寫散成標籤。

## Radius 與間距尺度

**Radius 依元件大小分級遞減**（避免小標籤配大圓角的塑膠感）：

- `--radius:14px` 最外層容器（service 框/node/大 layer）→ `--radius-sm:9px` 中層（layer/phase/legend）→ `8px` cell → `6px` chip → `5px` `.ent` 實體標籤 → `999px` pill（`.stat`／`.hbadge`）。

版面：

- **容器** `max-width:920px` 置中，padding 用 `clamp(20px,4vw,52px)` 流體。
- **節奏** `section{margin-top:40px}`；其餘間距**一律 gap-based**（flex/grid `gap`），不用 margin 疊加。
- **常見 grid** `1fr 1fr` gap 8–14px；橫向流程用 `repeat(N,1fr)`；phase 用 `auto auto 1fr`。
- **數據對齊** 靠 mono 天生等寬，達成類 `tabular-nums` 整齊感。
- **響應式** 單一斷點 `@media (max-width:640px)`，把所有兩欄 grid 塌成 `1fr`、橫向流程收成 2 欄。

---

## 版面元件詞彙

分兩層，**這是本規格最容易被誤用的地方**：

- **基元（primitives）** — 任何結構圖都會用到的可重用積木，已去專案化（拿掉具體 test count、公司系統名、帳密），**預設就用這些**。
- **可選敘事裝置（narrative devices）** — 只在**內容本身真的有**單一核心／真實循環／需展示指令時才畫，否則**一律不畫**。它們是「那張圖剛好長這樣」的家具，不是通用詞彙。

### A. 基元（恆用、去專案化）

- **`.legend` 圖例解碼帶** → 三種狀態色塊的白話定義。`flex-wrap` 於 `--surface-2` 帶內，每項＝一個 chip＋一句話。**放在圖之前**，是後面「色塊編碼」能被解讀的前提。
- **`.service` 服務容器＋`.slabel` 層標** → 把系統邊界圈成一框。`1.5px solid --border-strong`＋`linear-gradient(180deg,surface-2,surface)` 微漸層做實體感；`.slabel` 用 mono 大寫＋`::after` 拉一條到底細線，像技術示意圖分區。
- **`.layer`＋`.ltag` 子層** → service 內分層（如 SPA/後端/DB）。surface 卡；`.ltag` 用 mono＋accent 當層名；可 inline 覆寫 border/ltag 顏色標整層狀態（例：已完成層改 ok 綠）。
- **`.node`／`.lstat` 角色節點** → 參與者/入口/子系統。狀態靠 `border-left:3px solid` 換色（done=ok / plan=dashed border-strong / ref=ref），**左邊條是唯一狀態訊號源**。內容用**中性佔位**（角色名／模組名），別寫死具體人名或專案專屬系統。
- **`.chip` 狀態徽章** → 標題列的狀態標籤。mono 11px、`radius:6px`、**符號＋文字**（✓/◻/⇗）；done=ok-soft 底＋ok 字、plan=transparent＋dashed、ref=ref-soft/ref。
- **`.grid2`＋`.cell`＋`.tick` 功能格** → 層內逐項功能。2 欄 grid；`.cell.done`=ok-soft 底＋透明邊、`.cell.plan`=transparent＋dashed；`.tick` 16px 圓打勾，plan 態設 transparent 只留虛線圈。
- **`.sideref` 框外外部系統** → 第三方 API／既有系統等**外部真相**。放在 `.service` **收框之後**的獨立 grid，用 ref 灰左條＋⇗ chip。**物理位置在框外＝架構語意「引用非內建」**——這條規則本身是可重用的，但**內容填中性佔位（「外部系統 A／B」），別寫死特定廠商名**。
- **`.connector` 流向箭頭** → 純文字 ▼／→ 於 faint 色；`.split` 用 grid 對齊上方兩欄分別下箭。

### B. 可選敘事裝置（僅內容真有核心/循環/指令時才用，否則不畫）

> **判斷準則**：問「拿掉它，圖還讀得懂嗎？」——若答「讀得懂」，就別加。這些裝置每多用一個，圖就更像 living-WBS 圖的複製品。**全圖至多用一個**。

- **`.heart` 心臟強調列** → **僅當內容真的有「唯一一個」核心元件**時，把它從清單拔高。`grid-column:1/-1` 跨滿排＋`linear-gradient(100deg,accent-soft,surface-2)`＋accent 實線邊＋左掛 pill badge（★）＋可選右掛 mono 數據。**全圖只准一處**用這五重手法；沒有明確唯一核心就**不要用**，右側數據若無真實數字就留空。
- **`.loop`＋`.flowarrow` 循環流程帶** → **僅當流程真的是「回到起點」的循環**時才用（否則用 `.connector` 直線就好）。`repeat(N,1fr)` 無縫格（**N＝實際步數，不是固定 4**）＋`border-right` 分隔；`.flowarrow` 用 `position:absolute;right:-9px`＋底色 `--bg` 挖出圓形箭頭疊格縫；每格底可掛 `.ent` 實體標籤。
- **`.run` 指令區塊** → **僅當要展示可複製的指令/路徑**時才用。mono code block（surface-2 底），`.k` 用 accent 標關鍵片段。**內容用中性佔位（指令、路徑），絕不放真實帳密／密鑰**。
- **`.ecg` 心跳線母題** → **綁死「living=心跳」這個產品隱喻**，只有隱喻**真的貼合當前產品**時才用；資料模型圖、一般流程圖**不要用**。內聯 SVG 折線＋`.beat` 圓點沿 `offset-path` 跑；必須包 `@media (prefers-reduced-motion:no-preference)` 守門，減動偏好者不播。動態是點題不是炫技。
- **`.phases`＋`.phase` 有序路線圖** → **僅用於「有序列／相依關係」的建置路線圖（結構性）**，例如里程碑先後、相依前置。`grid auto auto 1fr`（編號｜狀態圓｜內文）；`border-left:4px solid ok`，未達成改 dashed＋surface-2 底；`.pstat` 填色打勾 vs 虛線空圈。**這不是狀態儀表板**——純進度百分比/完成率速覽屬「摘要」，走純文字（見下 C）。
- **`.footcards`＋`.fcard`＋`.run` 收尾卡** → 兩欄總結卡（如「已具備 vs 下一步」）。`h3::before` 小圓點分色；內含 `.run` 者遵守上面 `.run` 規則。內容真有兩組對照才用。

### C. 明確排除（不做成圖 → 一律純文字）

以下**即使那張來源圖有現成元件也不畫**，直接違反 `visualization-scope` memory：

- **`.metastrip`／`.stat` metrics 速覽**（commits 數、測試數、完成率等）→ 這是 memory 定義的「摘要」，**純文字**。純數字儀表板不是結構圖。
- **待拍板決策清單、審查結果摘要、選項比較** → 純文字（memory 正因決策清單被做成 Artifact 遭打回而立）。
- 拿不準是「結構／關係／地圖」還是「清單／摘要」時 → **純文字**。

---

## 設計原則（照抄，別自訂）

- **狀態＝色塊編碼，且先給 legend 解碼** → 三態（已建 ok 綠實線／規劃中 border-strong 灰虛線／引用 ref 灰）在 chip/cell/node 左條/phase 左條**反覆一致**；圖之前先放 `.legend` 白話定義。
- **虛線 vs 實線＝未完成 vs 完成** → `border-left-style:dashed`＋透明 tick/空心圈＝計畫中，實線＋填色打勾＝已驗證。狀態不靠額外圖示，靠邊框樣式本身。
- **重點至多給一個心臟** → 若用 `.heart`，全圖只有一列用滿五重手法拔高，其餘一律**克制**；沒有明確唯一核心就別用。視覺重量集中一處，讀者一眼知道核心是誰。
- **外部系統畫在框外** → 用物理位置（框內/框外）表達「內建 vs 外部真相」，而非只靠文字。
- **mono 專責機讀資訊** → 等寬字只給標籤/數字/路徑/指令，散文一律 sans。
- **雙主題同等用心** → light 當預設 → `prefers-color-scheme` 順應系統 → `[data-theme]` 手動雙向覆蓋；dark/light 各自完整重列 token。
- **語意色成對** → 每個語意色配一個低飽和 `-soft` 底；dark 主題把 soft 底改成**極深同色調**而非直接反相。

### 刻意避開的 AI 味（反面清單）

- **中性階必帶刻意色偏，禁純灰** → neutrals 都調過冷藍紫偏（`#F5F6FB`／`#181B27`），不是 `#888`/`#ccc` 純中性灰。擴充新增中性色時沿用此色偏。
- **字體不預設 AI 慣用體** → 不用 Inter／Space Grotesk 這類 AI 簡報體，一律 system stack（此處也被 CSP 強制，結果一致）。
- **不置中一切** → 敘述左對齊、`max-width:60ch`／`920px` 容器成欄，而非每段 `text-align:center` 的簡報感。
- **克制圓角** → 14/9/8/6/5px 依大小遞減，最小元素最小圓角；沒有全域大圓角糖果感。
- **單一靛藍 accent** → 不做紫藍漸層 hero；漸層只用在 service/heart 的低對比 180deg 微提亮做實體感，不做大面積彩色 banner。
- **陰影極淡、元件極小** → 大 blur、低 alpha、`-12px` 負 spread 只在底緣露出；tick/badge/狀態燈 7–16px。資訊密度優先於裝飾。
- **無 emoji 濫用** → 符號限 ✓◻⇗★ 的功能性使用，不當裝飾。
- **不照抄敘事家具** → 心跳線/心臟列/循環帶只在內容真有心跳/核心/循環時才畫（見「可選敘事裝置」判斷準則），否則每張圖都變成 living-WBS 圖的翻版——那正是 AI 味。

## 最小起手骨架（可直接貼上擴充；兩個 `[data-theme]` 已填滿，貼上即可雙向切換）

```html
<title>{系統名} · {圖種}</title>   <!-- 必改：填實際系統名與圖種，勿沿用來源產品名 -->
<style>
  /* ── 1. 三段式雙主題 token（三處色彩 token 必須各自完整，勿留空） ── */
  :root{
    --bg:#F5F6FB; --surface:#FFF; --surface-2:#FAFBFF;
    --border:#E4E7F1; --border-strong:#CBD1E2;
    --ink:#181B27; --muted:#5A6175; --faint:#8A91A5;
    --accent:#4F46E5; --accent-deep:#4338CA; --accent-soft:#EEF0FE;
    --ok:#0DA36C; --ok-soft:#E2F5EC; --ref:#7B8296; --ref-soft:#EEF0F5;
    --radius:14px; --radius-sm:9px;
    --shadow:0 1px 2px rgba(24,27,39,.04),0 8px 24px -12px rgba(24,27,39,.14);
    --sans:-apple-system,"Segoe UI Variable Text","Segoe UI",system-ui,"Noto Sans TC",sans-serif;
    --mono:ui-monospace,"Cascadia Code","SF Mono",Consolas,monospace;
  }
  @media (prefers-color-scheme:dark){:root{
    --bg:#0C0E15; --surface:#151824; --surface-2:#11131D;
    --border:#262B3B; --border-strong:#3A425C;
    --ink:#E9EBF4; --muted:#9CA3B8; --faint:#6D7488;
    --accent:#8983F2; --accent-deep:#A29BFF; --accent-soft:#20233B;
    --ok:#3DD892; --ok-soft:#123227; --ref:#8C93A8; --ref-soft:#20242F;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 28px -12px rgba(0,0,0,.6);
  }}
  /* 手動切換：靠特異度勝過 media query，兩塊都須完整重列色彩 token（不可留空註解） */
  :root[data-theme="dark"]{
    --bg:#0C0E15; --surface:#151824; --surface-2:#11131D;
    --border:#262B3B; --border-strong:#3A425C;
    --ink:#E9EBF4; --muted:#9CA3B8; --faint:#6D7488;
    --accent:#8983F2; --accent-deep:#A29BFF; --accent-soft:#20233B;
    --ok:#3DD892; --ok-soft:#123227; --ref:#8C93A8; --ref-soft:#20242F;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 28px -12px rgba(0,0,0,.6);
  }
  :root[data-theme="light"]{
    --bg:#F5F6FB; --surface:#FFF; --surface-2:#FAFBFF;
    --border:#E4E7F1; --border-strong:#CBD1E2;
    --ink:#181B27; --muted:#5A6175; --faint:#8A91A5;
    --accent:#4F46E5; --accent-deep:#4338CA; --accent-soft:#EEF0FE;
    --ok:#0DA36C; --ok-soft:#E2F5EC; --ref:#7B8296; --ref-soft:#EEF0F5;
    --shadow:0 1px 2px rgba(24,27,39,.04),0 8px 24px -12px rgba(24,27,39,.14);
  }

  body{background:var(--bg);color:var(--ink);font-family:var(--sans);
    line-height:1.6;margin:0;}
  .wrap{max-width:920px;margin:0 auto;padding:clamp(20px,4vw,52px);}
  section{margin-top:40px;}

  /* ── 2. legend：色塊解碼帶（放在圖之前） ── */
  .legend{display:flex;flex-wrap:wrap;gap:12px;background:var(--surface-2);
    border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 16px;}
  .lg{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);}
  .chip{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.06em;
    text-transform:uppercase;border-radius:6px;padding:2px 8px;}
  .chip.done{background:var(--ok-soft);color:var(--ok);}
  .chip.plan{background:transparent;color:var(--muted);
    border:1px dashed var(--border-strong);}

  /* ── 3. node：狀態靠 border-left 換色（唯一訊號源） ── */
  .node{background:var(--surface);box-shadow:var(--shadow);border-radius:var(--radius);
    padding:14px 18px;border-left:3px solid var(--border-strong);}
  .node.done{border-left-color:var(--ok);}
  .node.plan{border-left-color:var(--border-strong);border-left-style:dashed;}
</style>

<div class="wrap">
  <div class="legend">
    <span class="lg"><span class="chip done">✓ 已建</span>完成並驗證</span>
    <span class="lg"><span class="chip plan">◻ 規劃中</span>尚未實作</span>
  </div>
  <section>
    <!-- 中性佔位，實際內容自填 -->
    <div class="node done">模組 A · 已驗證</div>
  </section>
</div>
```
