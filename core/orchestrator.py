from core.agent import Agent
from tools.shell import run
from core.prompt import SYSTEM_PROMPT
from memory.memory import Memory
from core.knowledge import KnowledgeBase
from configs.teaching import DEFAULT_TEACHING_MODE, COMMAND_TEACHING_HINTS
from configs.policy import ALLOWED_COMMANDS
import os
import re


def _extract_command(reply: str) -> tuple[str | None, str]:
    """
    Extract a single-shell-line command from the model reply.

    Returns (cmd, explanation_prefix).
    - cmd is None if no RUN: marker is found.
    - explanation_prefix is everything before RUN: (may be empty).
    """
    # Match RUN even if not at column 0; capture up to end of line only
    match = re.search(r"RUN:\s*(.+)", reply)
    if not match:
        return None, reply

    # Only keep the first line after RUN:
    raw_cmd = match.group(1).strip().splitlines()[0].strip()

    # Strip common markdown wrappers that models sometimes add
    # e.g. `ls -l`, **ls**, or ```ls -l```
    if raw_cmd.startswith("```") and raw_cmd.endswith("```"):
        raw_cmd = raw_cmd.strip("`")

    # Strip surrounding single backticks once
    if raw_cmd.startswith("`") and raw_cmd.endswith("`") and len(raw_cmd) > 1:
        raw_cmd = raw_cmd[1:-1].strip()

    # Strip trailing markdown bold markers like "**" but keep single '*'
    raw_cmd = re.sub(r"\*{2,}$", "", raw_cmd).strip()

    explanation = reply[: match.start()].strip()
    return raw_cmd, explanation


class Orchestrator:
    def __init__(self):
        self.agent = Agent()
        self.memory = Memory()
        self.kb = KnowledgeBase()
        self.teaching_mode = DEFAULT_TEACHING_MODE

    def step(self, user_input):
        # Retrieve relevant kernel documentation
        kb_context = self.kb.query(user_input)
        history_context = self.memory.get_context()

        full_context = f"{history_context}\n{kb_context}" if kb_context else history_context

        # Compose prompt with teaching mode, environment hints, allowed commands, and optional per-command hints
        base = user_input.split()[0] if user_input else ""
        hint = COMMAND_TEACHING_HINTS.get(base, {}).get(self.teaching_mode, "")
        teaching_header = f"Teaching mode: {self.teaching_mode}.\n"
        env_hint = (
            f"The user's home directory is: {os.path.expanduser('~')}.\n"
            f"The current working directory is: {os.getcwd()}.\n"
            "When the user refers to their home directory, prefer '~' or '$HOME'. "
            "For project-related paths, prefer using the current working directory or subdirectories under it, "
            "instead of inventing new absolute paths.\n"
        )
        allowed_list = ", ".join(sorted(ALLOWED_COMMANDS))
        policy_hint = (
            "You may only run one shell command per response, and only if it is in this allow-list: "
            f"{allowed_list}.\n"
        )
        hint_block = f"Command teaching hint for `{base}`: {hint}\n" if hint else ""

        prompt = f"{SYSTEM_PROMPT}\n{teaching_header}{env_hint}{policy_hint}{hint_block}User: {user_input}"

        reply = self.agent.think(prompt, full_context).strip()
        self.memory.add("user", user_input)

        cmd, explanation = _extract_command(reply)

        if cmd:
            output = run(cmd).strip()
            combined_response = f"{explanation}\n\n> Executing: {cmd}\n{output}" if explanation else output

            if output:
                self.memory.add("tool", output)

            self.memory.add("assistant", combined_response)
            return combined_response

        # Fallback: if the user typed an explicit shell command starting with an
        # allowed base (e.g. "whoami", "ls ~/workspace") and the model did not
        # provide a RUN: line, run that command anyway after the explanation so
        # learners can see the real output.
        tokens = user_input.split()
        if tokens and tokens[0] in ALLOWED_COMMANDS:
            cmd = user_input
            output = run(cmd).strip()
            combined_response = f"{reply}\n\n> Executing: {cmd}\n{output}" if reply else output
            if output:
                self.memory.add("tool", output)
            self.memory.add("assistant", combined_response)
            return combined_response

        self.memory.add("assistant", reply)
        return reply
