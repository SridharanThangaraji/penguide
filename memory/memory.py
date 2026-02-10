class Memory:
    def __init__(self):
        self.history = []

    def add(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_context(self):
        context = ""
        for entry in self.history:
            context += f"{entry['role'].capitalize()}: {entry['content']}\n"
        return context

    def clear(self):
        self.history = []
