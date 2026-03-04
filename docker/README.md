# Docker — Penguide

Build and run the Penguide CLI in a container. Requires Ollama (and a model) to be available; run with `--network host` or point `OLLAMA_HOST` to the host.

## 1. Build the image

From the **project root** (`penguide/`):

```bash
docker build -t penguide -f docker/Dockerfile .
```

## 2. Run (interactive)

Use the host network so the container can reach Ollama on the host:

```bash
docker run --rm -it --network host -e OLLAMA_HOST=http://127.0.0.1:11434 penguide
```

To use a different model:

```bash
docker run --rm -it --network host -e OLLAMA_MODEL=phi penguide
```

## 3. Show help only

Default CMD shows help:

```bash
docker run --rm penguide
```

## Note

Ollama must be running on the host (or in another container). Pull a model first, e.g. `ollama pull mistral`.
