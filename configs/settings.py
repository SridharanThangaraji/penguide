"""
Central settings for Penguide. Prefer environment variables; defaults are safe for local use.
"""
import os

# Ollama
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "20"))

# Memory: max conversation turns to include in context (avoid token overflow)
MEMORY_MAX_TURNS = int(os.environ.get("PENGUIDE_MEMORY_MAX_TURNS", "20"))

# Knowledge base path (relative to project root or absolute)
KNOWLEDGE_PATH = os.environ.get("PENGUIDE_KNOWLEDGE_PATH", "knowledge/kernel")

# Shell
SHELL_TIMEOUT = int(os.environ.get("PENGUIDE_SHELL_TIMEOUT", "5"))
