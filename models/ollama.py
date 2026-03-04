import requests
from urllib.parse import urlparse, urlunparse
from configs.settings import OLLAMA_URL, OLLAMA_TIMEOUT


def _post(url: str, payload: dict) -> requests.Response:
    r = requests.post(
        url,
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    r.raise_for_status()
    return r


def _root_base(url: str) -> str:
    """
    Normalize OLLAMA_URL down to scheme://host:port so we can construct
    /api/generate or /api/chat robustly regardless of what path the user set.
    """
    parsed = urlparse(url)
    return urlunparse(parsed._replace(path="", params="", query="", fragment="")).rstrip("/")


def _generate_url(base: str) -> str:
    return f"{base}/api/generate"


def _chat_url(base: str) -> str:
    return f"{base}/api/chat"


def _extract_text(data: dict) -> str:
    """
    Support both legacy generate (response="...") and chat (message.content)
    response shapes.
    """
    if not isinstance(data, dict):
        return ""
    if "response" in data:
        return data.get("response") or ""
    message = data.get("message") or {}
    if isinstance(message, dict):
        return message.get("content") or ""
    return ""


def ask(model, prompt):
    """
    Call Ollama to get a single, non-streaming response.

    Strategy (robust across Ollama versions):
    - Derive a root base URL from OLLAMA_URL (host + port).
    - First try POST base + /api/generate with the legacy generate payload.
    - If that endpoint returns 404, try POST base + /api/chat with chat payload.
    - Extract text from either {"response": "..."} or {"message": {"content": "..."}}.
    """
    base = _root_base(OLLAMA_URL or "http://127.0.0.1:11434")
    gen_url = _generate_url(base)
    chat_url = _chat_url(base)

    try:
        # 1) Try legacy /api/generate
        try:
            r = _post(
                gen_url,
                {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            return _extract_text(r.json())
        except requests.exceptions.HTTPError as http_err:
            # If /api/generate itself is missing, fall through to /api/chat
            if http_err.response is None or http_err.response.status_code != 404:
                raise

        # 2) Fallback to /api/chat
        r = _post(
            chat_url,
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        return _extract_text(r.json())

    except requests.exceptions.Timeout:
        return "[Penguide: The model took too long to respond. Try a shorter question or check Ollama.]"
    except requests.exceptions.ConnectionError:
        return "[Penguide: Cannot reach Ollama. Is it running? Start with: ollama serve]"
    except Exception as e:
        return f"[Penguide: Error calling model: {e}]"

