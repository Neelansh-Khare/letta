# Benchmark Support Matrix

This matrix documents the current support intent for the benchmark harness. It is conservative on purpose: entries should represent what contributors can reasonably expect today, not what should eventually work.

## Operating Systems

| Operating System | Status | Notes |
| --- | --- | --- |
| macOS | Supported | Exercised during development. |
| Linux | Supported | Validated via GitHub Actions CI smoke tests. |
| Windows | Supported | Validated on local development environments. |

## Backend Paths

| Backend Path | Status | Notes |
| --- | --- | --- |
| Letta + local Ollama | Supported | Standard local benchmark path. |
| Letta + OpenAI-compatible hosted provider | Supported | Validated with GPT-4o-mini in CI. |

## Benchmarks

| Benchmark | Status | Notes |
| --- | --- | --- |
| LOCOMO | Supported | Standard baseline runner. |
| MemBench synthetic | Prototype | Useful smoke/development path. |
| MemBench real | Supported | Standard runner. |
| EverMemBench | Supported | Full Tier 1 runner implemented. |
| MemoryArena | Supported | Full Tier 1 runner implemented for agentic tasks. |
| CloneMem | Supported | Full Tier 1 runner implemented for digital traces. |
| LongMemEvalS | Supported | Full runner for the cleaned S variant. |
| EMemBench | Supported | Full runner for EMemBench episodes. |

## Interpretation

- `Partial`: implemented enough for active development, but not fully validated across contributor environments
- `Prototype`: runnable development scaffold, not yet a finished benchmark integration
- `Planned`: intended support target, not yet validated
- `Not started`: not implemented yet
