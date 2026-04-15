#!/usr/bin/env python3
"""
New machine bootstrap script.
Creates symlinks from ~/.claude/ to Dropbox-synced dotfiles,
and patches ~/.claude/settings.json with machine-specific paths.

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
SYMLINKS = [
    (DROPBOX / ".claude" / "CLAUDE.md",   HOME / ".claude" / "CLAUDE.md"),
    (DROPBOX / "statusline.sh",            HOME / ".claude" / "statusline.sh"),
    # Global skills — uncomment when skills are added to dotfiles
    # (DROPBOX / ".claude" / "skills" / "fp", HOME / ".claude" / "skills" / "fp"),
]

# Patch these keys into ~/.claude/settings.json using resolved local paths.
# Values are callables so they're evaluated at runtime on each machine.
def _statusline_value():
    path = str(HOME / ".claude" / "statusline.sh").replace("\\", "/")
    return {"type": "command", "command": f"bash '{path}'"}

SETTINGS_PATCHES = {
    "statusLine": _statusline_value,
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

    if changed:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


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


if __name__ == "__main__":
    print(f"Bootstrap dotfiles for: {USERNAME}\n")
    for target, link in SYMLINKS:
        create_symlink(target, link)
    print("\nPatching settings:")
    patch_settings()
    verify_symlinks()
