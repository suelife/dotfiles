#!/usr/bin/env python3
"""Converge a Claude home onto this portable profile."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any


MANAGED_SKILLS = ("fp", "notebooklm", "verify")
FORBIDDEN_PORTABLE_PATHS = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/auth.json",
    ".claude/credentials.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converge ~/.claude onto a portable profile safely."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--profile-root",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--home", type=Path, default=Path.home())
    return parser.parse_args()


def link_map(profile_root: Path, home: Path) -> list[tuple[Path, Path]]:
    claude_home = home / ".claude"
    mappings = [
        (profile_root / ".claude/CLAUDE.md", claude_home / "CLAUDE.md"),
        (profile_root / "statusline.sh", claude_home / "statusline.sh"),
    ]
    mappings.extend(
        (
            profile_root / f".claude/skills/{skill}",
            claude_home / f"skills/{skill}",
        )
        for skill in MANAGED_SKILLS
    )
    mappings.extend(
        (agent, claude_home / "agents" / agent.name)
        for agent in sorted((profile_root / "agents").glob("*.md"))
    )
    return mappings


def normalized_path(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value)))


def managed_post_hooks(profile_root: Path) -> list[dict[str, Any]]:
    log_read = str(profile_root / "hooks/log_read.py")
    check_citations = str(profile_root / "hooks/check_citations.py")
    return [
        {
            "matcher": "Read|Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": "python",
                    "args": [log_read],
                    "timeout": 10,
                }
            ],
        },
        {
            "matcher": "Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": "python",
                    "args": [check_citations],
                    "timeout": 15,
                    "statusMessage": "檢查引用",
                }
            ],
        },
    ]


def merged_settings(
    current: dict[str, Any], profile_root: Path, home: Path
) -> dict[str, Any]:
    result = deepcopy(current)
    statusline = str(home / ".claude/statusline.sh").replace("\\", "/")
    result["statusLine"] = {
        "type": "command",
        "command": f"bash '{statusline}'",
    }

    permissions = result.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise ValueError("settings.json permissions must be an object")
    additional = permissions.get("additionalDirectories", [])
    if not isinstance(additional, list):
        raise ValueError("settings.json permissions.additionalDirectories must be a list")
    managed_dirs = {
        normalized_path(home / "Dropbox/00.SecondBrain"),
        normalized_path(profile_root),
    }
    permissions["additionalDirectories"] = [
        value
        for value in additional
        if not isinstance(value, str) or normalized_path(value) not in managed_dirs
    ]

    hooks = result.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("settings.json hooks must be an object")
    session_start = hooks.get("SessionStart", [])
    if not isinstance(session_start, list):
        raise ValueError("settings.json hooks.SessionStart must be a list")
    hooks["SessionStart"] = [
        hook
        for hook in session_start
        if "check_inbox.py" not in json.dumps(hook, ensure_ascii=False)
    ]

    post_tool_use = hooks.get("PostToolUse", [])
    if not isinstance(post_tool_use, list):
        raise ValueError("settings.json hooks.PostToolUse must be a list")
    unmanaged_post_hooks = [
        hook
        for hook in post_tool_use
        if all(
            managed_name not in json.dumps(hook, ensure_ascii=False)
            for managed_name in ("log_read.py", "check_citations.py")
        )
    ]
    hooks["PostToolUse"] = unmanaged_post_hooks + managed_post_hooks(profile_root)
    return result


def read_settings(settings_path: Path) -> dict[str, Any]:
    if not settings_path.exists():
        return {}
    value = json.loads(settings_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("settings.json root must be an object")
    return value


def validate_profile(profile_root: Path, mappings: list[tuple[Path, Path]]) -> None:
    for relative in FORBIDDEN_PORTABLE_PATHS:
        forbidden = profile_root / relative
        if forbidden.exists() or forbidden.is_symlink():
            raise ValueError(f"forbidden portable state: {forbidden}")
    for source, _ in mappings:
        if not source.exists():
            raise ValueError(f"source missing: {source}")
    for required_hook in ("hooks/log_read.py", "hooks/check_citations.py"):
        if not (profile_root / required_hook).is_file():
            raise ValueError(f"source missing: {profile_root / required_hook}")
    destinations = [normalized_path(destination) for _, destination in mappings]
    if len(destinations) != len(set(destinations)):
        raise ValueError("duplicate managed destination")


def link_matches(source: Path, destination: Path) -> bool:
    try:
        return destination.is_symlink() and destination.resolve() == source.resolve()
    except OSError:
        return False


def link_changes(
    mappings: list[tuple[Path, Path]],
) -> list[tuple[Path, Path]]:
    return [
        (source, destination)
        for source, destination in mappings
        if not link_matches(source, destination)
    ]


def describe_actual(destination: Path) -> str:
    if destination.is_symlink():
        try:
            return f"symlink -> {os.readlink(destination)}"
        except OSError as error:
            return f"unreadable symlink ({error})"
    if destination.exists():
        return "ordinary path"
    return "missing"


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def backup_relative(destination: Path, claude_home: Path) -> Path:
    try:
        return Path("claude") / destination.relative_to(claude_home)
    except ValueError as error:
        raise ValueError(f"destination escapes Claude home: {destination}") from error


def verify_state(
    mappings: list[tuple[Path, Path]], settings_path: Path, desired: dict[str, Any]
) -> list[str]:
    errors = []
    for source, destination in mappings:
        if not link_matches(source, destination):
            errors.append(
                f"WRONG_LINK {destination}: expected {source}; actual "
                f"{describe_actual(destination)}"
            )
    try:
        current = read_settings(settings_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"SETTINGS_INVALID {settings_path}: {error}")
    else:
        if current != desired:
            errors.append(f"SETTINGS_DRIFT {settings_path}")
    return errors


def run_dry_run(
    changes: list[tuple[Path, Path]], settings_changed: bool
) -> int:
    for source, destination in changes:
        print(f"PLAN backup then link {destination} -> {source}")
    if settings_changed:
        print("PLAN settings merge managed fields")
    if not changes and not settings_changed:
        print("UNCHANGED")
    print("DRY_RUN_OK")
    return 0


def run_apply(
    mappings: list[tuple[Path, Path]],
    changes: list[tuple[Path, Path]],
    claude_home: Path,
    settings_path: Path,
    current_settings: dict[str, Any],
    desired_settings: dict[str, Any],
) -> int:
    settings_changed = current_settings != desired_settings
    if not changes and not settings_changed:
        print("BACKUP_ROOT=none")
        print("UNCHANGED")
        print("APPLY_OK")
        return 0

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    backup_root = claude_home / "portable-backups" / stamp
    moved: list[tuple[Path, Path]] = []
    created_links: list[Path] = []
    settings_backup: Path | None = None
    try:
        backup_root.mkdir(parents=True, exist_ok=False)
        for _, destination in changes:
            if destination.exists() or destination.is_symlink():
                backup = backup_root / backup_relative(destination, claude_home)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(os.fspath(destination), os.fspath(backup))
                moved.append((destination, backup))

        if settings_changed and settings_path.exists():
            settings_backup = backup_root / "claude/settings.json"
            settings_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(settings_path, settings_backup)

        for source, destination in changes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(
                os.fspath(source),
                os.fspath(destination),
                target_is_directory=source.is_dir(),
            )
            created_links.append(destination)
        if settings_changed:
            write_json_atomic(settings_path, desired_settings)

        errors = verify_state(mappings, settings_path, desired_settings)
        if errors:
            raise RuntimeError("; ".join(errors))
    except Exception:
        for destination in reversed(created_links):
            if destination.is_symlink():
                destination.unlink()
        for destination, backup in reversed(moved):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(os.fspath(backup), os.fspath(destination))
        if settings_changed:
            if settings_backup is not None and settings_backup.exists():
                shutil.copy2(settings_backup, settings_path)
            elif settings_path.exists():
                settings_path.unlink()
        raise

    print(f"BACKUP_ROOT={backup_root}")
    print("APPLY_OK")
    return 0


def main() -> int:
    args = parse_args()
    profile_root = args.profile_root.resolve()
    home = args.home.resolve()
    claude_home = home / ".claude"
    settings_path = claude_home / "settings.json"
    mappings = link_map(profile_root, home)
    try:
        validate_profile(profile_root, mappings)
        current_settings = read_settings(settings_path)
        desired_settings = merged_settings(current_settings, profile_root, home)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    changes = link_changes(mappings)
    settings_changed = current_settings != desired_settings
    if args.dry_run:
        return run_dry_run(changes, settings_changed)
    if args.verify:
        errors = verify_state(mappings, settings_path, desired_settings)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("VERIFY_OK")
        return 0
    try:
        return run_apply(
            mappings,
            changes,
            claude_home,
            settings_path,
            current_settings,
            desired_settings,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"APPLY_FAILED {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
