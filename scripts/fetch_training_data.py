#!/usr/bin/env python3
"""
Fetch and prepare training data for Penguide.
- Downloads a Linux/shell-related dataset from Hugging Face.
- Exports in-repo knowledge (knowledge/kernel/*.md) as instruction–output pairs.
Output is written under data/ for use by train_tensorflow.py.
Run from project root: python scripts/fetch_training_data.py
"""
import os
import json
import sys

# Project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.environ.get("PENGUIDE_DATA_DIR", os.path.join(ROOT, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

def export_knowledge_pairs():
    """Export knowledge/kernel/*.md as (instruction, output) pairs for training."""
    kb_path = os.path.join(ROOT, "knowledge", "kernel")
    pairs = []
    if not os.path.isdir(kb_path):
        return pairs
    for name in os.listdir(kb_path):
        if not name.endswith(".md"):
            continue
        path = os.path.join(kb_path, name)
        with open(path, "r") as f:
            content = f.read()
        topic = name.replace(".md", "").replace("-", " ").title()
        pairs.append({
            "instruction": f"Explain Linux kernel concept: {topic}.",
            "output": content.strip(),
        })
        pairs.append({
            "instruction": f"What does the kernel do regarding {topic.lower()}?",
            "output": content.strip(),
        })
    return pairs

def fetch_huggingface_dataset():
    """Download a Linux/shell-related dataset from Hugging Face."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets", file=sys.stderr)
        return []
    # hrsvrn/linux-commands-json: 1M rows; may have 'command', 'description', etc.
    # We take a subset and normalize to instruction/output if possible.
    try:
        ds = load_dataset("hrsvrn/linux-commands-json", split="train", trust_remote_code=True)
    except Exception as e:
        print(f"Dataset load failed: {e}", file=sys.stderr)
        return []
    rows = []
    # Limit size for local training
    max_rows = int(os.environ.get("PENGUIDE_MAX_DATASET_ROWS", "50000"))
    for i, row in enumerate(ds):
        if i >= max_rows:
            break
        if not isinstance(row, dict):
            continue
        # Prefer instruction/output if present (e.g. mrheinen/linux-commands style)
        if "instruction" in row and "output" in row:
            instr, out = str(row["instruction"]).strip(), str(row["output"]).strip()
            if instr and out:
                rows.append({"instruction": instr, "output": out})
            continue
        if "input" in row and "output" in row:
            inp, out = str(row["input"]).strip(), str(row["output"]).strip()
            if inp and out:
                rows.append({"instruction": f"What does the command '{inp}' do?", "output": f"{inp}\n{out}".strip()})
            continue
        # Fallback: command/description style (e.g. hrsvrn/linux-commands-json)
        cmd = row.get("command") or row.get("cmd") or row.get("name") or ""
        desc = row.get("description") or row.get("desc") or row.get("help") or ""
        if not cmd and not desc:
            continue
        instruction = f"What does the command '{cmd}' do?" if cmd else "Explain this Linux command."
        output = f"{cmd}: {desc}".strip() if desc else str(cmd).strip()
        if output:
            rows.append({"instruction": instruction, "output": output})
    return rows

def main():
    os.chdir(ROOT)
    all_pairs = []

    # 1) In-repo knowledge
    kb_pairs = export_knowledge_pairs()
    all_pairs.extend(kb_pairs)
    print(f"Exported {len(kb_pairs)} knowledge pairs from knowledge/kernel/")

    # 2) Hugging Face dataset
    hf_pairs = fetch_huggingface_dataset()
    all_pairs.extend(hf_pairs)
    print(f"Fetched {len(hf_pairs)} pairs from Hugging Face")

    if not all_pairs:
        print("No training pairs produced. Check paths and dataset.", file=sys.stderr)
        sys.exit(1)

    out_path = os.path.join(DATA_DIR, "training_pairs.jsonl")
    with open(out_path, "w") as f:
        for item in all_pairs:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {len(all_pairs)} pairs to {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
