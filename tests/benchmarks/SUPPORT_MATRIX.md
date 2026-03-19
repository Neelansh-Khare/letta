# Benchmark Support Matrix

This matrix documents the current support intent for the benchmark harness. It is conservative on purpose: entries should represent what contributors can reasonably expect today, not what should eventually work.

## Operating Systems

| Operating System | Status | Notes |
| --- | --- | --- |
| macOS | Partial | Current branch has been exercised here during development. |
| Linux | Planned | Should be supported in principle, but not validated in this branch yet. |
| Windows | Planned | Intended support target, but not validated in this branch yet. |

## Backend Paths

| Backend Path | Status | Notes |
| --- | --- | --- |
| Letta + local Ollama | Partial | Primary dev path in the current branch. |
| Letta + OpenAI-compatible hosted provider | Planned | Harness is moving toward provider-agnostic behavior, but this path needs explicit validation. |
| Letta + cloud-native provider-specific setup | Planned | Possible future target after the harness contract stabilizes. |

## Benchmarks

| Benchmark | Status | Notes |
| --- | --- | --- |
| LOCOMO | Prototype | Runnable with current harness, still legacy/prototype scoped. |
| MemBench synthetic | Prototype | Useful smoke/development path. |
| MemBench real | Prototype | Runner exists; real benchmark parity still needs work. |
| LongMemEval | Prototype | Runner exists; alignment to LongMemEvalS remains future work. |
| EverMemBench | Not started | Planned Tier 1 target. |
| MemoryArena | Not started | Planned Tier 1 target. |
| CloneMem | Not started | Planned Tier 1 target. |

## Interpretation

- `Partial`: implemented enough for active development, but not fully validated across contributor environments
- `Prototype`: runnable development scaffold, not yet a finished benchmark integration
- `Planned`: intended support target, not yet validated
- `Not started`: not implemented yet
