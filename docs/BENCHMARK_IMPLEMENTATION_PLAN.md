# Letta Memory Benchmark Implementation Plan

This document outlines the plan for implementing standardized evaluation benchmarks to measure and demonstrate Letta's memory system performance.

## 1. High-Level Plan

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

## 2. Directory Structure

The following directory structure has been created:

```
tests/
└── benchmarks/
    ├── common/
    │   ├── __init__.py
    │   ├── runner.py        # Common benchmark runner
    │   └── utils.py         # Utility functions (data loading, F1 calculation)
    ├── locomo/
    │   ├── run_locomo.py    # LOCOMO benchmark script
    │   ├── download_data.py # Script to download the LOCOMO dataset
    │   ├── README.md
    │   └── data/
    ├── membench/
    │   ├── run_membench.py  # MemBench operations test script
    │   ├── README.md
    │   └── data/            # Contains synthetic and real data
    └── longmemeval/
        ├── run_longmemeval.py # Long-term memory retention script
        ├── README.md
        └── data/
```

## 3. Phase 1: Foundation and LOCOMO Benchmark (COMPLETED)

### 3.1. Common Evaluation Framework (`tests/benchmarks/common/`)

*   **`runner.py`**: Contains `BenchmarkRunner` for agent interactions.
*   **`utils.py`**: Includes functions for JSON handling and token-level F1-score calculation.

### 3.2. LOCOMO Implementation (`tests/benchmarks/locomo/`)

*   **Data**: Download script provided. LOCOMO is sourced from `snap-research/locomo`.
*   **`run_locomo.py`**: Iterates through datasets, feeds conversations to Letta agents, and evaluates with F1-score.

## 4. Phase 2: MemBench Implementation (COMPLETED)

*   **`run_membench.py`**: Tests Store, Retrieve, Update, and Delete operations using synthetic data (with support for real MemBench data).
*   **Metrics**: Accuracy of operation success and F1-score for retrievals.

## 5. Phase 3: LongMemEval Implementation (COMPLETED)

*   **`run_longmemeval.py`**: Processes long-form, multi-session chat histories from the LongMemEval dataset (`xiaowu0162/longmemeval-cleaned`).
*   **Metrics**: F1-score for long-term recall.

## 6. Phase 4: Reporting and CI Integration (PLANNED)

*   **Standardized Reports**: Ensure consistent machine-readable (JSON) output across all runners.
*   **CI Integration**: Add GitHub Action workflows to track performance over time on memory-related changes.
