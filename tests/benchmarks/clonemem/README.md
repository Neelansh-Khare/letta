# CloneMem for Letta

This benchmark evaluates Letta on the public CloneMem dataset.

Current implementation notes:

- Supports the published English JSON files in the `100k` and `500k` releases
- Ingests digital traces as timestamped memory entries
- Evaluates:
  - token F1
  - exact match
  - multiple-choice accuracy when `correct_choice_id` is present
  - average latency
