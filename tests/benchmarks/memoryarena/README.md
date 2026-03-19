# MemoryArena for Letta

This benchmark evaluates Letta on the public MemoryArena dataset.

Current implementation notes:

- Loads the five public MemoryArena subsets from Hugging Face
- Ingests optional background context into Letta
- Evaluates each subtask with:
  - exact match
  - token F1
  - task success rate
  - average latency
