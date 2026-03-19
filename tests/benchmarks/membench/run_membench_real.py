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

BENCHMARK_NAME = "membench_real"


def run_membench_real(args):
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
    items = data.get("roles", [])

    if args.limit:
        items = items[:args.limit]

    results = []
    total_items = len(items)

    for item_idx, item in enumerate(tqdm(items, desc="Running MemBench Real"), start=1):
        tid = item.get("tid")
        message_list = item.get("message_list", [])
        qa = item.get("QA", {})
        total_messages = sum(len(sub_list) for sub_list in message_list)
        print(f"[MemBench Real] Item {item_idx}/{total_items}: tid={tid}, messages={total_messages}")

        agent = client.agents.create(
            name=f"membench_real_agent_{tid}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {"label": "human", "value": "I am a user sharing information with you."},
            ],
        )

        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)

        for sub_list_idx, sub_list in enumerate(message_list, start=1):
            print(f"[MemBench Real] Item {item_idx}/{total_items}: segment {sub_list_idx}/{len(message_list)}")
            for msg_obj in sub_list:
                user_msg = msg_obj.get("user_message")
                if user_msg:
                    runner.run_interaction(user_msg)

        question = qa.get("question")
        ground_truth = qa.get("answer")

        if not question or not ground_truth:
            client.agents.delete(agent.id)
            continue

        print(f"[MemBench Real] Item {item_idx}/{total_items}: answering final QA")
        response_messages = runner.run_interaction(f"Question: {question}\nAnswer briefly.")

        prediction = extract_text_from_messages(response_messages)
        f1 = calculate_f1(prediction, str(ground_truth))

        results.append({
            "tid": tid,
            "question": question,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "f1": f1,
        })
        print(f"[MemBench Real] Item {item_idx}/{total_items}: complete (f1={f1:.4f})")

        client.agents.delete(agent.id)

    overall_f1 = average(result["f1"] for result in results)

    print("\nMemBench Real Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Overall F1 Score: {overall_f1:.4f}")

    if args.output_path:
        summary = {
            "benchmark": BENCHMARK_NAME,
            "model": args.model,
            "base_url": args.base_url,
            "overall_f1": overall_f1,
            "items_processed": len(results),
        }
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MemBench Real benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/membench/data/MemData/FirstAgent/simple.json", help="Path to MemBench real dataset")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/membench/results_real.json", help="Path to save results")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip benchmark preflight checks")

    args = parser.parse_args()
    run_membench_real(args)
