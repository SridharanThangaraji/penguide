from core.agent import Agent
from tools.shell import run
from core.prompt import SYSTEM_PROMPT
import re

class Orchestrator:
    def __init__(self):
        self.agent = Agent()

    def step(self, user_input):
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}"
        reply = self.agent.think(prompt).strip()

        # Match RUN even if not at column 0
        match = re.search(r'RUN:\s*(.+)', reply)

        if match:
            cmd = match.group(1).strip()
            return run(cmd).strip()

        return reply.splitlines()[0]
