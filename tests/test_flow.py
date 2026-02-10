import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.orchestrator import Orchestrator
from core.knowledge import KnowledgeBase

def test_knowledge_base():
    print("Testing KnowledgeBase...")
    kb = KnowledgeBase()
    result = kb.query("process management")
    assert "processes.md" in result
    assert "task_struct" in result
    print("KnowledgeBase query passed!")

def test_educational_response():
    print("Testing Educational Response Flow...")
    orch = Orchestrator()
    # Simulate a user query about memory
    response = orch.step("How does memory management work?")
    print(f"Agent Response Snippet: {response[:100]}...")
    assert len(response) > 50 # Should have an explanation
    print("Educational flow passed!")

if __name__ == "__main__":
    try:
        test_knowledge_base()
        test_educational_response()
        print("\nAll educational tests passed!")
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
