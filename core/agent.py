from configs.settings import OLLAMA_MODEL, GEMINI_MODEL, LLM_BACKEND

if LLM_BACKEND == "gemini":
    from models.gemini import ask
    DEFAULT_MODEL = GEMINI_MODEL
else:
    from models.ollama import ask
    DEFAULT_MODEL = OLLAMA_MODEL

class Agent:
    def __init__(self, model=None):
        self.model = model or DEFAULT_MODEL

    def think(self, prompt, context=""):
        full_prompt = f"{context}\n{prompt}" if context else prompt
        return ask(self.model, full_prompt)
