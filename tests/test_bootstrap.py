from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import bootstrap


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO_ROOT / "bootstrap.py"


class Fixture:
    def __init__(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="claude-profile-test-")
        self.root = Path(self._temp.name)
        self.profile = self.root / "profile"
        self.home = self.root / "home"
        self.claude_home = self.home / ".claude"

        self._write(self.profile / ".claude/CLAUDE.md", "portable global\n")
        self._write(self.profile / "statusline.sh", "#!/usr/bin/env bash\n")
        for skill in ("fp", "notebooklm", "verify"):
            self._write(
                self.profile / f".claude/skills/{skill}/SKILL.md",
                f"portable {skill}\n",
            )
        self._write(self.profile / "agents/learn.md", "portable agent\n")
        self._write(self.profile / "hooks/log_read.py", "print('log')\n")
        self._write(self.profile / "hooks/check_citations.py", "print('check')\n")

        self._write(self.claude_home / "CLAUDE.md", "local global\n")
        self._write(
            self.claude_home / "skills/verify/SKILL.md",
            "local verify\n",
        )
        self._write(self.claude_home / "local-only.txt", "keep me\n")

        secondbrain = self.home / "Dropbox/00.SecondBrain"
        settings = {
            "permissions": {
                "additionalDirectories": [
                    str(secondbrain),
                    str(self.profile),
                    "D:/keep-this-directory",
                ],
                "allow": ["Read"],
            },
            "hooks": {
                "SessionStart": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": (
                                    f'python "{secondbrain / "scripts/check_inbox.py"}"'
                                ),
                            }
                        ]
                    },
                    {
                        "hooks": [
                            {"type": "command", "command": "python keep-session.py"}
                        ]
                    },
                ],
                "PostToolUse": [
                    {
                        "matcher": "Read|Write|Edit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python",
                                "args": [str(self.profile / "hooks/log_read.py")],
                            }
                        ],
                    },
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {"type": "command", "command": "python keep-post.py"}
                        ],
                    },
                ],
            },
            "statusLine": {"type": "command", "command": "old-status"},
            "theme": "dark",
        }
        self._write(
            self.claude_home / "settings.json",
            json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
        )

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def close(self) -> None:
        self._temp.cleanup()


class BootstrapCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = Fixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def run_bootstrap(self, mode: str | None) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(BOOTSTRAP),
        ]
        if mode is not None:
            command.append(mode)
        command.extend(
            [
                "--profile-root",
                str(self.fixture.profile),
                "--home",
                str(self.fixture.home),
            ]
        )
        environment = os.environ.copy()
        environment["USERPROFILE"] = str(self.fixture.home)
        environment["HOME"] = str(self.fixture.home)
        return subprocess.run(
            command,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )

    def test_no_mode_refuses_mutation(self) -> None:
        result = self.run_bootstrap(None)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(
            "local global\n",
            (self.fixture.claude_home / "CLAUDE.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.fixture.claude_home / "portable-backups").exists())

    def test_dry_run_is_read_only_and_reports_actions(self) -> None:
        before = (self.fixture.claude_home / "settings.json").read_bytes()

        result = self.run_bootstrap("--dry-run")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PLAN backup then link", result.stdout)
        self.assertIn("PLAN settings", result.stdout)
        self.assertIn("DRY_RUN_OK", result.stdout)
        self.assertEqual(before, (self.fixture.claude_home / "settings.json").read_bytes())
        self.assertFalse((self.fixture.claude_home / "CLAUDE.md").is_symlink())
        self.assertFalse((self.fixture.claude_home / "portable-backups").exists())

    def test_apply_backs_up_links_and_preserves_unmanaged_settings(self) -> None:
        result = self.run_bootstrap("--apply")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("APPLY_OK", result.stdout)
        backup_line = next(
            line for line in result.stdout.splitlines() if line.startswith("BACKUP_ROOT=")
        )
        backup_root = Path(backup_line.removeprefix("BACKUP_ROOT="))
        self.assertEqual(
            "local global\n",
            (backup_root / "claude/CLAUDE.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((backup_root / "claude/settings.json").is_file())

        expected_links = {
            self.fixture.claude_home / "CLAUDE.md": self.fixture.profile
            / ".claude/CLAUDE.md",
            self.fixture.claude_home / "statusline.sh": self.fixture.profile
            / "statusline.sh",
            self.fixture.claude_home / "skills/fp": self.fixture.profile
            / ".claude/skills/fp",
            self.fixture.claude_home / "skills/notebooklm": self.fixture.profile
            / ".claude/skills/notebooklm",
            self.fixture.claude_home / "skills/verify": self.fixture.profile
            / ".claude/skills/verify",
            self.fixture.claude_home / "agents/learn.md": self.fixture.profile
            / "agents/learn.md",
        }
        for destination, source in expected_links.items():
            self.assertTrue(destination.is_symlink(), destination)
            self.assertEqual(source.resolve(), destination.resolve())

        settings = json.loads(
            (self.fixture.claude_home / "settings.json").read_text(encoding="utf-8")
        )
        self.assertEqual("dark", settings["theme"])
        self.assertEqual(["Read"], settings["permissions"]["allow"])
        self.assertEqual(
            ["D:/keep-this-directory"],
            settings["permissions"]["additionalDirectories"],
        )
        session_commands = json.dumps(settings["hooks"]["SessionStart"])
        self.assertIn("keep-session.py", session_commands)
        self.assertNotIn("check_inbox.py", session_commands)
        post = settings["hooks"]["PostToolUse"]
        post_json = json.dumps(post)
        self.assertIn("keep-post.py", post_json)
        self.assertEqual(1, post_json.count("log_read.py"))
        self.assertEqual(1, post_json.count("check_citations.py"))
        self.assertEqual("command", settings["statusLine"]["type"])
        self.assertIn(".claude/statusline.sh", settings["statusLine"]["command"])
        self.assertEqual(
            "keep me\n",
            (self.fixture.claude_home / "local-only.txt").read_text(encoding="utf-8"),
        )

        second = self.run_bootstrap("--apply")
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertIn("BACKUP_ROOT=none", second.stdout)
        self.assertIn("UNCHANGED", second.stdout)

    def test_verify_rejects_wrong_link_and_reports_actual_target(self) -> None:
        apply_result = self.run_bootstrap("--apply")
        self.assertEqual(0, apply_result.returncode, apply_result.stdout + apply_result.stderr)
        global_link = self.fixture.claude_home / "CLAUDE.md"
        global_link.unlink()
        wrong = self.fixture.root / "wrong-global.md"
        wrong.write_text("wrong\n", encoding="utf-8")
        global_link.symlink_to(wrong)

        result = self.run_bootstrap("--verify")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("wrong-global.md", result.stdout + result.stderr)

    def test_forbidden_portable_state_fails_before_mutation(self) -> None:
        Fixture._write(self.fixture.profile / ".claude/settings.json", "{}\n")

        result = self.run_bootstrap("--apply")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("settings.json", result.stdout + result.stderr)
        self.assertEqual(
            "local global\n",
            (self.fixture.claude_home / "CLAUDE.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.fixture.claude_home / "portable-backups").exists())

    def test_apply_rolls_back_if_link_creation_fails(self) -> None:
        mappings = bootstrap.link_map(self.fixture.profile, self.fixture.home)
        settings_path = self.fixture.claude_home / "settings.json"
        settings_before = settings_path.read_bytes()
        current = bootstrap.read_settings(settings_path)
        desired = bootstrap.merged_settings(
            current, self.fixture.profile, self.fixture.home
        )
        changes = bootstrap.link_changes(mappings)
        real_symlink = bootstrap.os.symlink
        calls = 0

        def fail_second_symlink(*args: object, **kwargs: object) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("controlled symlink failure")
            real_symlink(*args, **kwargs)

        with mock.patch.object(bootstrap.os, "symlink", fail_second_symlink):
            with self.assertRaisesRegex(OSError, "controlled symlink failure"):
                bootstrap.run_apply(
                    mappings,
                    changes,
                    self.fixture.claude_home,
                    settings_path,
                    current,
                    desired,
                )

        self.assertFalse((self.fixture.claude_home / "CLAUDE.md").is_symlink())
        self.assertEqual(
            "local global\n",
            (self.fixture.claude_home / "CLAUDE.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.fixture.claude_home / "statusline.sh").exists())
        self.assertEqual(settings_before, settings_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
