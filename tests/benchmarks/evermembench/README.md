# EverMemBench for Letta

This benchmark evaluates Letta on the public EverMemBench Dynamic dataset.

Current implementation notes:

- Uses the public dialogue and QA files from `EverMind-AI/EverMemBench-Dynamic`
- Ingests multi-day group dialogue into Letta as textual context
- Evaluates question answering with:
  - token F1
  - exact match
  - multiple-choice accuracy when options are present
  - average latency

## Usage

```bash
uv run python tests/benchmarks/evermembench/download_data.py
uv run python tests/benchmarks/evermembench/run_evermembench.py \
  --model ollama/llama3.1:latest \
  --limit 10
```
