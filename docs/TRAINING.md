# Penguide — Training (Dataset + TensorFlow)

Training is **optional** and is intended to be run on another machine (e.g. another laptop). This repo only provides the scripts and data format.

## Overview

- **Dataset:** Fetched by `scripts/fetch_training_data.py` (Hugging Face + in-repo knowledge). Output: `data/training_pairs.jsonl` with `instruction` and `output` fields.
- **Training:** `scripts/train_tensorflow.py` reads that file and trains a small TensorFlow 2 model (LSTM-based seq2seq-style). You run this where you have GPU/CPU and time (e.g. another laptop).

## 1. Fetch training data (this machine or CI)

From the project root:

```bash
pip install datasets   # for Hugging Face
python scripts/fetch_training_data.py
```

- Exports `knowledge/kernel/*.md` as instruction–output pairs.
- Downloads a subset of `hrsvrn/linux-commands-json` from Hugging Face (size limited by `PENGUIDE_MAX_DATASET_ROWS`, default 50k).
- Writes `data/training_pairs.jsonl` (one JSON object per line: `{"instruction": "...", "output": "..."}`).

Optional env vars:

- `PENGUIDE_DATA_DIR` — directory for output (default: `./data`).
- `PENGUIDE_MAX_DATASET_ROWS` — max rows from HF dataset (default: 50000).

## 2. Copy data to the other laptop

Copy the whole project or at least:

- `data/training_pairs.jsonl`
- `scripts/train_tensorflow.py`
- `requirements-training.txt`

So that `train_tensorflow.py` can find `data/training_pairs.jsonl` (or set `--data` to the copied path).

## 3. Train on the other laptop

```bash
pip install -r requirements-training.txt
python scripts/train_tensorflow.py --epochs 3 --batch 32 --out ./saved_model
```

Options:

- `--data` — path to `.jsonl` file (default: `data/training_pairs.jsonl`).
- `--epochs` — number of epochs (default: 3).
- `--batch` — batch size (default: 32).
- `--max_samples` — cap number of training samples (optional).
- `--out` — directory to save the model (default: `./saved_model`).
- `--vocab_size` — tokenizer vocab size (default: 10000).
- `--seq_len` — max sequence length (default: 256).

Output:

- Saved model in `--out` (e.g. `saved_model/`).
- `tokenizer_config.json` in the same directory (vocab_size, seq_len).

## 4. Using the trained model

The current Penguide app uses **Ollama** for generation. This TensorFlow script trains a **separate** small model (LSTM) on the same (instruction, output) data. To use it inside Penguide you would:

- Add a TensorFlow inference path in `models/` (load `saved_model` and tokenizer config).
- Optionally use it as a fallback or for command-suggestion only when Ollama is unavailable.

That integration is not implemented in the repo yet; the scripts only prepare data and train the model so you can run training on another laptop.

## 5. Dependencies (training only)

- `requirements-training.txt`: `tensorflow`, `datasets` (and keep `requests` from main `requirements.txt` if you run fetch on the same env).
