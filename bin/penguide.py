import sys
import os
import textwrap

# Ensure project root is on path when running as script (e.g. python bin/penguide.py)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.orchestrator import Orchestrator
from configs.settings import OLLAMA_MODEL, LOW_RESOURCE
from configs.policy import ALLOWED_COMMANDS, DENY_COMMANDS
from tools.registry import TOOLS


# Simple ANSI color helpers (no external deps).
RESET = "\033[0m"
BOLD = "\033[1m"
FG_CYAN = "\033[36m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_RED = "\033[31m"
FG_MAGENTA = "\033[35m"
FG_WHITE = "\033[37m"


def _color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def _box(title: str, body: str, border_color: str = FG_CYAN, title_color: str = FG_CYAN, wrap_width: int = 80) -> str:
    """
    Render text in a compact, cyberpunk-style block: colored title + top/bottom lines, no vertical bars.

    Long lines are softly wrapped to keep the block readable in typical terminals.
    """
    # Wrap each logical line separately so we preserve paragraph breaks
    wrapped_lines = []
    raw_lines = body.splitlines() or [""]
    for line in raw_lines:
        if not line:
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(line, width=wrap_width))

    content_width = max(len(line) for line in wrapped_lines) if wrapped_lines else len(title)
    title_text = f"[ {title} ]"
    border_len = max(len(title_text), content_width + 4)

    top = _color("─" * border_len, border_color)
    bottom = top
    title_line = _color(title_text.center(border_len), title_color)

    body_lines = [f"  {line}" for line in wrapped_lines]
    return "\n".join([title_line, top, *body_lines, bottom])


def _format_penguide_output(raw: str) -> str:
    """Apply colorful highlighting to Penguide's text before boxing."""
    colored_lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("> Executing:"):
            colored_lines.append(_color(line, BOLD + FG_YELLOW))
        elif stripped.startswith("[Error:"):
            colored_lines.append(_color(line, FG_RED))
        elif stripped.startswith("Hello") or stripped.startswith("Penguide"):
            # Greeting / intro lines
            colored_lines.append(_color(line, FG_CYAN))
        elif stripped.startswith("* "):
            # Bullet points
            colored_lines.append(_color(line, FG_GREEN))
        elif stripped.startswith("So, ") or stripped.startswith("In your case"):
            # Summary or emphasis
            colored_lines.append(_color(line, FG_YELLOW))
        elif stripped.startswith("```") or stripped.startswith("$ "):
            # Code blocks and shell examples
            colored_lines.append(_color(line, FG_GREEN))
        else:
            # Default body text
            colored_lines.append(_color(line, FG_WHITE))
    return "\n".join(colored_lines)


def _print_welcome(mode: str):
    """Print a more informative, chat-like welcome header."""
    title = _color("Penguide - Your Linux & Kernel Guide", BOLD + FG_CYAN)
    model = os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL)

    print(title)
    print(_color(f"Model: {model}", FG_MAGENTA))
    print(_color(f"Teaching mode: {mode}", FG_MAGENTA))
    if LOW_RESOURCE:
        print(_color("Low-resource mode: ON (smaller context, less CPU/RAM)", FG_YELLOW))
    print()
    print("Type your question in natural language.")
    print("Penguide will explain and may safely run ONE Linux command for you.")
    print()
    print(_color("Special commands:", BOLD))
    print("  help         - show this help")
    print("  history      - show recent conversation turns")
    print("  commands     - show allowed shell commands")
    print("  mode simple  - shorter explanations")
    print("  mode detailed- deeper explanations")
    print("  clear        - clear conversation memory")
    print("  exit         - quit Penguide")
    print()


def main():
    orch = Orchestrator()

    # One-shot / non-interactive mode
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg in ("--clear", "-c"):
            orch.memory.clear()
            print("Conversation memory cleared.")
            return
        user_input = " ".join(sys.argv[1:])
        output = orch.step(user_input)
        if output:
            print(output)
        return

    # Interactive loop
    _print_welcome(orch.teaching_mode)

    while True:
        try:
            prompt_label = _color("🐧 penguide> ", FG_CYAN)
            user_input = input(prompt_label)

            # Ignore pure escape/arrow-key sequences (like up-arrow ^[[A)
            if user_input.startswith("\x1b["):
                continue

            user_input = user_input.strip()

            if not user_input:
                continue

            lower = user_input.lower()

            if lower in ("exit", "quit"):
                print("Goodbye!")
                break

            if lower in ("help", "?"):
                _print_welcome(orch.teaching_mode)
                continue

            if lower == "mode":
                print(f"Current teaching mode: {orch.teaching_mode}")
                print("Available modes: simple, detailed")
                continue

            if lower.startswith("mode "):
                _, _, requested = lower.partition(" ")
                requested = requested.strip()
                if requested in ("simple", "detailed"):
                    orch.teaching_mode = requested
                    print(f"Teaching mode set to: {orch.teaching_mode}")
                else:
                    print("Unknown mode. Available modes: simple, detailed")
                continue

            if lower in ("commands", "tools"):
                header = (
                    "Penguide can only run a small, permit-listed set of shell commands.\n"
                    "These are checked against an allow/deny policy before execution.\n"
                )

                allowed_lines = []
                for name in sorted(ALLOWED_COMMANDS):
                    desc = TOOLS.get(name, "")
                    colored_name = _color(f"{name:8}", FG_GREEN)
                    if desc:
                        allowed_lines.append(f"{colored_name} - {desc}")
                    else:
                        allowed_lines.append(colored_name)

                deny_lines = []
                if DENY_COMMANDS:
                    deny_lines.append(_color("Always denied (never run):", BOLD + FG_RED))
                    for name in sorted(DENY_COMMANDS):
                        deny_lines.append(_color(f"  {name}", FG_RED))

                body_parts = [
                    header.rstrip(),
                    "",
                    _color("Allowed commands:", BOLD),
                    *allowed_lines,
                ]
                if deny_lines:
                    body_parts.extend(["", *deny_lines])

                box_text = "\n".join(body_parts)
                print()
                print(_box("Shell policy", box_text))
                print()
                continue

            if lower in ("history", "hist"):
                if not orch.memory.history:
                    body = "  (no history yet)"
                else:
                    lines = []
                    for i, entry in enumerate(orch.memory.history[-10:], start=1):
                        role = entry.get("role", "?")
                        content = entry.get("content", "").strip().replace("\n", " ")
                        if len(content) > 120:
                            content = content[:117] + "..."
                        lines.append(f"{i:2}. {role:9} - {content}")
                    body = "\n".join(lines)

                print()
                print(_box("Recent conversation", body, border_color=FG_MAGENTA, title_color=FG_MAGENTA))
                print()
                continue

            if lower == "clear":
                orch.memory.clear()
                print("Conversation memory cleared.")
                continue

            # Small UX hint: users sometimes paste shell-style env checks here
            if user_input.startswith("echo ") and "$" in user_input:
                print(
                    "\n(Note: you're inside Penguide, not your system shell. "
                    "I'll treat this as a learning question about echo. "
                    "To inspect real environment variables, run echo in your terminal prompt instead.)\n"
                )

            output = orch.step(user_input)
            if output:
                formatted = _format_penguide_output(output)
                print()
                print(_box("Penguide", formatted, border_color=FG_MAGENTA, title_color=FG_CYAN))
                print()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
