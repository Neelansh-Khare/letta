# MemoryArena for Letta

MemoryArena is a memory-centric benchmark for agentic tasks, introduced in **arXiv:2603.07670**. It evaluates an agent's ability to make active decisions based on multi-session history, rather than just passive recall.

This benchmark evaluates Letta on the public MemoryArena dataset.

## 1. Overview
MemoryArena tests how an LLM agent uses its memory to:
- **Formulate and update plans:** Adjusting future actions based on past results.
- **Track state across sessions:** Remembering progress and goals over multiple independent interactions.
- **Active decision-making:** Applying historical context to influence new choices.

## 2. Implementation Notes
- Loads the public MemoryArena subsets (e.g., from Hugging Face).
- Ingests optional background context into Letta.
- Evaluates each subtask with:
  - exact match (EM)
  - token F1
  - task success rate
  - average latency

## 3. Running the Benchmark

Ensure you have the `memoryarena_scenarios.json` file in the `data/` directory.

```bash
uv run python tests/benchmarks/memoryarena/run_memoryarena.py \
  --model openai/gpt-4o-mini \
  --limit 10
```

### Options:
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the MemoryArena JSON scenarios.
- `--model`: Model for the agent (e.g., `openai/gpt-4o-mini`, `ollama/llama3.1:latest`).
- `--limit`: Limit the number of scenarios for quick testing.
- `--output_path`: Path to save JSON results.

## 4. Metrics
The script outputs:
- **Task Effectiveness:** Success rate of completing the assigned objectives.
- **Plan Completion:** Percentage of planned steps successfully executed across sessions.
- **Memory Quality (Precision/Recall/F1):** Accuracy of information used in decision-making.
- **Exact Match (EM)**
- **Average Latency**

## 5. Comparison
MemoryArena highlights significant performance drops for models that excel in simple recall (like LOCOMO) but struggle with agentic tasks.
- **LOCOMO high-scorers:** Typically drop to **40–60%** on MemoryArena.
- **Letta/MemGPT:** (Pending your results) - MemoryArena is particularly well-suited for Letta's agentic memory architecture.
