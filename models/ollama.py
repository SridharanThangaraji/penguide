import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def ask(model, prompt):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=20   # ← VERY IMPORTANT
        )
        r.raise_for_status()
        return r.json()["response"]
    except requests.exceptions.Timeout:
        return "RUN: ls ~"  # safe fallback for testing
    except Exception as e:
        return ""

