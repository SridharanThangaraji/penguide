from models.ollama import ask

class Agent:
    def __init__(self, model="mistral"):
        self.model = model

    def think(self, prompt, context=""):
        full_prompt = f"{context}\n{prompt}" if context else prompt
        return ask(self.model, full_prompt)
