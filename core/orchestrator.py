from core.agent import Agent
from tools.shell import run
from core.prompt import SYSTEM_PROMPT
from memory.memory import Memory
from core.knowledge import KnowledgeBase
import re

class Orchestrator:
    def __init__(self):
        self.agent = Agent()
        self.memory = Memory()
        self.kb = KnowledgeBase()

    def step(self, user_input):
        # Retrieve relevant kernel documentation
        kb_context = self.kb.query(user_input)
        history_context = self.memory.get_context()
        
        full_context = f"{history_context}\n{kb_context}" if kb_context else history_context
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}"
        
        reply = self.agent.think(prompt, full_context).strip()
        self.memory.add("user", user_input)

        # Match RUN even if not at column 0
        match = re.search(r'RUN:\s*(.+)', reply)

        if match:
            cmd = match.group(1).strip()
            # Everything before RUN: is the explanation
            explanation = reply[:match.start()].strip()
            
            output = run(cmd).strip()
            combined_response = f"{explanation}\n\n> Executing: {cmd}\n{output}" if explanation else output
            
            if output:
                self.memory.add("tool", output)
            
            self.memory.add("assistant", combined_response)
            return combined_response

        self.memory.add("assistant", reply)
        return reply
