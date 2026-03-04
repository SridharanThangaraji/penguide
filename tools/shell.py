import subprocess
import shlex
from configs.policy import DENY_COMMANDS, ALLOWED_COMMANDS
from configs.settings import SHELL_TIMEOUT


def _extract_base(cmd: str) -> str:
    """
    Extract the base program name from a shell command using shlex for robustness.
    Falls back to simple splitting if shlex fails.
    """
    try:
        parts = shlex.split(cmd, posix=True)
        return parts[0] if parts else ""
    except Exception:
        return cmd.split()[0] if cmd.split() else ""


def run(cmd):
    """
    Run a shell command if it passes the allow/deny policy.

    Returns decoded stdout (and stderr merged), or a short, user-friendly
    error message if the command fails or times out.
    """
    if not cmd or not cmd.strip():
        return ""

    base = _extract_base(cmd)

    if base in DENY_COMMANDS:
        return ""

    if base not in ALLOWED_COMMANDS:
        return ""

    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=SHELL_TIMEOUT,
        ).decode()
    except subprocess.TimeoutExpired:
        return "[Error: command timed out. It may be taking too long or waiting on input.]"
    except subprocess.CalledProcessError as e:
        # Command executed but exited with a non-zero status. This often means:
        # - invalid options
        # - no matches (for grep/find)
        # - permission issues when reading kernel files
        output = ""
        try:
            if e.output:
                output = e.output.decode(errors="replace")
        except Exception:
            output = ""
        message = (
            f"[Error: command exited with status {e.returncode}. "
            "This usually means invalid options, no matches, or permission issues.]"
        )
        if output:
            message += f"\n{output}"
        return message
    except Exception as e:
        return f"[Error: {e}]"
