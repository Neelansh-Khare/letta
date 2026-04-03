# EMemBench Alignment for Letta

EMemBench is a programmatic interactive benchmark centered on game trajectories rather than a simple static QA file.

This repository currently adds a normalized text-mode alignment path so contributors can start evaluating EMemBench-style exported trajectories with the existing Letta harness before the full interactive game environment is integrated.

Expected normalized input format:

```json
[
  {
    "episode_id": "text-game-001",
    "context": [
      "trajectory event 1",
      "trajectory event 2"
    ],
    "questions": [
      {
        "id": "q1",
        "question": "What item did the agent pick up first?",
        "answer": "rusty key"
      }
    ]
  }
]
```

Current evaluation:

- token F1
- exact match
- average latency

This is intentionally an alignment scaffold, not yet the full interactive EMemBench environment.
