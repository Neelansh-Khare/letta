# LOCOMO Benchmark for Letta

This benchmark evaluates Letta's long-term memory capabilities using the LOCOMO (Long-Context Conversational Memory) dataset.

## Dataset
The dataset consists of long, multi-session dialogues between two speakers, with associated question-answer pairs that test memory of events and details across the entire conversation.

## Metrics
- **F1 Score**: Token-level F1 score comparing the agent's response to the ground truth answer.

## Running the Benchmark

1. **Ensure Letta server is running**:
   ```bash
   letta server
   ```

2. **Download the data** (if not already present):
   ```bash
   python tests/benchmarks/locomo/download_data.py
   ```

3. **Run the benchmark**:
   ```bash
   python tests/benchmarks/locomo/run_locomo.py --model openai/gpt-4o-mini --limit 5
   ```

## Options
- `--base_url`: Letta server URL (default: http://localhost:8283)
- `--data_path`: Path to the LOCOMO JSON file
- `--model`: LLM model to use for the agent
- `--limit`: Number of conversation items to process (useful for quick testing)
- `--output_path`: Path to save the JSON results
