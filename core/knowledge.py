import os
from configs.settings import KNOWLEDGE_PATH, KB_MAX_CHARS

class KnowledgeBase:
    def __init__(self, docs_path=None):
        self.docs_path = docs_path or KNOWLEDGE_PATH
        self.knowledge = {}
        self.load_docs()

    def load_docs(self):
        if not os.path.exists(self.docs_path):
            return
        for filename in os.listdir(self.docs_path):
            if filename.endswith(".md"):
                path = os.path.join(self.docs_path, filename)
                with open(path, "r") as f:
                    self.knowledge[filename] = f.read()

    def query(self, user_input):
        relevant_context = ""
        user_input_lower = user_input.lower()
        
        # Simple keyword matching for demo/education purposes
        for title, content in self.knowledge.items():
            # Check if title or content matches keywords
            topic = title.replace(".md", "").lower()
            
            # Match if the topic is in the input, or if any part of the input is in the topic
            if topic in user_input_lower or any(word in topic for word in user_input_lower.split() if len(word) > 3):
                relevant_context += f"\n--- From Kernel Doc: {title} ---\n{content}\n"
            elif "kernel" in user_input_lower:
                 relevant_context += f"\n--- From Kernel Doc: {title} ---\n{content}\n"
        
        if KB_MAX_CHARS and len(relevant_context) > KB_MAX_CHARS:
            relevant_context = relevant_context[:KB_MAX_CHARS] + "\n[... truncated for low-resource mode ...]"
        return relevant_context
