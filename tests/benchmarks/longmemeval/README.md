# LongMemEval Benchmark for Letta

This benchmark evaluates Letta's long-term memory capabilities over extended, multi-session chat histories.

## Dataset
The benchmark uses the LongMemEval dataset, which contains long-form conversations with specific questions designed to test information extraction, temporal reasoning, and multi-session synthesis.

## Metrics
- **F1 Score**: Token-level F1 score comparing the agent's final answer to the ground truth.

## Running the Benchmark

1. **Ensure Letta server is running**:
   ```bash
   letta server
   ```

2. **Download the data**:
   The data can be found on Hugging Face at `xiaowu0162/longmemeval-cleaned`. Download `longmemeval_s_cleaned.json` (small) or `longmemeval_m_cleaned.json` (medium) and place them in the `tests/benchmarks/longmemeval/data/` directory.

3. **Run the benchmark**:
   ```bash
   python tests/benchmarks/longmemeval/run_longmemeval.py --model openai/gpt-4o-mini --limit 5
   ```

## Options
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the LongMemEval JSON file
- `--model`: LLM model to use for the agent
- `--limit`: Number of conversation items to process
- `--output_path`: Path to save the JSON results
