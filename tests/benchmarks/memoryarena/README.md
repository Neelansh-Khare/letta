# MemoryArena for Letta

MemoryArena is a memory-centric benchmark for agentic tasks, introduced in **arXiv:2603.07670**. It evaluates an agent's ability to make active decisions based on multi-session history, rather than just passive recall.

## 1. Overview
MemoryArena tests how an LLM agent uses its memory to:
- **Formulate and update plans:** Adjusting future actions based on past results.
- **Track state across sessions:** Remembering progress and goals over multiple independent interactions.
- **Active decision-making:** Applying historical context to influence new choices.

## 2. Benchmark Data
The benchmark uses datasets from the **arXiv:2603.07670** survey. The data consists of multi-session scenarios where an agent is tasked with a specific objective that requires historical knowledge. Ensure you have `memoryarena_scenarios.json` in the `data/` directory.

## 3. Running the Benchmark

```bash
python -m tests.benchmarks.memoryarena.run_memoryarena --data_path tests/benchmarks/memoryarena/data/memoryarena_scenarios.json --model <your_model>
```

### Options:
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the MemoryArena JSON scenarios.
- `--model`: Model for the agent (default: openai/gpt-4o-mini).
- `--limit`: Limit the number of scenarios for quick testing.
- `--output_path`: Path to save JSON results.

## 4. Metrics
The script outputs:
- **Task Effectiveness:** Success rate of completing the assigned objectives.
- **Plan Completion:** Percentage of planned steps successfully executed across sessions.
- **Memory Quality (Precision/Recall):** Accuracy of information used in decision-making.

## 5. Comparison
MemoryArena highlights significant performance drops for models that excel in simple recall (like LOCOMO) but struggle with agentic tasks.
- **LOCOMO high-scorers:** Typically drop to **40–60%** on MemoryArena.
- **Letta/MemGPT:** (Pending your results) - MemoryArena is particularly well-suited for Letta's agentic memory architecture.
