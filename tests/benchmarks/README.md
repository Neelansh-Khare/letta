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

## Prerequisites

- Letta server running locally.
- `letta-client` installed.
- Appropriate LLM provider (e.g., OpenAI, Ollama) configured.

## Usage

### 1. Download Datasets

Before running the benchmarks, you must download the respective datasets:

```bash
# LOCOMO
uv run python tests/benchmarks/locomo/download_data.py

# MemBench
uv run python tests/benchmarks/membench/download_data.py

# LongMemEval
uv run python tests/benchmarks/longmemeval/download_data.py
```

*Note: The datasets are ignored by Git as they are too large for the repository.*

### 2. Run Benchmarks

Each benchmark can be run individually. Ensure your Letta server is running (`uv run letta server`).

```bash
# Run LOCOMO
uv run python tests/benchmarks/locomo/run_locomo.py --model openai/gpt-4o-mini --limit 10

# Run MemBench
uv run python tests/benchmarks/membench/run_membench.py --model openai/gpt-4o-mini --limit 10

# Run LongMemEval
uv run python tests/benchmarks/longmemeval/run_longmemeval.py --model openai/gpt-4o-mini --limit 10
```

### Options

- `--base_url`: Letta server base URL (default: `http://localhost:8283`)
- `--data_path`: Path to the dataset JSON file.
- `--model`: Model to use for the agent (default: `openai/gpt-4o-mini`).
- `--limit`: Limit the number of items/tasks to process (useful for testing).
- `--output_path`: Path to save the detailed results.

## Contributing

To add a new benchmark, create a new subdirectory and follow the pattern established by the existing ones:
- `download_data.py`: Script to download the dataset.
- `run_<benchmark>.py`: Runner script using the `BenchmarkRunner` from `tests/benchmarks/common/runner.py`.
- `README.md`: Specific instructions for the benchmark.
