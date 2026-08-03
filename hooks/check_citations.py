# -*- coding: utf-8 -*-
"""PostToolUse(Write|Edit)：交付物裡引用了沒開過的檔案就回報。

存在的理由是一個重複發作的失誤：把 subagent 或舊報告講的 `檔案:行號` 當成
事實照抄，實際上那個路徑根本不存在，或存在但我沒開過。規則寫在 CLAUDE.md
裡擋不住（靠自律），寫成 hook 才擋得住（靠執行）。

只檢查 .md／.html——那是交出去給人看的東西。程式碼註解裡出現行號是正常的，
不該被吵。這也代表聊天訊息裡的引用檢查不到，那是已知缺口。
"""
import io
import json
import os
import re
import sys

STATE_DIR = os.path.expanduser("~/.claude/hook-state")
DELIVERABLE_EXT = (".md", ".html")

# 要有副檔名才算引用，否則 "10:30" 這種時間、"localhost:8000" 都會中。
# 副檔名必須「以字母開頭」：否則 127.0.0.1:8000 會被拆成 "127.0.0" + ".1"
# 當成檔案（第一次實戰就誤判了這個）。
CITATION = re.compile(r"([A-Za-z0-9_./\\-]+\.[A-Za-z][A-Za-z0-9]{0,9}):(\d+)")
URL = re.compile(r"https?://\S+")
# 沒有斜線又以常見 TLD 結尾的，是網域不是檔案（example.com:443）。
HOSTLIKE = re.compile(
    r"^[^/\\]+\.(com|net|org|io|dev|app|cc|tw|co|ai|me|sh|xyz|test|local)$", re.I
)


def norm(p):
    return os.path.normpath(p).replace("\\", "/").lower()


def known_paths(session):
    state = os.path.join(STATE_DIR, "%s.reads.txt" % session)
    if not os.path.exists(state):
        return set()
    with io.open(state, encoding="utf-8") as fh:
        return {norm(ln.strip()) for ln in fh if ln.strip()}


def written_text(payload):
    ti = payload.get("tool_input") or {}
    # Write 給 content，Edit 給 new_string——欄位名不同，實測確認過
    return ti.get("content") or ti.get("new_string") or ""


def resolve(cited, cwd):
    """引用可能是相對於 cwd、也可能是絕對路徑。回傳絕對路徑（若能定位）。"""
    if os.path.isabs(cited):
        return cited
    return os.path.join(cwd, cited)


def main():
    payload = json.loads(sys.stdin.read())
    target = (payload.get("tool_input") or {}).get("file_path") or ""
    if not target.lower().endswith(DELIVERABLE_EXT):
        return

    text = written_text(payload)
    if not text:
        return

    session = payload.get("session_id") or "unknown"
    cwd = payload.get("cwd") or os.getcwd()
    known = known_paths(session)

    missing, unread = [], []
    seen = set()
    for cited, _line in CITATION.findall(URL.sub("", text)):
        if cited in seen or HOSTLIKE.match(cited):
            continue
        seen.add(cited)
        n = norm(cited)
        # 尾綴比對：引用多半是 repo 相對路徑，紀錄裡是絕對路徑
        if any(k == n or k.endswith("/" + n) for k in known):
            continue
        if not os.path.exists(resolve(cited, cwd)):
            missing.append(cited)
        else:
            unread.append(cited)

    if not missing and not unread:
        return

    parts = []
    if missing:
        parts.append(
            "cited but no such file exists: " + ", ".join(sorted(missing)[:8])
        )
    if unread:
        parts.append(
            "cited but never opened in this session: " + ", ".join(sorted(unread)[:8])
        )
    detail = "; ".join(parts)

    out = {
        "systemMessage": "引用檢查：%s" % detail,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "Citation check on %s. %s. "
                "These citations were not verified against the files in this session."
                % (os.path.basename(target), detail)
            ),
        },
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


try:
    main()
except Exception:
    # 檢查失敗絕不能擋工作——這是護欄，不是關卡
    pass
sys.exit(0)
