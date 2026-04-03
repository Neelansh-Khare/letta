# Letta Memory Benchmarks

This directory contains standardized evaluation benchmarks to measure and demonstrate Letta's memory system performance.

## Benchmarks Included

1. **LOCOMO (Long-Context Conversational Memory)**
   - Tests conversational memory recall and consistency over very long dialogues.
   - Measures accuracy of retrieving information from past conversations.
   - Location: `tests/benchmarks/locomo`

2. **MemBench**
   - Comprehensive memory evaluation suite.
   - Tests different memory operations (store, retrieve, update, delete).
   - Includes both synthetic tasks (`run_membench.py`) and real-world scenarios from the MemBench paper (`run_membench_real.py`).
   - Location: `tests/benchmarks/membench`

3. **LongMemEval**
   - Evaluates long-term memory retention across extended conversation sessions.
   - Location: `tests/benchmarks/longmemeval`

4. **EverMemBench**
   - Modern long-term memory benchmark with long group-dialogue histories and QA.
   - Location: `tests/benchmarks/evermembench`

5. **MemoryArena**
   - Agentic multi-session task benchmark with structured subtasks.
   - Location: `tests/benchmarks/memoryarena`

6. **CloneMem**
   - Long-horizon persona memory benchmark built from digital traces.
   - Location: `tests/benchmarks/clonemem`

7. **LongMemEvalS**
   - Alignment layer for the `S` variant already used by the current cleaned dataset path.
   - Location: `tests/benchmarks/longmemevals`

8. **EMemBench alignment**
   - Normalized text-mode alignment scaffold for exported EMemBench-style episodes.
   - Location: `tests/benchmarks/emembench`

## Prerequisites

- Letta server running locally.
- `letta-client` installed.
- Appropriate LLM provider (e.g., OpenAI, Ollama) configured.

## Contributor Docs

- [Contributor setup](./CONTRIBUTOR_SETUP.md)
- [Support matrix](./SUPPORT_MATRIX.md)

## Usage

### 0. Run Preflight Checks

Before starting a long benchmark run, validate the local setup:

```bash
uv run python tests/benchmarks/run_preflight.py \
  --benchmark locomo \
  --base_url http://localhost:8283 \
  --model ollama/llama3.1:latest \
  --data_path tests/benchmarks/locomo/data/locomo10.json \
  --output_path tests/benchmarks/locomo/results.json \
  --require-dataset
```

This preflight checks:
- Letta server reachability
- Model handle format
- Model availability from the Letta server
- Dataset presence
- Output directory readiness

### 1. Download Datasets

Before running the benchmarks, you must download the respective datasets:

```bash
# LOCOMO
uv run python tests/benchmarks/locomo/download_data.py

# MemBench
uv run python tests/benchmarks/membench/download_data.py

# LongMemEval
uv run python tests/benchmarks/longmemeval/download_data.py

# EverMemBench
uv run python tests/benchmarks/evermembench/download_data.py

# MemoryArena
uv run python tests/benchmarks/memoryarena/download_data.py

# CloneMem
uv run python tests/benchmarks/clonemem/download_data.py
```

*Note: The datasets are ignored by Git as they are too large for the repository.*

### 2. Run Benchmarks

Each benchmark can be run individually. Ensure your Letta server is running (`uv run letta server`).

```bash
# Run LOCOMO
uv run python tests/benchmarks/locomo/run_locomo.py --model ollama/llama3.1:latest --limit 10

# Run MemBench
uv run python tests/benchmarks/membench/run_membench.py --model ollama/llama3.1:latest --limit 10

# Run LongMemEval
uv run python tests/benchmarks/longmemeval/run_longmemeval.py --model ollama/llama3.1:latest --limit 10

# Run EverMemBench
uv run python tests/benchmarks/evermembench/run_evermembench.py --model ollama/llama3.1:latest --limit 10

# Run MemoryArena
uv run python tests/benchmarks/memoryarena/run_memoryarena.py --model ollama/llama3.1:latest --limit 10

# Run CloneMem
uv run python tests/benchmarks/clonemem/run_clonemem.py --model ollama/llama3.1:latest --limit 3

# Run LongMemEvalS alignment
uv run python tests/benchmarks/longmemevals/run_longmemevals.py --model ollama/llama3.1:latest --limit 10
```

### 3. Summarize Result Files

You can summarize one or more result JSON files with:

```bash
uv run python tests/benchmarks/summarize_results.py \
  tests/benchmarks/membench/results.json \
  tests/benchmarks/longmemeval/results.json
```

For machine-readable output:

```bash
uv run python tests/benchmarks/summarize_results.py \
  --format json \
  tests/benchmarks/membench/results.json
```

### Options

- `--base_url`: Letta server base URL (default: `http://localhost:8283`)
- `--data_path`: Path to the dataset JSON file.
- `--model`: Model handle to use for the agent (default: `ollama/llama3.1:latest`).
- `--limit`: Limit the number of items/tasks to process (useful for testing).
- `--output_path`: Path to save the detailed results.
- `--skip-preflight`: Skip benchmark preflight checks.

## Contributing

To add a new benchmark, create a new subdirectory and follow the pattern established by the existing ones:
- `download_data.py`: Script to download the dataset.
- `run_<benchmark>.py`: Runner script using the `BenchmarkRunner` from `tests/benchmarks/common/runner.py`.
- `README.md`: Specific instructions for the benchmark.
