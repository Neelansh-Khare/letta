import argparse

from letta_client import Letta
from tqdm import tqdm

from tests.benchmarks.common.metrics import average_latency, exact_match, f1_for_any
from tests.benchmarks.common.preflight import assert_preflight_ok, print_preflight_report, run_benchmark_preflight
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import (
    average,
    build_output_payload,
    build_run_metadata,
    default_benchmark_base_url,
    default_benchmark_model,
    extract_text_from_messages,
    load_json,
    save_json,
)

BENCHMARK_NAME = "emembench_alignment"


def run_emembench(args):
    if not args.skip_preflight:
        preflight_results = run_benchmark_preflight(
            benchmark_name=BENCHMARK_NAME,
            base_url=args.base_url,
            model=args.model,
            data_path=args.data_path,
            output_path=args.output_path,
            require_dataset=True,
        )
        print_preflight_report(preflight_results)
        assert_preflight_ok(preflight_results)

    client = Letta(base_url=args.base_url)
    episodes = load_json(args.data_path)
    if args.limit:
        episodes = episodes[: args.limit]

    details = []
    for episode in tqdm(episodes, desc="EMemBench episodes"):
        agent = client.agents.create(
            name=f"emembench_{episode.get('episode_id')}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with episodic memory."},
                {"label": "human", "value": "I am evaluating your memory over a trajectory-derived episode."},
            ],
        )
        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)
        runner.ingest_text_entries([str(entry) for entry in episode.get("context", [])], batch_size=20)

        for question in episode.get("questions", []):
            response_messages, latency = runner.run_interaction_timed(question["question"])
            prediction = extract_text_from_messages(response_messages)
            last_interaction = runner.get_history()[-1]
            details.append(
                {
                    "episode_id": episode.get("episode_id"),
                    "question_id": question.get("id"),
                    "question": question.get("question"),
                    "answer": question.get("answer"),
                    "prediction": prediction,
                    "f1": f1_for_any(prediction, question.get("answer", "")),
                    "exact_match": exact_match(prediction, question.get("answer", "")),
                    "latency_seconds": latency,
                    "usage": last_interaction.get("usage"),
                    "memory_calls": last_interaction.get("memory_calls", []),
                }
            )

        client.agents.delete(agent.id)

    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "items_processed": len(details),
        "overall_f1": average(item["f1"] for item in details),
        "exact_match_rate": average(item["exact_match"] for item in details),
        "average_latency_seconds": average_latency(item["latency_seconds"] for item in details),
        "total_latency_seconds": sum(item["latency_seconds"] for item in details),
        "usage": {
            "completion_tokens": sum(item.get("usage", {}).get("completion_tokens", 0) for item in details if item.get("usage")),
            "prompt_tokens": sum(item.get("usage", {}).get("prompt_tokens", 0) for item in details if item.get("usage")),
            "total_tokens": sum(item.get("usage", {}).get("total_tokens", 0) for item in details if item.get("usage")),
            "step_count": sum(item.get("usage", {}).get("step_count", 0) for item in details if item.get("usage")),
        },
    }
    if args.output_path:
        metadata = build_run_metadata(
            benchmark_name=BENCHMARK_NAME,
            model=args.model,
            base_url=args.base_url,
            data_path=args.data_path,
            limit=args.limit,
            output_path=args.output_path,
        )
        save_json(build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=details, metadata=metadata), args.output_path)
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EMemBench alignment benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url())
    parser.add_argument("--model", type=str, default=default_benchmark_model())
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/emembench/data/emembench_alignment.json")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/emembench/results.json")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()
    run_emembench(args)
