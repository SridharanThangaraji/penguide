"""
Teaching configuration for Penguide.

Defines teaching modes (simple vs detailed) and per-command hints that
the orchestrator can inject into the system prompt.
"""
import os

# Supported teaching modes
TEACHING_MODES = ("simple", "detailed")

# Default mode can be overridden via environment variable
DEFAULT_TEACHING_MODE = os.environ.get("PENGUIDE_TEACHING_MODE", "simple")
if DEFAULT_TEACHING_MODE not in TEACHING_MODES:
    DEFAULT_TEACHING_MODE = "simple"


# Per-command teaching hints to help the model adapt explanation depth.
# These are intentionally short and human-readable; they are appended to
# the system prompt for matching commands.
COMMAND_TEACHING_HINTS = {
    "ls": {
        "simple": (
            "Explain ls in one or two sentences and show one basic example listing the current directory. "
            "If the user mentions the home directory, use '~' or '$HOME'. If they mention a workspace folder, "
            "prefer a concrete path like '~/workspace' instead of inventing usernames or directories."
        ),
        "detailed": (
            "Explain ls more deeply, including -l and -a flags, permissions, and an example. "
            "If the user mentions paths like home or workspace, map them to real paths relative to '~' or "
            "the current working directory, and avoid made-up paths such as '/home/Penguide'."
        ),
    },
    "pwd": {
        "simple": "Briefly explain what pwd does and show one example.",
        "detailed": "Explain pwd in more depth, including how it relates to the shell's working directory.",
    },
    "whoami": {
        "simple": "Explain whoami in one short paragraph and show a simple example.",
        "detailed": "Explain whoami in more detail, including how it relates to user IDs and login sessions.",
    },
    "grep": {
        "simple": "Give a short explanation of grep with one simple example on a regular text file.",
        "detailed": "Explain grep with multiple examples and mention common flags like -i and -r, but avoid scanning /proc.",
    },
    "find": {
        "simple": "Give a short explanation of find with one basic example searching the current directory.",
        "detailed": "Explain find with examples of searching by name and type, but avoid very heavy or recursive root scans.",
    },
    "ps": {
        "simple": "Briefly explain ps and show one example listing the user's processes.",
        "detailed": "Explain ps with a couple of examples (e.g. ps aux, ps -ef) and how to interpret key columns.",
    },
    "df": {
        "simple": "Explain df briefly and show one example of checking disk usage.",
        "detailed": "Explain df -h in more detail, describing what each column means.",
    },
    "du": {
        "simple": "Give a short explanation of du with one simple example on a directory.",
        "detailed": "Explain du with -h and --max-depth style usage, and warn that it can be slow on large trees.",
    },
    "free": {
        "simple": "Briefly explain the free command and how to read total vs used memory.",
        "detailed": "Explain free -h in more detail, including buffers/cache and swap.",
    },
    "ip": {
        "simple": "Give a short explanation of ip and show a safe read-only example like ip address show.",
        "detailed": "Explain ip in more depth with a couple of safe read-only examples; avoid configuration-changing commands.",
    },
    "ss": {
        "simple": "Briefly explain ss and show a simple example listing listening sockets.",
        "detailed": "Explain ss with safe examples like ss -tuln and what the columns mean.",
    },
}

