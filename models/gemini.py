import requests
from configs.settings import GOOGLE_API_KEY, GEMINI_MODEL, OLLAMA_TIMEOUT

def ask(model: str, prompt: str) -> str:
    """
    Call Google Gemini API to get a response.
    """
    if not GOOGLE_API_KEY:
        return "[Penguide: Google API Key is missing. Please set it in configs/settings.py or via GOOGLE_API_KEY env var.]"

    url = f"https://generativelanguage.googleapis.com/v1/models/{model or GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract text from Gemini response structure
        # data['candidates'][0]['content']['parts'][0]['text']
        candidates = data.get("candidates", [])
        if not candidates:
            return "[Penguide: No candidates returned from Gemini.]"
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return "[Penguide: No content parts returned from Gemini.]"
            
        return parts[0].get("text", "")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "[Penguide: Invalid Google API Key.]"
        return f"[Penguide: Gemini API HTTP Error: {e}]"
    except requests.exceptions.Timeout:
        return "[Penguide: Gemini API took too long to respond.]"
    except Exception as e:
        return f"[Penguide: Error calling Gemini: {e}]"
