#!/usr/bin/env python3
"""
New machine bootstrap script.
Creates symlinks from ~/.claude/ to Dropbox-synced dotfiles.

Usage:
    python bootstrap.py
"""
import os
import sys
import pathlib

USERNAME = os.environ.get("USERNAME") or os.environ.get("USER")
HOME = pathlib.Path.home()
DROPBOX = HOME / "Dropbox" / "00.claudedotfile"

SYMLINKS = [
    (DROPBOX / ".claude" / "CLAUDE.md", HOME / ".claude" / "CLAUDE.md"),
]


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


if __name__ == "__main__":
    print(f"Bootstrap dotfiles for: {USERNAME}\n")
    for target, link in SYMLINKS:
        create_symlink(target, link)
    print("\nDone.")
