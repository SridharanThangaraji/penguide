# Penguide — Global Documentation

This document describes how Penguide works end to end: architecture, data flow, configuration, security, and optional training.

---

## 1. What Penguide Is

**Penguide** is an educational autonomous agent that helps beginners learn the Linux command line and related kernel concepts. It:

- Answers natural-language questions about Linux and the kernel.
- Suggests **one** safe shell command per turn, explains it, and can execute it in a sandbox.
- Uses in-memory conversation history for follow-up questions.
- Injects short kernel-documentation snippets into context when relevant.

**Tech stack:** Python 3, Ollama (local LLM), no web framework. Single CLI entry point.

---

## 2. Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────────────────────┐
│   User      │────▶│  bin/penguide.py │────▶│  Core / Orchestrator                    │
│   (CLI)     │     │  (entry point)   │     │  - step(user_input)                     │
└─────────────┘     └──────────────────┘     │  - coordinates Agent, Memory, KB, Shell │
                                             └───────────────┬─────────────────────────┘
                                                             │
         ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
         │                                                  │                                                  │
         ▼                                                  ▼                                                  ▼
┌─────────────────┐                              ┌─────────────────┐                              ┌─────────────────┐
│ Memory          │                              │ Core / Agent    │                              │ Core / Knowledge │
│ - history[]     │                              │ - think(p,c)    │                              │ - load *.md     │
│ - get_context() │                              │ - Ollama client │                              │ - query(input)  │
│ - clear()       │                              └────────┬────────┘                              └────────┬────────┘
└─────────────────┘                                       │                                                 │
         │                                                 ▼                                                 ▼
         │                                        ┌─────────────────┐                              ┌─────────────────┐
         │                                        │ models/ollama   │                              │ knowledge/kernel│
         │                                        │ - ask(model,p)  │                              │ - memory.md     │
         │                                        │ - HTTP POST     │                              │ - processes.md  │
         │                                        └─────────────────┘                              └─────────────────┘
         │                                                 │
         │                                                 │ (reply may contain RUN: <cmd>)
         │                                                 ▼
         │                                        ┌─────────────────┐
         └───────────────────────────────────────▶│ tools/shell     │
                                                  │ - run(cmd)      │
                                                  │ - policy check  │
                                                  └────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ configs/policy  │
                                                  │ ALLOWED/DENY    │
                                                  └─────────────────┘
```

- **Entry:** `bin/penguide.py` — interactive loop or one-shot with first argument as the query.
- **Orchestrator** (`core/orchestrator.py`): Runs the full step: KB query → memory context → prompt → agent → parse `RUN:` → optional shell run → memory update → return response.
- **Agent** (`core/agent.py`): Builds full prompt (context + user prompt) and calls `models/ollama.ask()`.
- **Memory** (`memory/memory.py`): List of `{role, content}`; `get_context()` returns the last N turns for the prompt.
- **KnowledgeBase** (`core/knowledge.py`): Loads all `knowledge/kernel/*.md`; `query(user_input)` does keyword/topic matching and returns concatenated snippets.
- **Shell** (`tools/shell.py`): Runs a command only if its first token is in `ALLOWED_COMMANDS` and not in `DENY_COMMANDS`; uses `subprocess` with a timeout.
- **Config** (`configs/settings.py`, `configs/policy.py`): Central settings (Ollama, memory, timeouts) and allow/deny lists.

---

## 3. End-to-End Data Flow (One User Turn)

1. **User input**  
   - Interactive: `input("> ")`  
   - One-shot: `sys.argv[1:]` joined.

2. **Orchestrator.step(user_input)**  
   - **Knowledge:** `KnowledgeBase.query(user_input)` → keyword/topic match over `knowledge/kernel/*.md` → string `kb_context`.  
   - **Memory:** `Memory.get_context()` → last `MEMORY_MAX_TURNS` entries formatted as `"Role: content\n"` → `history_context`.  
   - **Context:** `full_context = history_context + "\n" + kb_context` (or only history if no KB hit).  
   - **Prompt:** `SYSTEM_PROMPT + "\nUser: " + user_input`.  
   - **Agent:** `Agent.think(prompt, full_context)` → `full_prompt = full_context + "\n" + prompt` → `ollama.ask(model, full_prompt)` → raw LLM reply.  
   - **Memory update:** `memory.add("user", user_input)`.

3. **Parse reply**  
   - Regex: `RUN:\s*(.+)`  
   - If **no match:** reply is explanation-only → `memory.add("assistant", reply)` → return reply.  
   - If **match:**  
     - Explanation = everything before `RUN:`; command = captured part.  
     - `tools.shell.run(cmd)` (policy-checked, timeout).  
     - Combined response = explanation + `"> Executing: " + cmd` + command output.  
     - `memory.add("tool", output)` and `memory.add("assistant", combined_response)` → return combined response.

4. **Output**  
   - Printed in the CLI (interactive or one-shot).

So in one turn: **User → KB + Memory → Prompt → Ollama → Reply → (optional) Shell → Memory update → Response to user.**

---

## 4. Components in Detail

### 4.1 Entry point (`bin/penguide.py`)

- No args: interactive loop; prompts `>`; `exit` / `quit` / Ctrl+C to quit; `clear` clears conversation memory.
- With args:  
  - `python3 bin/penguide.py --clear` (or `-c`) clears memory and exits.  
  - Otherwise the full line is treated as one user query and the reply is printed once.

### 4.2 Orchestrator (`core/orchestrator.py`)

- Owns: `Agent`, `Memory`, `KnowledgeBase`.  
- `step(user_input)`: runs the flow above; only one command per response (`RUN: <command>`).

### 4.3 Agent (`core/agent.py`)

- Wraps Ollama: `think(prompt, context)` → `ask(model, context + "\n" + prompt)`.  
- Model name from `configs.settings.OLLAMA_MODEL` (default `mistral`).

### 4.4 Models / Ollama (`models/ollama.py`)

- POST to `OLLAMA_URL` (`/api/generate`), `stream: false`, JSON `{ model, prompt }`.  
- Timeout and URL from `configs.settings`.  
- On timeout / connection error / other error: returns a short user-visible message instead of empty or a hidden fallback.

### 4.5 Memory (`memory/memory.py`)

- `history`: list of `{"role": "user"|"assistant"|"tool", "content": str}`.  
- `get_context()`: last `MEMORY_MAX_TURNS` entries (from `configs.settings`) to avoid token overflow.  
- `clear()`: empties history.

### 4.6 Knowledge base (`core/knowledge.py`)

- Loads every `*.md` under `knowledge/kernel` (or path from `KNOWLEDGE_PATH`).  
- `query(user_input)`: simple keyword/topic match (topic from filename; “kernel” in input returns all).  
- No embeddings or vector DB; result is concatenated markdown snippets.

### 4.7 Shell (`tools/shell.py`)

- `run(cmd)`:  
  - First token of `cmd` must be in `ALLOWED_COMMANDS` and not in `DENY_COMMANDS` (`configs/policy.py`).  
  - Runs with `subprocess.check_output(..., shell=True, timeout=SHELL_TIMEOUT)`.  
  - Returns decoded stdout (and stderr merged), or a short error message on timeout/exception.

### 4.8 Prompts (`core/prompt.py`)

- `SYSTEM_PROMPT`: defines “Penguide”, teaching tone, one command per reply, format `RUN: <command>` for actions.

---

## 5. Configuration

### 5.1 Environment variables (`configs/settings.py`)

| Variable | Meaning | Default |
|----------|---------|---------|
| `OLLAMA_URL` | Ollama generate API URL | `http://127.0.0.1:11434/api/generate` |
| `OLLAMA_MODEL` | Model name | `mistral` |
| `OLLAMA_TIMEOUT` | Request timeout (seconds) | `20` |
| `PENGUIDE_MEMORY_MAX_TURNS` | Max conversation turns in context | `20` |
| `PENGUIDE_KNOWLEDGE_PATH` | Path to kernel docs (relative or absolute) | `knowledge/kernel` |
| `PENGUIDE_SHELL_TIMEOUT` | Shell command timeout (seconds) | `5` |

### 5.2 Policy (`configs/policy.py`)

- **ALLOWED_COMMANDS:** set of command names (first token) that may run.  
- **DENY_COMMANDS:** set that is always blocked even if allowed elsewhere.  
- Only the first token of the user-requested command is checked; no parsing of arguments.

---

## 6. Security Notes

- **Shell:** Commands run with `shell=True`; the **only** enforcement is the allow/deny list on the first token. Do not run Penguide with elevated privileges.  
- **Ollama:** Runs locally; no data is sent to the cloud by default.  
- **Knowledge:** Loaded from local files only.  
- **Memory:** In-memory only; not persisted to disk.

---

## 7. Project Layout (relevant to “how it works”)

```
penguide/
├── bin/
│   └── penguide.py          # CLI entry
├── configs/
│   ├── policy.py            # ALLOWED_COMMANDS, DENY_COMMANDS
│   └── settings.py          # Central settings (env)
├── core/
│   ├── agent.py             # LLM wrapper
│   ├── knowledge.py         # KB load + query
│   ├── orchestrator.py      # Step loop
│   └── prompt.py            # SYSTEM_PROMPT
├── knowledge/
│   └── kernel/              # *.md kernel snippets
├── memory/
│   └── memory.py            # Conversation history
├── models/
│   └── ollama.py            # Ollama HTTP client
├── tools/
│   ├── registry.py          # Tool metadata (e.g. for prompts)
│   └── shell.py             # Safe command execution
├── tests/
│   ├── test_flow.py         # KB + educational flow
│   └── test_comprehensive.py # Branding, KB, memory, policy, mock Ollama
├── docs/
│   └── GLOBAL.md            # This file
├── scripts/                 # Dataset fetch + TensorFlow training (see below)
├── README.md
└── requirements.txt
```

---

## 8. Training (dataset + TensorFlow)

Training is **optional** and intended to be run on another machine (e.g. another laptop).

- **Scripts:**  
  - `scripts/fetch_training_data.py`: Fetches a public dataset (e.g. Linux/shell-related from Hugging Face) and can export in-repo knowledge as (instruction, output) pairs.  
  - `scripts/train_tensorflow.py`: TensorFlow 2 script that loads the prepared data and trains a small model (e.g. for command suggestion or intent).  

- **Usage:**  
  1. Install extra deps: `pip install -r requirements-training.txt` (or as indicated in the scripts).  
  2. From project root: `python scripts/fetch_training_data.py` → writes data under `data/` (or path configured in the script).  
  3. On the other laptop: copy `data/` and run `python scripts/train_tensorflow.py` (see script for args and output paths).  

Details (dataset name, format, model architecture) are in the scripts and in `docs/TRAINING.md` if present.

---

## 9. Quick Reference

- **Run:** `python3 bin/penguide.py` (interactive) or `python3 bin/penguide.py "How do I see processes?"` (one-shot).  
- **Clear memory:** type `clear` in interactive mode, or `python3 bin/penguide.py --clear`.  
- **Prerequisites:** Ollama running, model pulled (e.g. `ollama pull mistral`), `pip install -r requirements.txt`.  
- **Tests:** `python tests/test_flow.py` and `python -m pytest tests/` or `python tests/test_comprehensive.py`.

This is the global picture of how Penguide works end to end.
