from models.ollama import ask
from configs.settings import OLLAMA_MODEL

class Agent:
    def __init__(self, model=None):
        self.model = model or OLLAMA_MODEL

    def think(self, prompt, context=""):
        full_prompt = f"{context}\n{prompt}" if context else prompt
        return ask(self.model, full_prompt)
