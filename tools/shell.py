import subprocess
from configs.policy import DENY_COMMANDS, ALLOWED_COMMANDS

def run(cmd):
    base = cmd.split()[0]

    if base in DENY_COMMANDS:
        return ""

    if base not in ALLOWED_COMMANDS:
        return ""

    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=5
        ).decode()
    except Exception:
        return ""
