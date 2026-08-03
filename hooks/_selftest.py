# -*- coding: utf-8 -*-
"""兩支 hook 腳本的自我測試。用 subprocess 餵真的 stdin，驗真的行為。

跑法：cd 到本目錄，python _selftest.py
"""
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.expanduser("~/.claude/hook-state")
SID = "selftest-session"
STATE = os.path.join(STATE_DIR, "%s.reads.txt" % SID)

REPO = r"C:\Users\wind.kuo\Dropbox\00.AI Projects\pulse"
READ_ME = os.path.join(REPO, r"frontend\src\components\ball-panel.tsx")

fails = []


def run(script, payload):
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, script)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  -> " + detail) if detail and not cond else ""))
    if not cond:
        fails.append(name)


if os.path.exists(STATE):
    os.remove(STATE)

print("1) log_read 記下 Read 過的檔")
rc, out, err = run("log_read.py", {
    "session_id": SID, "tool_name": "Read", "tool_input": {"file_path": READ_ME},
})
check("exit 0", rc == 0, "rc=%s stderr=%s" % (rc, err[:300]))
check("狀態檔存在", os.path.exists(STATE), "expected %s" % STATE)
if os.path.exists(STATE):
    body = io.open(STATE, encoding="utf-8").read()
    check("內容含 ball-panel.tsx", "ball-panel.tsx" in body, repr(body[:200]))

print("2) check_citations 分辨三種引用")
content = (
    "verified: frontend/src/components/ball-panel.tsx:44 \n"
    "unread:   frontend/src/lib/format.ts:30 \n"
    "missing:  backend/app/routers/asks.py:372 \n"
    "url 不該中: https://example.com/a.js:9 \n"
    "時間不該中: 10:30 \n"
    "IP 不該中:  127.0.0.1:8000 \n"
    "網域不該中: panpapa.cc:443 example.com:8080 \n"
)
rc, out, err = run("check_citations.py", {
    "session_id": SID, "cwd": REPO, "tool_name": "Write",
    "tool_input": {"file_path": "C:/tmp/report.md", "content": content},
})
check("exit 0", rc == 0, "rc=%s stderr=%s" % (rc, err[:300]))
check("有輸出 JSON", out.strip().startswith("{"), repr(out[:300]))
if out.strip().startswith("{"):
    o = json.loads(out)
    ctx = o["hookSpecificOutput"]["additionalContext"]
    print("     ctx: " + ctx)
    check("讀過的沒被誤報", "ball-panel.tsx" not in ctx, ctx)
    check("沒讀過的有報", "format.ts" in ctx, ctx)
    check("不存在的有報且歸類正確", "no such file" in ctx and "asks.py" in ctx, ctx)
    check("URL 沒被誤抓", "example.com" not in ctx and "a.js" not in ctx, ctx)
    check("時間沒被誤抓", "10:30" not in ctx, ctx)
    # 第一次實戰就誤判 127.0.0.1:8000（"127.0.0" + ".1" 剛好像檔名加副檔名）
    check("IP 沒被誤抓", "127.0.0" not in ctx, ctx)
    check("網域沒被誤抓", "panpapa" not in ctx and "example.com" not in ctx, ctx)
    check("有給使用者的訊息", o.get("systemMessage", "").startswith("引用檢查"), repr(o.get("systemMessage")))

print("3) Edit 走 new_string 欄位（跟 Write 的 content 不同名）")
rc, out, err = run("check_citations.py", {
    "session_id": SID, "cwd": REPO, "tool_name": "Edit",
    "tool_input": {
        "file_path": "C:/tmp/report.md",
        "old_string": "x", "new_string": "see backend/app/routers/asks.py:372", "replace_all": False,
    },
})
check("Edit 也會檢查", "asks.py" in out, repr(out[:300]))

print("4) 非交付物（.tsx）不吵")
rc, out, err = run("check_citations.py", {
    "session_id": SID, "cwd": REPO, "tool_name": "Write",
    "tool_input": {"file_path": "C:/tmp/thing.tsx", "content": "// see backend/app/routers/asks.py:372"},
})
check("原始碼不觸發", out.strip() == "", repr(out[:200]))

print("5) 全部都讀過時保持安靜")
rc, out, err = run("check_citations.py", {
    "session_id": SID, "cwd": REPO, "tool_name": "Write",
    "tool_input": {"file_path": "C:/tmp/report.md",
                   "content": "only frontend/src/components/ball-panel.tsx:44"},
})
check("零誤報時無輸出", out.strip() == "", repr(out[:200]))

print("6) 壞輸入不炸、不擋事")
for bad in (b"", b"not json", b'{"tool_input":null}'):
    p = subprocess.run([sys.executable, os.path.join(HERE, "check_citations.py")],
                       input=bad, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check("壞輸入 %r 仍 exit 0" % bad[:12], p.returncode == 0, "rc=%s" % p.returncode)

print("")
print("FAILED: %d" % len(fails))
for f in fails:
    print("  - " + f)
sys.exit(1 if fails else 0)
