#!/usr/bin/env python3
"""
TensorFlow 2 training script for Penguide-style (instruction, output) data.
Uses a small transformer-based sequence model or a simple LSTM for learning
instruction -> output mapping. Run on the machine where you want to train
(e.g. another laptop). Data is read from data/training_pairs.jsonl produced
by fetch_training_data.py.

Usage (from project root):
  pip install -r requirements-training.txt
  python scripts/train_tensorflow.py [--epochs 3] [--batch 32] [--out ./saved_model]
"""
import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.environ.get("PENGUIDE_DATA_DIR", os.path.join(ROOT, "data"))
DATA_FILE = os.path.join(DATA_DIR, "training_pairs.jsonl")

def load_data(path, max_samples=None):
    pairs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pairs.append(json.loads(line))
            if max_samples and len(pairs) >= max_samples:
                break
    return pairs

def main():
    parser = argparse.ArgumentParser(description="Train TensorFlow model on instruction-output pairs")
    parser.add_argument("--data", default=DATA_FILE, help="Path to .jsonl training data")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch", type=int, default=32, help="Batch size")
    parser.add_argument("--max_samples", type=int, default=None, help="Cap training samples")
    parser.add_argument("--out", default=os.path.join(ROOT, "saved_model"), help="Output model directory")
    parser.add_argument("--vocab_size", type=int, default=10000, help="Tokenizer vocab size")
    parser.add_argument("--seq_len", type=int, default=256, help="Max sequence length")
    args = parser.parse_args()

    if not os.path.isfile(args.data):
        print(f"Data file not found: {args.data}. Run scripts/fetch_training_data.py first.", file=sys.stderr)
        sys.exit(1)

    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
        from tensorflow.keras.preprocessing.text import Tokenizer
        from tensorflow.keras.preprocessing.sequence import pad_sequences
    except ImportError:
        print("Install TensorFlow: pip install tensorflow", file=sys.stderr)
        sys.exit(1)

    pairs = load_data(args.data, args.max_samples)
    if not pairs:
        print("No samples in data file.", file=sys.stderr)
        sys.exit(1)

    instructions = [p["instruction"] for p in pairs]
    outputs = [p["output"] for p in pairs]

    # Simple tokenizer on combined text
    all_text = instructions + outputs
    tokenizer = Tokenizer(num_words=args.vocab_size, oov_token="<OOV>", filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
    tokenizer.fit_on_texts(all_text)

    X = tokenizer.texts_to_sequences(instructions)
    Y = tokenizer.texts_to_sequences(outputs)
    X = pad_sequences(X, maxlen=args.seq_len, padding="post", truncating="post")
    Y = pad_sequences(Y, maxlen=args.seq_len, padding="post", truncating="post")

    # Model: embed -> LSTM -> dense (same seq_len, vocab_size) for next-token style or classification
    # Here we do a simple seq2seq-style setup: input seq -> output seq (teacher forcing omitted for brevity)
    vocab_size = min(args.vocab_size, len(tokenizer.word_index) + 1)
    embedding_dim = 128
    lstm_units = 128

    model = keras.Sequential([
        layers.Embedding(vocab_size, embedding_dim, input_length=args.seq_len),
        layers.LSTM(lstm_units, return_sequences=True),
        layers.LSTM(lstm_units, return_sequences=True),
        layers.Dense(vocab_size, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    # Target: (batch, seq_len) integer indices for sparse_categorical_crossentropy
    model.fit(X, Y, batch_size=args.batch, epochs=args.epochs, validation_split=0.1)

    os.makedirs(args.out, exist_ok=True)
    model.save(args.out)
    with open(os.path.join(args.out, "tokenizer_config.json"), "w") as f:
        json.dump({"vocab_size": vocab_size, "seq_len": args.seq_len}, f)
    print(f"Model and config saved to {args.out}")

if __name__ == "__main__":
    main()
