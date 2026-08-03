# -*- coding: utf-8 -*-
"""PostToolUse(Read|Write|Edit)：記下這個 session 真的碰過哪些檔。

為什麼要自己記而不解析 transcript：官方文件明寫 transcript 是非同步寫入、
「may lag the in-memory conversation」，同一輪剛做的 Read 可能還沒 flush，
拿它比對會產生假警報——明明讀過卻被判沒讀過。自維護狀態檔沒有這個問題。

Read／Write／Edit 都算「我知道這個檔的內容」：Read 是讀過，Write 是我寫的，
Edit 的前提本來就是先讀過。
"""
import io
import json
import os
import sys
import time

STATE_DIR = os.path.expanduser("~/.claude/hook-state")
PRUNE_AFTER_DAYS = 7


def prune(now):
    """順手清掉過期的 session 狀態檔，免得這個目錄無限長大。"""
    cutoff = now - PRUNE_AFTER_DAYS * 86400
    try:
        for name in os.listdir(STATE_DIR):
            if not name.endswith(".reads.txt"):
                continue
            path = os.path.join(STATE_DIR, name)
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
    except Exception:
        pass


def main():
    payload = json.loads(sys.stdin.read())
    session = payload.get("session_id") or "unknown"
    path = (payload.get("tool_input") or {}).get("file_path")
    if not path:
        return

    os.makedirs(STATE_DIR, exist_ok=True)
    state = os.path.join(STATE_DIR, "%s.reads.txt" % session)
    with io.open(state, "a", encoding="utf-8") as fh:
        fh.write(os.path.normpath(path).replace("\\", "/") + "\n")

    # 一天最多清一次就夠，用狀態檔自己的行數當粗略節流
    if int(time.time()) % 97 == 0:
        prune(time.time())


try:
    main()
except Exception:
    # 記錄失敗絕不能擋工作：寧可漏記一筆，也不要讓 hook 變成障礙
    pass
sys.exit(0)
