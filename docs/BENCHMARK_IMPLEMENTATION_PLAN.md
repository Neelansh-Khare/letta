# Letta Memory Benchmark Implementation Plan

This document tracks the implementation status for memory benchmarks in this repository. It replaces the earlier "COMPLETED" framing with the repo's actual state: benchmark scaffolding exists, but the suite is not yet aligned with the updated 2026 benchmark landscape or with a reproducible evaluation standard.

## 1. Current Status

1.  **Phase 1: Foundation and LOCOMO Benchmark (COMPLETED)**
    *   Set up basic directory structure for benchmarks.
    *   Developed a common evaluation framework (`tests/benchmarks/common/`).
    *   Implemented the LOCOMO benchmark (`tests/benchmarks/locomo/`).
2.  **Phase 2: MemBench Implementation (COMPLETED)**
    *   Integrated the MemBench suite to test various memory operations (`tests/benchmarks/membench/`).
3.  **Phase 3: LongMemEval Implementation (COMPLETED)**
    *   Integrated the LongMemEval benchmark for long-term memory retention (`tests/benchmarks/longmemeval/`).
4.  **Phase 4: Reporting and CI Integration (PLANNED)**
    *   Implement standardized reporting for all benchmarks.
    *   Integrate benchmark runs into the CI/CD pipeline.
5.  **Phase 5: EverMemBench and MemoryArena Implementation (IN PROGRESS)**
    *   Integrate EverMemBench for high-scale, multi-hop, and temporal reasoning (`tests/benchmarks/evermembench/`).
    *   Integrate MemoryArena for multi-session agentic tasks (`tests/benchmarks/memoryarena/`).

### What already exists

- Common benchmark utilities under `tests/benchmarks/common/`
- Prototype runners for:
  - `tests/benchmarks/locomo/`
  - `tests/benchmarks/membench/`
  - `tests/benchmarks/longmemeval/`
- Dataset download helpers
- A simple aggregate entrypoint in `tests/benchmarks/run_all.py`
- Shared output payload helpers for benchmark summaries and details
- Shared benchmark preflight checks in `tests/benchmarks/common/preflight.py`
- A standalone preflight entrypoint in `tests/benchmarks/run_preflight.py`
- Per-step progress logging in the existing prototype runners
- Targeted tests for common helpers, runner behavior, and preflight validation

### What is still missing

- First-class support for newer Tier 1 benchmarks:
  - EverMemBench
  - MemoryArena
  - CloneMem
- A contributor-friendly benchmark environment contract:
  - Required env vars
  - Supported provider/model handle examples
  - Dataset prerequisites
  - Expected server setup
- Cross-platform validation for macOS, Linux, and Windows contributor setups
- Preflight validation that fails fast when server, datasets, or model handles are misconfigured
- A more complete reproducibility manifest:
  - System/platform details
  - Python/runtime details
  - Benchmark schema versioning
  - Optional source-control provenance
- Broader evaluation metrics beyond basic accuracy/F1
- CI-friendly smoke runs and regression reporting

## 2. Status by Area

1. Benchmark framework: `PARTIAL`
   - Shared runner/output/preflight building blocks now exist, but the harness still needs richer manifests, metric coverage, and more benchmark integrations.

2. LOCOMO: `PARTIAL`
   - Implemented as a runnable prototype.
   - Should be retained as a legacy baseline, not treated as the main target benchmark.

3. MemBench: `PARTIAL`
   - Current support includes synthetic tasks and does not yet represent a strong standardized benchmark pipeline.

4. LongMemEval: `PARTIAL`
   - Existing code is a starting point, but should be aligned with the newer LongMemEvalS direction where applicable.

5. Modern 2026 benchmark coverage: `IN PROGRESS`
   - EverMemBench and MemoryArena are under development. CloneMem is not yet implemented.

6. Contributor portability: `PARTIAL`
   - Preflight checks now exist, but the contributor setup contract and explicit support matrix are still incomplete.

7. Reporting and CI: `NOT STARTED`
   - No durable benchmark report schema or regression workflow yet.

## 2.1 Recently Completed

- Removed the Ollama hardcoding from the shared message-capture path by deriving provider/model from the benchmark model handle.
- Standardized the current runners around a shared output payload shape.
- Added a benchmark preflight flow that validates server reachability, model-handle validity, model availability, dataset presence, and output-path readiness.
- Added live per-step progress output so long benchmark items do not appear stalled.
- Added targeted unit coverage for helper, runner, and preflight behavior.

## 3. Directory Structure

The following directory structure has been updated:

```
tests/
└── benchmarks/
    ├── common/
    │   ├── __init__.py
    │   ├── runner.py        # Common benchmark runner
    │   ├── utils.py         # Utility functions (data loading, F1 calculation)
    │   └── preflight.py      # Benchmark preflight checks
    ├── locomo/
    │   ├── run_locomo.py    # LOCOMO benchmark script
    │   ├── download_data.py # Script to download the LOCOMO dataset
    │   ├── README.md
    │   └── data/
    ├── membench/
    │   ├── run_membench.py  # MemBench operations test script
    │   ├── README.md
    │   └── data/            # Contains synthetic and real data
    ├── longmemeval/
    │   ├── run_longmemeval.py # Long-term memory retention script
    │   ├── README.md
    │   └── data/
    ├── evermembench/
    │   ├── run_evermembench.py # EverMemBench script
    │   ├── README.md
    │   └── data/
    ├── memoryarena/
    │   ├── run_memoryarena.py # MemoryArena script
    │   ├── README.md
    │   └── data/
    ├── run_all.py            # Aggregate entrypoint
    └── run_preflight.py      # Standalone preflight entrypoint
```

## 4. Recommended Benchmark Portfolio

### Tier 1

- EverMemBench
- MemoryArena
- CloneMem

### Tier 2

- LongMemEvalS
- EMemBench
- LOCOMO

### Watchlist

- MemoryRewardBench
- OOLONG
- MemoryAgentBench

## 5. Metric Stack

The suite should report at least the following categories:

1. Task effectiveness
   - Success rate
   - Completion quality
   - Final-answer correctness

2. Memory quality
   - Precision / recall / F1
   - Staleness
   - Contradictions
   - Update correctness
   - Temporal reasoning
   - Multi-hop attribution

3. Efficiency
   - Latency
   - Token usage
   - Embedding usage
   - Storage growth

4. Governance
   - Deletion compliance
   - Traceability
   - Retention correctness

## 6. Implementation Phases

### Phase 0: Audit and cleanup (COMPLETED)

- Review and document the current `tests/benchmarks/` code.
- Remove or update outdated docs that claim completion.
- Mark current runners as prototype or legacy where needed.

### Phase 1: Harness hardening (IN PROGRESS)

- Define a shared runner interface.
- Remove provider-specific assumptions from common helpers.
- Add structured config manifests for each run.
- Add shared result schema and metadata schema.
- Add instrumentation for latency, token usage, and storage metrics.
- Add a benchmark preflight validator for:
  - Letta server reachability
  - Model handle format
  - Dataset presence
  - Required environment variables
  - Friendly error messages before long-running execution starts
- Define a benchmark environment contract for contributors:
  - Supported Python versions
  - Required services
  - Example local and hosted backend configurations
  - Expected output locations
- Document a support matrix for tested backends and operating systems.
- Expand benchmark manifests with machine/runtime provenance so benchmark outputs can be compared across contributor setups more safely.

### Phase 2: Tier 1 integrations (IN PROGRESS)

- Implement EverMemBench. (IN PROGRESS)
- Implement MemoryArena. (IN PROGRESS)
- Implement CloneMem.

### Phase 3: Supplementary and legacy coverage

- Keep LOCOMO as a baseline floor.
- Upgrade LongMemEval support toward LongMemEvalS.
- Add EMemBench if it fits the standardized harness cleanly.

### Phase 4: Reporting and regression workflows

- Add consolidated report generation.
- Add benchmark comparison utilities.
- Add smoke-sized CI runs.
- Document full offline/manual benchmark runs.
- Add portability-oriented smoke coverage:
  - One lightweight local-backend flow
  - One hosted/OpenAI-compatible flow where available
  - Documentation for expected behavior on macOS, Linux, and Windows

## 7. Practical Guidance for Current Repo Work

While the harness is being upgraded:

- Reuse the current benchmark directory structure.
- Preserve working download scripts and any useful dataset adapters.
- Prefer incremental refactors over wholesale rewrites where possible.
- Treat current output files and example results as development artifacts, not final benchmark evidence.
- Avoid introducing new local-machine assumptions without documenting them in the benchmark environment contract.
- Prefer preflight validation and clear setup errors over late failures during benchmark execution.

## 8. Exit Criteria

This effort is in good shape when:

- Tier 1 benchmarks are runnable end to end.
- Legacy benchmarks are clearly labeled and intentionally scoped.
- Reporting is reproducible and comparable across runs.
- Local and hosted model backends can be benchmarked through the same harness.
- Contributors have a documented setup contract and a preflight command that verifies benchmark readiness before a run.
- At least a minimal cross-platform path is documented and validated for open-source contributors.
- Letta can be evaluated credibly against current memory-system baselines.
