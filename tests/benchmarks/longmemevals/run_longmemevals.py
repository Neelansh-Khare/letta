import argparse
import os

from letta_client import Letta
from tqdm import tqdm

from tests.benchmarks.common.preflight import assert_preflight_ok, print_preflight_report, run_benchmark_preflight
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import (
    average,
    build_output_payload,
    build_run_metadata,
    calculate_f1,
    default_benchmark_base_url,
    default_benchmark_model,
    extract_text_from_messages,
    load_json,
    save_json,
)

BENCHMARK_NAME = "longmemeval_s"


def run_longmemeval_s(args):
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

    if not os.path.exists(args.data_path):
        print(f"Data not found at {args.data_path}. Please download it first.")
        return

    data = load_json(args.data_path)

    if args.limit:
        data = data[:args.limit]

    results = []
    total_items = len(data)

    for item_idx, item in enumerate(tqdm(data, desc="Processing LongMemEvalS items")):
        print(f"[LongMemEvalS] Item {item_idx + 1}/{total_items}: creating agent")
        agent = client.agents.create(
            name=f"longmem_s_agent_{item_idx}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory and long-term context recall."},
                {"label": "human", "value": "I am a user engaged in a long-term conversation with you."},
            ],
        )

        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)

        sessions = item["haystack_sessions"]
        
        print(f"[LongMemEvalS] Item {item_idx + 1}/{total_items}: loading {len(sessions)} sessions")
        for session_idx, session in enumerate(sessions, start=1):
            runner.bulk_add_messages(session)

        question = item["question"]
        ground_truth = item["answer"]
        print(f"[LongMemEvalS] Item {item_idx + 1}/{total_items}: answering final question")
        response_messages = runner.run_interaction(f"Final Question based on our entire history: {question}\nAnswer briefly.")

        prediction = extract_text_from_messages(response_messages)
        last_interaction = runner.get_history()[-1]
        latency = last_interaction.get("latency_seconds", 0)
        usage = last_interaction.get("usage")
        memory_calls = last_interaction.get("memory_calls", [])
        f1 = calculate_f1(prediction, str(ground_truth))

        results.append({
            "item_idx": item_idx,
            "question": question,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "f1": f1,
            "latency_seconds": latency,
            "usage": usage,
            "memory_calls": memory_calls,
        })
        print(f"[LongMemEvalS] Item {item_idx + 1}/{total_items}: complete (f1={f1:.4f})")

        client.agents.delete(agent.id)

    overall_f1 = average(result["f1"] for result in results)
    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "overall_f1": overall_f1,
        "items_processed": len(results),
        "average_latency_seconds": average(item["latency_seconds"] for item in results),
        "total_latency_seconds": sum(item["latency_seconds"] for item in results),
        "usage": {
            "completion_tokens": sum(item.get("usage", {}).get("completion_tokens", 0) for item in results if item.get("usage")),
            "prompt_tokens": sum(item.get("usage", {}).get("prompt_tokens", 0) for item in results if item.get("usage")),
            "total_tokens": sum(item.get("usage", {}).get("total_tokens", 0) for item in results if item.get("usage")),
            "step_count": sum(item.get("usage", {}).get("step_count", 0) for item in results if item.get("usage")),
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
        payload = build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=results, metadata=metadata)
        save_json(payload, args.output_path)
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LongMemEvalS benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/longmemeval/data/longmemeval_s_cleaned.json", help="Path to LongMemEvalS JSON")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/longmemevals/results.json", help="Path to save results")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip benchmark preflight checks")

    args = parser.parse_args()
    run_longmemeval_s(args)
