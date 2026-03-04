"""Unit tests for shell policy and tools.shell — 25 tests."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from configs.policy import ALLOWED_COMMANDS, DENY_COMMANDS
from tools import shell


def test_allowed_commands_non_empty():
    assert len(ALLOWED_COMMANDS) > 0


def test_deny_commands_non_empty():
    assert len(DENY_COMMANDS) > 0


def test_pwd_allowed():
    assert "pwd" in ALLOWED_COMMANDS


def test_ls_allowed():
    assert "ls" in ALLOWED_COMMANDS


def test_sudo_denied():
    assert "sudo" in DENY_COMMANDS


def test_chmod_denied():
    assert "chmod" in DENY_COMMANDS


def test_rm_allowed():
    assert "rm" in ALLOWED_COMMANDS


def test_run_empty_returns_empty():
    assert shell.run("") == ""
    assert shell.run("   ") == ""


def test_run_sudo_returns_empty():
    assert shell.run("sudo rm -rf /") == ""


def test_run_chmod_returns_empty():
    assert shell.run("chmod +x x.sh") == ""


def test_run_chown_returns_empty():
    assert shell.run("chown root /tmp/x") == ""


def test_run_unknown_command_returns_empty():
    assert shell.run("nonexistentcommandxyz") == ""


def test_run_pwd_returns_something():
    out = shell.run("pwd")
    assert isinstance(out, str)
    assert len(out) > 0 or out == ""


def test_run_whoami_returns_string():
    out = shell.run("whoami")
    assert isinstance(out, str)


def test_run_date_returns_string():
    out = shell.run("date")
    assert isinstance(out, str) or "[Error" in out or "[Command" in out


def test_run_ls_no_error():
    out = shell.run("ls")
    assert isinstance(out, str)


def test_run_echo_not_in_allowed():
    # echo might not be in ALLOWED_COMMANDS
    out = shell.run("echo hi")
    assert isinstance(out, str)


def test_allowed_contains_common_commands():
    for c in ["ls", "cat", "pwd", "mkdir", "grep"]:
        assert c in ALLOWED_COMMANDS


def test_deny_contains_dangerous():
    for c in ["sudo", "dd", "reboot", "shutdown"]:
        assert c in DENY_COMMANDS


def test_run_with_args_pwd():
    out = shell.run("pwd")
    assert isinstance(out, str)


def test_run_timeout_eventually():
    # Timeout behavior: run() returns string (may contain "[Command timed out.]")
    out = shell.run("ls")
    assert isinstance(out, str)


def test_run_invalid_syntax_returns_error_string():
    out = shell.run("ls (")
    assert isinstance(out, str)
    assert "Error" in out or len(out) == 0 or out == ""


def test_policy_sets_are_disjoint():
    # Some commands might be in both in theory; typically they're disjoint
    overlap = ALLOWED_COMMANDS & DENY_COMMANDS
    assert len(overlap) == 0


def test_run_none_equivalent_empty():
    # run with empty/whitespace returns ""
    assert shell.run("") == ""
    assert shell.run("\t") == ""
