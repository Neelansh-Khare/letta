# Next Steps: Letta Memory Benchmark Suite

This document tracks the remaining tasks to reach 100% completion of the benchmark implementation as defined in `issue_3115.md` and the `BENCHMARK_IMPLEMENTATION_PLAN.md`.

## 1. Advanced Metrics (The "Metric Stack")
Expand the `tests/benchmarks/common/metrics.py` and runner logic to include deeper memory evaluation beyond basic accuracy.

- **Memory Quality:**
  - [ ] **Staleness:** Implement detection for when an agent retrieves or uses outdated information when newer context is available.
  - [ ] **Contradiction Detection:** Implement checks (likely LLM-based) to identify when an agent's memory or response asserts facts that conflict with the ground truth or its own prior state.
  - [ ] **Multi-hop Attribution:** Implement quality checks for tasks requiring evidence from multiple disparate conversation segments.
- **Governance:**
  - [ ] **Deletion Compliance:** Implement automated verification that "forget" or "delete" operations successfully remove data from the agent's accessible memory.
  - [ ] **Traceability:** Add hooks to log which specific memory blocks or archival segments were used to generate a response.

## 2. Automation & CI/CD
Integrate the benchmark harness into the repository's continuous integration pipeline.

- [ ] **Smoke Test Workflow:** Create `.github/workflows/benchmarks.yml` to run a minimal slice (`--limit 2`) of Tier 1 benchmarks on PRs.
- [ ] **Regression Analysis Tool:** Build a utility to compare `results.json` files and highlight performance drops.

## 3. Cross-Platform Validation
Ensure the benchmark harness is "first-class" on all major operating systems.

- [ ] **Validation:** Verify preflight and Tier 1 runners on Windows and Linux.
- [ ] **Documentation:** Update `SUPPORT_MATRIX.md` and `CONTRIBUTOR_SETUP.md` once validated.

## 4. Final Alignment of Tier 2
Bring the remaining benchmarks up to the new harness standard.

- [ ] **LongMemEvalS:** Fully migrate from the legacy `longmemeval` structure to the cleaned `S` variant.
- [ ] **EMemBench:** Complete the alignment layer for exported interactive episodes.
