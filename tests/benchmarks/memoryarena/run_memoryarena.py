import argparse
import json
from pathlib import Path

from letta_client import Letta
from tqdm import tqdm

from tests.benchmarks.common.metrics import average_latency, exact_match, f1_for_any, task_success_rate
from tests.benchmarks.common.preflight import assert_preflight_ok, print_preflight_report, run_benchmark_preflight
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import (
    average,
    build_output_payload,
    build_run_metadata,
    default_benchmark_base_url,
    default_benchmark_model,
    extract_text_from_messages,
    save_json,
)

BENCHMARK_NAME = "memoryarena"


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_tasks(data_dir: str) -> list[tuple[str, dict]]:
    tasks = []
    for file_path in sorted(Path(data_dir).glob("*/data.jsonl")):
        subset = file_path.parent.name
        for row in load_jsonl(str(file_path)):
            tasks.append((subset, row))
    return tasks


def coerce_backgrounds(item: dict) -> list[str]:
    backgrounds = item.get("backgrounds")
    if backgrounds is None:
        base_person = item.get("base_person")
        if isinstance(base_person, dict):
            texts = [base_person.get("query", "")]
            if base_person.get("daily_plans"):
                texts.append(json.dumps(base_person["daily_plans"], ensure_ascii=True))
            return [text for text in texts if text]
        return []
    if isinstance(backgrounds, str):
        return [backgrounds]
    if isinstance(backgrounds, list):
        return [json.dumps(entry, ensure_ascii=True) if isinstance(entry, (dict, list)) else str(entry) for entry in backgrounds]
    return [str(backgrounds)]


def stringify_answer(answer):
    if isinstance(answer, (dict, list)):
        return json.dumps(answer, ensure_ascii=True, sort_keys=True)
    return str(answer)


def run_memoryarena(args):
    if not args.skip_preflight:
        preflight_results = run_benchmark_preflight(
            benchmark_name=BENCHMARK_NAME,
            base_url=args.base_url,
            model=args.model,
            data_path=args.data_dir,
            output_path=args.output_path,
            require_dataset=True,
        )
        print_preflight_report(preflight_results)
        assert_preflight_ok(preflight_results)

    client = Letta(base_url=args.base_url)
    tasks = load_tasks(args.data_dir)
    if args.limit:
        tasks = tasks[: args.limit]

    results = []
    for index, (subset, task) in enumerate(tqdm(tasks, desc="MemoryArena tasks"), start=1):
        print(f"[MemoryArena] Task {index}/{len(tasks)} subset={subset} id={task.get('id')}")
        agent = client.agents.create(
            name=f"memoryarena_{subset}_{task.get('id')}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant solving multi-session tasks."},
                {"label": "human", "value": "I am evaluating your memory across a structured task sequence."},
            ],
        )
        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)

        backgrounds = coerce_backgrounds(task)
        if backgrounds:
            runner.ingest_text_entries([f"[MemoryArena][Background] {entry}" for entry in backgrounds], batch_size=10)

        subtasks = []
        latencies = []
        for subtask_idx, (question, answer) in enumerate(zip(task.get("questions", []), task.get("answers", [])), start=1):
            response_messages, latency = runner.run_interaction_timed(str(question))
            prediction = extract_text_from_messages(response_messages)
            answer_text = stringify_answer(answer)
            subtask_result = {
                "subset": subset,
                "task_id": task.get("id"),
                "subtask_index": subtask_idx,
                "question": question,
                "answer": answer,
                "prediction": prediction,
                "f1": f1_for_any(prediction, answer_text),
                "exact_match": exact_match(prediction, answer_text),
                "latency_seconds": latency,
                "usage": runner.get_history()[-1].get("usage"),
            }
            subtasks.append(subtask_result)
            latencies.append(latency)

        results.append(
            {
                "subset": subset,
                "task_id": task.get("id"),
                "subtasks": subtasks,
                "task_success_rate": task_success_rate(item["exact_match"] for item in subtasks),
                "average_latency_seconds": average_latency(latencies),
                "total_latency_seconds": sum(latencies),
            }
        )
        client.agents.delete(agent.id)

    flattened = [subtask for task in results for subtask in task["subtasks"]]
    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "tasks_processed": len(results),
        "subtasks_processed": len(flattened),
        "overall_f1": average(item["f1"] for item in flattened),
        "exact_match_rate": average(item["exact_match"] for item in flattened),
        "task_success_rate": average(item["task_success_rate"] for item in results),
        "average_latency_seconds": average(item["latency_seconds"] for item in flattened),
        "total_latency_seconds": sum(item["latency_seconds"] for item in flattened),
        "usage": {
            "completion_tokens": sum(item.get("usage", {}).get("completion_tokens", 0) for item in flattened if item.get("usage")),
            "prompt_tokens": sum(item.get("usage", {}).get("prompt_tokens", 0) for item in flattened if item.get("usage")),
            "total_tokens": sum(item.get("usage", {}).get("total_tokens", 0) for item in flattened if item.get("usage")),
            "step_count": sum(item.get("usage", {}).get("step_count", 0) for item in flattened if item.get("usage")),
        },
    }
    if args.output_path:
        metadata = build_run_metadata(
            benchmark_name=BENCHMARK_NAME,
            model=args.model,
            base_url=args.base_url,
            data_path=args.data_dir,
            limit=args.limit,
            output_path=args.output_path,
        )
        save_json(
            build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=results, metadata=metadata), args.output_path
        )
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MemoryArena on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url())
    parser.add_argument("--model", type=str, default=default_benchmark_model())
    parser.add_argument("--data_dir", type=str, default="tests/benchmarks/memoryarena/data")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/memoryarena/results.json")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()
    run_memoryarena(args)
