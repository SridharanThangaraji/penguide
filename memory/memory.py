from configs.settings import MEMORY_MAX_TURNS

class Memory:
    def __init__(self, max_turns=None):
        self.history = []
        self.max_turns = max_turns or MEMORY_MAX_TURNS

    def add(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_context(self):
        # Use only the last N turns to avoid token overflow
        recent = self.history[-self.max_turns:] if self.max_turns else self.history
        context = ""
        for entry in recent:
            context += f"{entry['role'].capitalize()}: {entry['content']}\n"
        return context

    def clear(self):
        self.history = []
