# Claude portable profile

這個 repository 是大姊的跨電腦全域 Claude profile。Dropbox 保存可攜來源；`bootstrap.py` 把明確受管理的檔案連到本機 `~/.claude`，並只合併它負責的 `settings.json` 欄位。

## 管理邊界

版本控制內：

- 全域 `CLAUDE.md`、status line；
- local custom skills：`fp`、`notebooklm`、`verify`；
- `agents/*.md`；
- citation hooks 與 bootstrap/tests；
- skills/plugins inventory 與研究紀錄。

本機保留、不進版本控制：登入、token、credentials、sessions、history、cache、完整 `settings.json`。SecondBrain 的目錄授權與 inbox lifecycle hook 屬專案設定，不由全域 profile 注入。

## 新電腦啟用

1. 安裝 Git、Python 3.11+、Dropbox 與 Claude Code，完成各產品登入。
2. 等待 `00.claudedotfile` 完整同步。
3. 在 repository 根目錄先預覽：

   ```powershell
   python bootstrap.py --dry-run
   ```

4. 檢查每個 `PLAN` 後套用；既有受管理路徑與設定會先備份：

   ```powershell
   python bootstrap.py --apply
   ```

5. 以唯讀驗證確認所有 link 與 managed settings 收斂：

   ```powershell
   python bootstrap.py --verify
   ```

6. 依 [skill_index.md](skill_index.md) 手動安裝或登入 marketplace plugins。Plugin 本體不由 bootstrap 複製。

不帶 mode 時，bootstrap 只顯示說明並以非零結束，不會變更檔案。`--dry-run` 不建立目錄或備份。`--apply` 會輸出 `BACKUP_ROOT=<path>`；再次執行若已收斂則輸出 `BACKUP_ROOT=none` 與 `UNCHANGED`。

## 維護與驗證

```powershell
python -m unittest discover -s tests -v
python hooks/_selftest.py
python -m py_compile bootstrap.py hooks/log_read.py hooks/check_citations.py
git diff --check
```

修改 skill 時，同步更新 `skill_index.md` 與其契約測試。修改 bootstrap 時，必須保留 dry-run 不變性、備份、rollback、idempotence、錯誤 link 診斷及 unmanaged settings preservation。
