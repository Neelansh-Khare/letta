# EverMemBench for Letta

EverMemBench is a comprehensive memory evaluation suite for LLM agents, introduced in **arXiv:2602.01313**. It focuses on multi-hop reasoning, temporal reasoning, and memory awareness across large-scale conversation traces (~2,400 QA pairs, 10K turns, ~1M tokens).

This benchmark evaluates Letta on the public EverMemBench Dynamic dataset.

## 1. Overview
EverMemBench addresses limitations in LOCOMO where models that score near-perfectly on passive recall often plummet to much lower performance on more complex reasoning tasks. It specifically tests:
- **Single-hop recall:** Retrieving a single fact.
- **Multi-hop reasoning:** Chaining evidence from multiple conversational turns.
- **Temporal reasoning:** Understanding event lifecycles and the order of information.
- **Memory awareness:** Proactively applying constraints based on previous knowledge.

## 2. Implementation Notes
- Uses the public dialogue and QA files from `EverMind-AI/EverMemBench-Dynamic`.
- Ingests multi-day group dialogue into Letta as textual context.
- Evaluates question answering with:
  - token F1
  - exact match
  - multiple-choice accuracy when options are present
  - average latency

## 3. Running the Benchmark

Ensure you have the `evermembench_data.json` file in the `data/` directory.

```bash
uv run python tests/benchmarks/evermembench/download_data.py
uv run python tests/benchmarks/evermembench/run_evermembench.py \
  --model openai/gpt-4o-mini \
  --limit 10
```

### Options:
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the EverMemBench JSON dataset.
- `--model`: Model for the agent (e.g., `openai/gpt-4o-mini`, `ollama/llama3.1:latest`).
- `--limit`: Limit the number of items to process for quick testing.
- `--output_path`: Path to save JSON results.

## 4. Metrics
The script outputs:
- **Overall F1 Score**
- **Exact Match (EM)**
- **Multiple-choice accuracy**
- **Single-hop accuracy**
- **Multi-hop accuracy**
- **Temporal reasoning accuracy**
- **Memory awareness score**
- **Average Latency**

## 5. Comparison
Published baselines (from arXiv:2602.01313):
- **Mem0:** 37.09%
- **MemOS:** 42.55%
- **Zep:** 39.97%
- **Gemini-3-Flash:** 72.61% (full-context)
- **Letta/MemGPT:** (Pending your results)
