Summary
Issue #3115 should no longer be framed as "add LOCOMO, MemBench, and LongMemEval and call it done." The repository now contains partial benchmark scaffolding under `tests/benchmarks/`, but the benchmark landscape has shifted and the current implementation is not yet standardized, reproducible, or publication-grade.

---
### Update: 2026 Q1 Benchmark Landscape Has Evolved Significantly
Since this issue was filed, the memory evaluation field has moved fast. Several 2026 papers expose critical limitations in the benchmarks originally proposed here (LOCOMO, MemBench, LongMemEval) and introduce stronger alternatives. Here is an updated proposal.

#### LOCOMO Is Approaching Saturation
A comprehensive 2026 survey (arXiv:2603.07670) found that "models that score near-perfectly on LoCoMo plummet to 40–60% in MemoryArena". The survey identifies MemGPT/Letta as a key hierarchical memory system (Pattern C: tiered memory with prompted control) but notes the absence of standardized evaluation.

#### New Benchmarks Worth Adding
**Tier 1: Recommended**

| Benchmark | Paper | Scale | Key Insight |
| :--- | :--- | :--- | :--- |
| **EverMemBench** | arXiv:2602.01313 | 2,400 QA, 10K turns, ~1M tokens | Multi-hop reasoning drops to 26% despite 97.65% single-hop; temporal reasoning collapses to 7–45%. Mem0 scored 37.09%, MemOS 42.55%, Zep 39.97%, while Gemini-3-Flash hit 72.61%. |
| **MemoryArena** | cited in arXiv:2603.07670 | Multi-session agentic tasks | Where LOCOMO high-scorers plummet to 40–60%. Tests active decision-making, not just passive recall. |
| **CloneMem** | arXiv:2601.07023 | ~5K QA, 10 personas, 1-3 year traces | 8 task types (factual → counterfactual). Simple flat retrieval outperformed Mem0 and A-Mem. |

**Tier 2: Supplementary**

| Benchmark | Paper | Key Feature |
| :--- | :--- | :--- |
| **LongMemEvalS** | arXiv:2603.16862 | 500 questions, 6 categories. Chronos achieved 95.60% SOTA. |
| **EMemBench** | arXiv:2601.16690 | Interactive gameplay-based, 6 memory skills, "far from saturated". |
| **LOCOMO** | (legacy) | Useful only as baseline floor. |

#### Evaluation Should Go Beyond Recall/Accuracy
The survey (arXiv:2603.07670) proposes a four-layer metric stack:
1. **Task effectiveness** — success rates, plan completion
2. **Memory quality** — precision/recall, staleness, contradictions
3. **Efficiency** — latency, token cost, storage growth
4. **Governance** — privacy/deletion compliance

EverMemBench adds critical dimensions: temporal reasoning (event lifecycles), multi-hop attribution (cross-group evidence chaining), and memory awareness (proactive constraint application).

#### Letta Is Missing From Comparisons
EverMemBench already has published baselines for Mem0, Zep, MemOS, and MemoBase. Letta/MemGPT is absent. Adding benchmark support would establish Letta's position in the field — especially on MemoryArena, which tests agentic memory (Letta's core differentiator).

#### References (All 2026)
* **Benchmarks:** EverMemBench (2602.01313), CloneMem (2601.07023), EMemBench (2601.16690), MemoryRewardBench (2601.11969), Chronos/LongMemEvalS (2603.16862)
* **Surveys:** Memory for Autonomous LLM Agents (2603.07670), Anatomy of Agentic Memory (2602.19320), Graph-based Agent Memory (2602.05665)

I'd be happy to submit a PR implementing these benchmarks for Letta. The recommended starting point would be **EverMemBench + MemoryArena** — EverMemBench has published baselines to compare against, and MemoryArena most clearly differentiates passive recall from agentic memory.

@cpacker Would this direction be useful? Is benchmark integration on the roadmap?
---

Updated Goal
Build a credible benchmark suite for Letta's memory system that:

- Measures Letta on modern memory benchmarks that better reflect 2026 agentic-memory evaluation.
- Produces reproducible results that can be compared with published baselines.
- Evaluates more than recall alone: quality, task success, efficiency, and governance.
- Makes Letta's hierarchical/agentic memory design legible in head-to-head comparisons.

Why This Issue Needs Reframing
When this issue was opened, LOCOMO, MemBench, and LongMemEval were reasonable starting points. Since then, newer 2026 work has highlighted major gaps in older benchmarks:

- LOCOMO is useful as a baseline floor, but is increasingly saturated.
- MemoryArena better stresses active, agentic memory decisions.
- EverMemBench exposes failure modes that older recall-heavy benchmarks miss, especially multi-hop reasoning and temporal reasoning.
- CloneMem tests realistic long-horizon persona memory and counterfactual memory tasks where simple retrieval baselines can outperform poorly structured memory systems.

Per the latest issue discussion, the benchmark set should be updated to reflect this newer landscape.

Current Repository Status
There is already partial implementation work in the repo:

- `tests/benchmarks/common/`
- `tests/benchmarks/locomo/`
- `tests/benchmarks/membench/`
- `tests/benchmarks/longmemeval/`
- `tests/benchmarks/run_all.py`

What exists today is best described as prototype scaffolding, not completed benchmark support.

Recent progress already landed in this branch:

- Shared output payload helpers for benchmark runners
- Provider/model handling derived from model handles rather than a hardcoded Ollama assumption
- Shared benchmark preflight checks plus a standalone preflight CLI entrypoint
- Per-step progress logging in the current runners
- Targeted tests for helper logic, runner behavior, and preflight checks

Current gaps in the existing code:

1. Benchmark coverage is outdated.
   - The current tree focuses on LOCOMO, MemBench, and LongMemEval only.
   - It does not yet cover EverMemBench, MemoryArena, or CloneMem.

2. Some implementations are synthetic or incomplete.
   - `run_membench.py` falls back to synthetic tasks rather than a standardized benchmark workflow.
   - The current runners do not yet establish publication-quality parity with external benchmark protocols.

3. Model/provider handling is not standardized.
   - Benchmark utilities still contain local assumptions such as hardcoded Ollama capture behavior.
   - Default model examples still point to `openai/gpt-4o-mini` rather than a documented benchmark matrix.

4. Metrics are too narrow.
   - Current runners focus mostly on simple F1/accuracy-style outputs.
   - They do not yet implement the broader metric stack now expected for memory evaluation.

5. Reproducibility is still incomplete.
   - The branch now has a shared output payload shape, but the manifest still needs richer provenance details and schema hardening.
   - We still need stronger guarantees around dataset/version/run comparability.

6. CI and regression tracking are missing.
   - There is no lightweight smoke benchmark lane or artifact-based benchmark history.

7. Contributor portability is only partially addressed.
   - Fast preflight checks now exist for server availability, dataset presence, and model-handle validity.
   - The remaining gap is a documented setup contract and support matrix for macOS, Linux, and Windows contributors.

Updated Benchmark Priorities
Tier 1: Recommended for first-class support

1. EverMemBench
   - Large-scale benchmark with long interaction histories and stronger coverage of temporal reasoning, multi-hop attribution, and memory awareness.
   - Important because published comparisons already include systems like Mem0, Zep, MemOS, and MemoBase, while Letta is absent.

2. MemoryArena
   - High-priority benchmark for active, agentic memory behavior.
   - Especially relevant for Letta because it tests memory-guided decision making, not just passive recall.

3. CloneMem
   - Valuable for long-horizon personal memory and counterfactual tasks.
   - Useful for testing whether Letta's structured memory actually beats flat retrieval baselines.

Tier 2: Supplementary support

1. LongMemEvalS
   - Keep as a targeted long-term recall benchmark, but align to the updated "S" variant where possible.

2. EMemBench
   - Add as an interactive supplementary benchmark once the core evaluation harness is stable.

3. LOCOMO
   - Retain as a legacy baseline floor, not the main success criterion.

Watchlist / nice-to-have

- MemoryRewardBench
- OOLONG
- MemoryAgentBench

Metric Stack We Should Implement
The benchmark suite should report more than answer correctness. The evaluation plan should track four layers:

1. Task effectiveness
   - Task success
   - Plan completion
   - Final-answer correctness

2. Memory quality
   - Precision / recall / F1 where appropriate
   - Staleness
   - Contradictions
   - Update correctness
   - Temporal reasoning accuracy
   - Multi-hop attribution quality

3. Efficiency
   - End-to-end latency
   - LLM token usage
   - Embedding usage
   - Storage growth
   - Retrieval volume / cost

4. Governance
   - Deletion compliance
   - Data isolation
   - Memory editability / traceability
   - Privacy-sensitive retention checks where benchmark design permits

Recommended Scope for This Issue
This issue should cover the benchmark framework and the first wave of credible integrations, not every benchmark in the literature.

Recommended deliverables:

1. Stabilize the benchmark harness.
   - Standardize runner interfaces.
   - Remove hardcoded provider assumptions from common utilities.
   - Support reproducible config manifests for model/provider/dataset versions.

2. Reclassify existing benchmark code as prototype support.
   - Keep current LOCOMO / MemBench / LongMemEval code where useful.
   - Mark it clearly as incomplete or legacy where appropriate.

3. Add first-class Tier 1 benchmark support.
   - EverMemBench
   - MemoryArena
   - CloneMem

4. Retain legacy/supplementary support.
   - LOCOMO as baseline floor
   - LongMemEvalS as supplementary recall benchmark
   - EMemBench as optional follow-on

5. Standardize reporting.
   - Shared JSON result schema
   - Per-run metadata manifest
   - Aggregate comparison table generation

6. Add regression-friendly automation.
   - Small smoke subsets runnable in CI
   - Full benchmark runs documented for manual/offline execution

7. Make the benchmark suite contributor-friendly.
   - Add a documented environment contract for OSS users.
   - Add a preflight validator that fails fast on setup issues.
   - Define and maintain a minimal support matrix for tested backends and operating systems.

Proposed Implementation Plan
Phase 0: Audit and cleanup

- Audit existing code in `tests/benchmarks/`.
- Identify what can be reused versus replaced.
- Remove misleading "completed" claims from docs.

Phase 1: Benchmark framework hardening

- Define a common benchmark contract.
- Add provider-agnostic ingestion and execution helpers.
- Add structured result and metadata schemas.
- Add timing / token / storage instrumentation hooks.
- Add benchmark preflight validation for:
  - Letta server connectivity
  - Dataset availability
  - Model handle format
  - Required environment variables
- Add a contributor-facing benchmark setup contract that documents:
  - Supported Python versions
  - Expected Letta server setup
  - Supported backend examples
  - Local versus hosted run expectations

Phase 2: Modern benchmark integrations

- Implement EverMemBench runner.
- Implement MemoryArena runner.
- Implement CloneMem runner.

Phase 3: Legacy and supplementary alignment

- Keep LOCOMO as a baseline runner.
- Align LongMemEval support with the current LongMemEvalS direction.
- Add EMemBench if dataset and workflow fit the harness cleanly.

Phase 4: Comparison and regression workflows

- Add result summarization scripts.
- Add documented benchmark presets for local and hosted models.
- Add CI smoke runs on tiny benchmark slices.
- Add portability-oriented smoke checks and documentation for contributor setups across supported operating systems.

Definition of Done
This issue should be considered complete when:

- Letta has reproducible benchmark runners for at least the Tier 1 set.
- Existing prototype runners are either upgraded or explicitly documented as legacy/prototype.
- Reports include effectiveness, memory-quality, efficiency, and governance dimensions where applicable.
- Results are easy to rerun and compare across models/providers.
- Contributors can validate benchmark readiness with a preflight step before starting long runs.
- The benchmark setup contract and minimum cross-platform support expectations are documented.
- Letta can be positioned in the modern memory-benchmark landscape with defensible methodology.

References Mentioned In Issue Discussion
Benchmarks:

- EverMemBench (arXiv:2602.01313)
- CloneMem (arXiv:2601.07023)
- EMemBench (arXiv:2601.16690)
- MemoryRewardBench (arXiv:2601.11969)
- Chronos / LongMemEvalS (arXiv:2603.16862)
- MemoryArena (as cited in arXiv:2603.07670)
- LOCOMO (legacy baseline)

Surveys / framing papers:

- Memory for Autonomous LLM Agents (arXiv:2603.07670)
- Anatomy of Agentic Memory (arXiv:2602.19320)
- Graph-based Agent Memory (arXiv:2602.05665)

Working Interpretation
The work already in this repo is still useful, but it should be treated as a starting point for a more up-to-date benchmark program rather than as the finished implementation of #3115.
