#!/usr/bin/env python3
"""
New machine bootstrap script.
Creates symlinks from ~/.claude/ to Dropbox-synced dotfiles,
and patches ~/.claude/settings.json with machine-specific paths.

== 換新機器的初始化步驟 ==

1. 安裝 Node.js（https://nodejs.org）
2. 安裝 Claude Code：
       npm install -g @anthropic-ai/claude-code
3. 登入：
       claude
   （首次啟動會要求登入 Anthropic 帳號）
4. 確認 Dropbox 已同步完成
5. 執行此腳本：
       cd ~/Dropbox/00.claudedotfile
       python bootstrap.py

完成後所有 symlink、settings、agents、skills 全部就位。

Usage:
    python bootstrap.py
"""
import json
import os
import sys
import pathlib
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

USERNAME = os.environ.get("USERNAME") or os.environ.get("USER")
HOME = pathlib.Path.home()
DROPBOX = HOME / "Dropbox" / "00.claudedotfile"

# (target_in_dropbox, link_in_system)
# 根據 skill_index.md 記錄的 skills 進行 symlink
# 僅包含 LOCAL CUSTOM SKILLS；官方 plugin skills 通過 marketplace 管理
SYMLINKS = [
    (DROPBOX / ".claude" / "CLAUDE.md",                HOME / ".claude" / "CLAUDE.md"),
    (DROPBOX / "statusline.sh",                         HOME / ".claude" / "statusline.sh"),
    (DROPBOX / ".claude" / "skills" / "fp",             HOME / ".claude" / "skills" / "fp"),
    (DROPBOX / ".claude" / "skills" / "wiki-note",      HOME / ".claude" / "skills" / "wiki-note"),
    (DROPBOX / ".claude" / "skills" / "wiki-query",     HOME / ".claude" / "skills" / "wiki-query"),
    (DROPBOX / ".claude" / "skills" / "notebooklm",     HOME / ".claude" / "skills" / "notebooklm"),
]

# Agents directory: sync all .md files from dotfiles/agents/ → ~/.claude/agents/
AGENTS_SRC = DROPBOX / "agents"
AGENTS_DST = HOME / ".claude" / "agents"

# Patch these keys into ~/.claude/settings.json using resolved local paths.
# Values are callables so they're evaluated at runtime on each machine.
def _statusline_value():
    path = str(HOME / ".claude" / "statusline.sh").replace("\\", "/")
    return {"type": "command", "command": f"bash '{path}'"}

# Top-level key patches
SETTINGS_PATCHES = {
    "statusLine": _statusline_value,
}

# Nested key patches: tuple of keys → callable returning value
def _additional_dirs_value():
    secondbrain = str(HOME / "Dropbox" / "00.SecondBrain")
    claudedotfile = str(HOME / "Dropbox" / "00.claudedotfile")
    return [secondbrain, claudedotfile]

def _session_start_hook_value():
    script = str(HOME / "Dropbox" / "00.SecondBrain" / "scripts" / "check_inbox.py").replace("\\", "/")
    return [{"hooks": [{"type": "command", "command": f'python "{script}"'}]}]

NESTED_PATCHES = {
    ("permissions", "additionalDirectories"): _additional_dirs_value,
    ("hooks", "SessionStart"):                _session_start_hook_value,
}


def create_symlink(target: pathlib.Path, link: pathlib.Path) -> None:
    if not target.exists():
        print(f"✗ Target not found: {target}")
        sys.exit(1)

    if link.exists() or link.is_symlink():
        print(f"  Already exists, skipping: {link}")
        return

    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(str(target), str(link))
    print(f"✓ {link} → {target}")


def patch_settings() -> None:
    settings_path = HOME / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if settings_path.exists():
        with open(settings_path, encoding="utf-8") as f:
            data = json.load(f)

    changed = False
    for key, value_fn in SETTINGS_PATCHES.items():
        value = value_fn()
        if data.get(key) != value:
            data[key] = value
            print(f"✓ settings.json: {key} = {value}")
            changed = True
        else:
            print(f"  Already set, skipping: {key}")

    for keys, value_fn in NESTED_PATCHES.items():
        value = value_fn()
        parent = data
        for k in keys[:-1]:
            parent = parent.setdefault(k, {})
        last = keys[-1]
        if parent.get(last) != value:
            parent[last] = value
            print(f"✓ settings.json: {'.'.join(keys)} updated")
            changed = True
        else:
            print(f"  Already set, skipping: {'.'.join(keys)}")

    if changed:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


def sync_agents() -> None:
    """Symlink every .md file in dotfiles/agents/ into ~/.claude/agents/."""
    if not AGENTS_SRC.exists():
        print("  agents/ directory not found in dotfiles, skipping.")
        return

    AGENTS_DST.mkdir(parents=True, exist_ok=True)
    for agent_file in sorted(AGENTS_SRC.glob("*.md")):
        dst = AGENTS_DST / agent_file.name
        if dst.is_symlink() and dst.resolve() == agent_file.resolve():
            print(f"  Already linked, skipping: {agent_file.name}")
        elif dst.exists():
            print(f"  ✗ {agent_file.name} exists but is NOT a symlink — skipping")
        else:
            os.symlink(str(agent_file), str(dst))
            print(f"✓ ~/.claude/agents/{agent_file.name} → {agent_file}")


def verify_symlinks() -> None:
    print("\nVerifying symlinks:")
    all_ok = True
    for target, link in SYMLINKS:
        if link.is_symlink() and link.resolve() == target.resolve():
            print(f"  ✓ {link.name} → {target}")
        elif link.exists():
            print(f"  ✗ {link.name} exists but is NOT a symlink")
            all_ok = False
        else:
            print(f"  ✗ {link.name} missing")
            all_ok = False

    if all_ok:
        print("\nAll good.")
    else:
        print("\nSome symlinks are broken. Re-run bootstrap.")


def print_manual_steps() -> None:
    """提示需要手動執行的步驟（官方 plugin 等）。"""
    print("\n📋 Manual Steps Required:\n")
    print("1. Enable superpowers plugin:")
    print("   - Open Claude Code settings")
    print("   - Search for 'superpowers' in Extensions/Plugins")
    print("   - Enable 'superpowers@claude-plugins-official'")
    print("\n2. Verify skill_index.md for latest skills list")
    print("   📄 See: claudedotfile/skill_index.md\n")


if __name__ == "__main__":
    print(f"Bootstrap dotfiles for: {USERNAME}\n")
    for target, link in SYMLINKS:
        create_symlink(target, link)
    print("\nSyncing agents:")
    sync_agents()
    print("\nPatching settings:")
    patch_settings()
    verify_symlinks()
    print_manual_steps()
