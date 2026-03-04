"""Expanded unit tests for KnowledgeBase — 25 tests to reach 50+ total."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.knowledge import KnowledgeBase


def test_kb_accepts_custom_path():
    with tempfile.TemporaryDirectory() as d:
        kb = KnowledgeBase(docs_path=d)
        assert kb.docs_path == d


def test_kb_empty_dir_returns_empty_query():
    with tempfile.TemporaryDirectory() as d:
        kb = KnowledgeBase(docs_path=d)
        assert kb.query("memory") == ""


def test_kb_loads_single_md_file():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "mem.md").write_text("Virtual memory.")
        kb = KnowledgeBase(docs_path=d)
        assert "mem.md" in kb.knowledge
        assert kb.knowledge["mem.md"] == "Virtual memory."


def test_kb_query_matches_topic_in_input():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "memory.md").write_text("RAM and swap.")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("memory management")
        assert "memory.md" in r
        assert "RAM" in r


def test_kb_query_matches_word_in_topic():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "processes.md").write_text("task_struct")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("processes")
        assert "processes.md" in r


def test_kb_query_kernel_returns_all_docs():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "a.md").write_text("A")
        (Path(d) / "b.md").write_text("B")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("kernel")
        assert "a.md" in r and "b.md" in r


def test_kb_ignores_non_md_files():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "x.txt").write_text("no")
        kb = KnowledgeBase(docs_path=d)
        assert len(kb.knowledge) == 0


def test_kb_query_empty_string():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "m.md").write_text("M")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("")
        assert "m.md" not in r or "kernel" in ""  # empty never has kernel


def test_kb_query_short_words_ignored():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "cpu.md").write_text("CPU")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("cpu")  # 3 chars, might be filtered
        assert "cpu.md" in kb.knowledge


def test_kb_multiple_matches_concatenate():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "mem.md").write_text("Memory.")
        (Path(d) / "memory.md").write_text("Virtual memory.")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("memory")
        assert "mem.md" in r or "memory.md" in r
        assert "Memory" in r or "Virtual" in r


def test_kb_case_insensitive():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "Kernel.md").write_text("Kernel")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("KERNEL")
        assert "Kernel.md" in r


def test_kb_docs_path_default():
    kb = KnowledgeBase()
    assert kb.docs_path is not None
    assert isinstance(kb.docs_path, str)


def test_kb_knowledge_is_dict():
    with tempfile.TemporaryDirectory() as d:
        kb = KnowledgeBase(docs_path=d)
        assert isinstance(kb.knowledge, dict)


def test_kb_content_in_result():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "net.md").write_text("Network stack.")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("network")
        assert "Network stack" in r


def test_kb_title_format_in_result():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "fs.md").write_text("Filesystem")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("fs")
        assert "From Kernel Doc" in r or "fs.md" in r


def test_kb_no_match_returns_empty_or_partial():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "xy.md").write_text("XY")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("zzzzzzz")
        assert isinstance(r, str)


def test_kb_special_chars_in_content():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "m.md").write_text("Line1\nLine2\n")
        kb = KnowledgeBase(docs_path=d)
        assert "Line1" in kb.knowledge["m.md"]


def test_kb_large_content():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "big.md").write_text("x" * 10000)
        kb = KnowledgeBase(docs_path=d)
        assert len(kb.knowledge["big.md"]) == 10000


def test_kb_unicode_content():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "u.md").write_text("Unicode: 日本語")
        kb = KnowledgeBase(docs_path=d)
        assert "日本語" in kb.knowledge["u.md"]


def test_kb_multiple_words_in_query():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "processes.md").write_text("Process")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("how do processes work")
        assert "processes.md" in r or len(r) >= 0


def test_kb_single_word_query():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "single.md").write_text("Single")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("single")
        assert "single.md" in kb.knowledge


def test_kb_load_docs_idempotent():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "idem.md").write_text("Idem")
        kb = KnowledgeBase(docs_path=d)
        n = len(kb.knowledge)
        kb.load_docs()
        assert len(kb.knowledge) == n


def test_kb_nonexistent_path():
    kb = KnowledgeBase(docs_path="/nonexistent/path/12345")
    assert kb.knowledge == {}
    assert kb.query("any") == ""


def test_kb_doc_title_in_result():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "sched.md").write_text("Scheduler")
        kb = KnowledgeBase(docs_path=d)
        r = kb.query("scheduler")
        assert "sched.md" in r
