Summary
Add standardized evaluation benchmarks to measure and demonstrate Letta's memory system performance, including LOCOMO, MemBench, and LongMemEval.

Motivation
Currently, Letta lacks any standardized benchmark or evaluation code to measure memory system performance. This makes it difficult to:

Quantify improvements: No way to measure if changes to memory systems actually help
Compare with alternatives: Cannot objectively compare Letta with other memory solutions (Mem0, MemAgent, etc.)
Validate claims: Hard to demonstrate Letta's effectiveness to potential users
Guide development: Without metrics, it's unclear which optimizations matter most
Recent research papers (Mem0, MemAgent) use standardized benchmarks to demonstrate their effectiveness:

Mem0 reports 26% improvement on LOCOMO benchmark
MemAgent shows results on various long-context tasks
Proposed Solution
Add evaluation scripts and documentation for the following benchmarks:

1. LOCOMO (Long-Context Conversational Memory)
Tests conversational memory recall and consistency
Measures accuracy of retrieving information from past conversations
Reference: Used by Mem0 (arXiv:2504.19413)
2. MemBench
Comprehensive memory evaluation suite
Tests different memory operations (store, retrieve, update, delete)
Reference: "A Survey on the Memory Mechanism of LLM-based Agents" (arXiv:2404.13501)
3. LongMemEval
Evaluates long-term memory retention
Tests memory across extended conversation sessions
Relevant issue: How can I implement LongMemEval testing on Letta? #2990 (closed) showed community interest
Implementation Suggestions
tests/
└── benchmarks/
    ├── locomo/
    │   ├── run_locomo.py
    │   └── README.md
    ├── membench/
    │   ├── run_membench.py
    │   └── README.md
    └── longmemeval/
        ├── run_longmemeval.py
        └── README.md
Each benchmark should:

Be runnable with a single command
Support different model configurations
Output standardized metrics (accuracy, recall, F1, etc.)
Generate comparison reports

Implementation Details
1.  **Project Setup**: 
    *   Create the proposed directory structure under `tests/benchmarks`.
    *   Each benchmark directory will contain the runner script, a README with instructions, and any specific data or configuration files.

2.  **Benchmark Adapters**:
    *   For each benchmark (LOCOMO, MemBench, LongMemEval), create an adapter that allows the benchmark to interact with the Letta memory system. 
    *   This will likely involve creating a `LettaAgent` with a specific persona and tools tailored for the benchmark's tasks.

3.  **Data Loading and Preprocessing**:
    *   The `run_<benchmark_name>.py` script for each benchmark will be responsible for loading the respective dataset.
    *   Implement data loaders to handle the specific format of each benchmark's data (e.g., JSON, CSV).
    *   Pre-process the data as needed to fit the input requirements of the Letta agent.

4.  **Execution Logic**:
    *   The core of each `run_<benchmark_name>.py` script will be the execution loop.
    *   This loop will iterate through the benchmark's test cases, send the appropriate prompts to the `LettaAgent`, and capture the agent's responses.
    *   The agent's memory state should be managed according to the benchmark's requirements (e.g., reset between tests, persisted across conversational turns).

5.  **Evaluation and Reporting**:
    *   After the execution loop is complete, the script will evaluate the agent's responses against the ground truth from the benchmark data.
    *   Implement functions to calculate the relevant metrics for each benchmark (e.g., accuracy for question answering, F1 score for information retrieval).
    *   The final output should be a clear report, possibly in both console output and a file (e.g., CSV, JSON), summarizing the results. This will allow for easy comparison across different runs and with other systems.

6.  **CI/CD Integration**:
    *   Consider integrating the benchmark runners into the CI/CD pipeline. 
    *   This will allow for continuous monitoring of memory performance and prevent regressions.
    *   Initially, these could be run manually, but the goal should be to automate them.

Benefits
Credibility: Objective metrics demonstrate Letta's effectiveness
Development guidance: Clear targets for optimization
Community engagement: Users can contribute benchmark results
Research alignment: Enables academic comparisons
References
LOCOMO: Long-Context Conversational Memory benchmark
MemBench: Memory evaluation suite from LLM agent survey
Mem0 paper (arXiv:2504.19413) - benchmark methodology
MemAgent paper (arXiv:2507.02259) - evaluation approaches
"A Survey on the Memory Mechanism of LLM-based Agents" (arXiv:2404.13501)
Additional Context
I'd be happy to contribute to implementing these benchmarks. This could start with a simple LOCOMO integration and expand from there.

Related closed issue: #2990 (LongMemEval testing question)

Activity

github-project-automation
added this to  🐛 Letta issue trackeron Dec 22, 2025

github-project-automation
moved this to To triage in  🐛 Letta issue trackeron Dec 22, 2025
github-actions
github-actions commented 3 weeks ago
github-actions
bot
3 weeks ago – with GitHub Actions
Contributor
This issue is stale because it has been open for 30 days with no activity.


github-actions
added 
stale
 3 weeks ago
Neelansh-Khare
Neelansh-Khare commented 3 weeks ago
Neelansh-Khare
3 weeks ago
is anyone working on this, or are you @Soein? I could take a look


github-actions
removed 
stale
 3 weeks ago
qdrddr
qdrddr commented 2 days ago
qdrddr
2 days ago
Also
OOLONG
MemoryAgentBench

Neelansh-Khare
Neelansh-Khare commented 2 days ago
Neelansh-Khare
2 days ago
Working on this since I don't think anyone else is