# Benchmark Contributor Setup

This document defines the current benchmark setup contract for open-source contributors working on Letta's benchmark harness.

## Scope

This setup contract is for the benchmark harness under `tests/benchmarks/`. It is intentionally narrower than the full Letta application setup and focuses on what contributors need in order to run benchmark preflight checks and small benchmark smoke runs reliably.

## Minimum Environment

- Python `3.11` to `3.13`
- `uv`
- A working Letta server
- A model handle exposed by the Letta server
- Benchmark datasets downloaded locally for benchmarks that require them

## Supported Setup Pattern Today

The harness supports both local and hosted LLMs:

- **Local**: Letta server running on `http://localhost:8283` with local Ollama (`ollama/llama3.1:latest`).
- **Hosted**: Letta server configured with OpenAI or other hosted providers (`openai/gpt-4o-mini`).

Example environment variables:

```bash
export LETTA_BENCHMARK_BASE_URL="http://localhost:8283"
export LETTA_BENCHMARK_MODEL="openai/gpt-4o-mini"
export OPENAI_API_KEY="sk-..."
```

## Contributor Workflow

1. Sync dependencies:

```bash
uv sync --all-extras
```

2. Start the Letta server in a separate terminal:

```bash
uv run letta server
```

3. Validate benchmark readiness before running a benchmark:

```bash
uv run python tests/benchmarks/run_preflight.py \
  --benchmark membench \
  --base_url http://localhost:8283 \
  --model ollama/llama3.1:latest \
  --data_path tests/benchmarks/membench/data/membench_synthetic.json \
  --output_path tests/benchmarks/membench/results.json
```

4. Run a tiny benchmark slice:

```bash
uv run python tests/benchmarks/membench/run_membench.py \
  --base_url http://localhost:8283 \
  --model ollama/llama3.1:latest \
  --limit 1
```

## Regression Analysis

After running a benchmark, you can compare the current results with a baseline to check for regressions:

```bash
uv run python tests/benchmarks/compare_results.py \
  baseline_results.json \
  tests/benchmarks/evermembench/results.json \
  --fail-on-regression
```

## Dataset Expectations

- `LOCOMO`: dataset required
- `MemBench synthetic`: dataset optional, falls back to generated synthetic data
- `MemBench real`: dataset required
- `LongMemEvalS`: dataset required

Use the benchmark download scripts before running required-dataset benchmarks.

## Output Contract

Current benchmark result files include:

- benchmark name
- summary
- details
- run metadata
- environment metadata:
  - schema version
  - platform
  - Python runtime details
  - selected benchmark-related environment variables
  - git commit when available

This is intended to make results more comparable across contributor setups.

## Known Limitations

- The benchmark suite is currently in an active stabilization phase.
- Some advanced metrics (like staleness and deletion compliance) are implemented but require specific dataset labeling to be fully exercised.

## Expectations For New Benchmark Work

When adding or refactoring a benchmark:

- Use model handles in `<provider>/<model>` format.
- Ensure the `BenchmarkRunner` correctly captures `memory_calls` for traceability.
- Add or update tests for new shared helper behavior.
- Use the smoke test lane (`--limit 1` or `--limit 2`) to verify functionality before long runs.
