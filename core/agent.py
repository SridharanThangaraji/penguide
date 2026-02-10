from models.ollama import ask

class Agent:
    def __init__(self, model="mistral"):
        self.model = model

    def think(self, prompt):
        return ask(self.model, prompt)
