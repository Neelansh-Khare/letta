# MemBench Benchmark for Letta

This benchmark evaluates Letta's memory performance across fundamental operations: Store, Retrieve, Update, and Delete.

## Dataset
The benchmark uses a suite of tasks that simulate interaction scenarios where information is provided, queried, changed, or removed.

## Metrics
- **Accuracy**: Percentage of steps successfully completed (retrieval matching expected values, or old info being successfully updated/deleted).
- **F1 Score**: For retrieval tasks, token-level F1 score.

## Running the Benchmark

1. **Ensure Letta server is running**:
   ```bash
   letta server
   ```

2. **Run the benchmark**:
   ```bash
   python tests/benchmarks/membench/run_membench.py --model openai/gpt-4o-mini
   ```

## Options
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the MemBench JSON file (will use synthetic data if not found)
- `--model`: LLM model to use for the agent
- `--limit`: Number of tasks to process
- `--output_path`: Path to save the JSON results
