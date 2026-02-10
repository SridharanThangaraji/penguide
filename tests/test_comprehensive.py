import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.orchestrator import Orchestrator
from core.knowledge import KnowledgeBase
from core.prompt import SYSTEM_PROMPT

class TestPenguideComprehensive(unittest.TestCase):
    def setUp(self):
        self.orch = Orchestrator()

    def test_branding(self):
        """Verify the agent identifies as Penguide."""
        self.assertIn("Penguide", SYSTEM_PROMPT)

    def test_knowledge_retrieval(self):
        """Verify KB retrieves kernel info for specific keywords."""
        result = self.orch.kb.query("memory management")
        self.assertIn("memory.md", result)
        self.assertIn("Virtual Memory", result)

    def test_memory_retention(self):
        """Verify history is maintained across steps."""
        self.orch.step("Hello")
        self.orch.step("What did I just say?")
        # Each step adds 3 entries when simulated (user, tool output from fallback, assistant reply)
        self.assertEqual(len(self.orch.memory.history), 6)

    def test_policy_enforcement(self):
        """Verify restricted commands are still filtered via shell.run (implicitly called via orchestrator if Agent suggests it)."""
        # We can't easily mock the Agent's decision here without more effort, 
        # but we can test tools/shell.py directly.
        from tools.shell import run
        self.assertEqual(run("sudo rm -rf /"), "")
        self.assertEqual(run("chmod +x script.sh"), "")
        # Valid command
        output = run("pwd")
        self.assertTrue(len(output) > 0)

    @patch('models.ollama.requests.post')
    def test_educational_format(self, mock_post):
        """Verify orchestrator parses explanation and RUN command."""
        # Mock successful Ollama response with explanation + RUN
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "I will show you the path.\nRUN: pwd"}
        mock_post.return_value = mock_response

        result = self.orch.step("where am i")
        self.assertIn("I will show you the path", result)
        self.assertIn("> Executing: pwd", result)

if __name__ == "__main__":
    unittest.main()
