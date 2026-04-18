"""
Central settings for Penguide. Prefer environment variables; defaults are safe for local use.
"""
import os

# Ollama
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "20"))

# Google Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyAAH5bew3QsWOn7l-rVPqSuVIcWZ3ajYlQ")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# LLM Backend: 'ollama' or 'gemini'
LLM_BACKEND = os.environ.get("PENGUIDE_LLM_BACKEND", "gemini").lower()

# Memory: max conversation turns to include in context (avoid token overflow)
# Lower = less RAM/CPU for the model. Use 3–6 on slow/low-memory machines.
MEMORY_MAX_TURNS = int(os.environ.get("PENGUIDE_MEMORY_MAX_TURNS", "20"))

# Low-resource mode: smaller context, shorter prompts (set PENGUIDE_LOW_RESOURCE=1)
# Use when the laptop becomes slow or unusable while running Penguide.
LOW_RESOURCE = os.environ.get("PENGUIDE_LOW_RESOURCE", "").strip().lower() in ("1", "true", "yes")
if LOW_RESOURCE:
    MEMORY_MAX_TURNS = int(os.environ.get("PENGUIDE_MEMORY_MAX_TURNS", "4"))

# Knowledge base: max chars to inject per query (0 = no limit). Capped in low-resource mode.
_KB_MAX_DEFAULT = "1500" if LOW_RESOURCE else "0"
KB_MAX_CHARS = int(os.environ.get("PENGUIDE_KB_MAX_CHARS", _KB_MAX_DEFAULT))
if KB_MAX_CHARS == 0 and LOW_RESOURCE:
    KB_MAX_CHARS = 1500

# Knowledge base path (relative to project root or absolute)
KNOWLEDGE_PATH = os.environ.get("PENGUIDE_KNOWLEDGE_PATH", "knowledge/kernel")

# Shell
SHELL_TIMEOUT = int(os.environ.get("PENGUIDE_SHELL_TIMEOUT", "5"))
