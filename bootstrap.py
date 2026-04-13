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

# Add more symlinks here as needed
# (target_in_dropbox, link_in_system)
SYMLINKS = [
    (DROPBOX / ".claude" / "CLAUDE.md", HOME / ".claude" / "CLAUDE.md"),
    # Global skills — uncomment when skills are added to dotfiles
    # (DROPBOX / ".claude" / "skills" / "fp", HOME / ".claude" / "skills" / "fp"),
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
    verify_symlinks()
