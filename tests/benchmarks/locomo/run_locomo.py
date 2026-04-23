import argparse

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

BENCHMARK_NAME = "locomo"


def run_locomo(args):
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
    data = load_json(args.data_path)

    if args.limit:
        data = data[: args.limit]

    results = []
    total_items = len(data)

    for item_idx, item in enumerate(tqdm(data, desc="Processing LOCOMO items")):
        print(f"[LOCOMO] Item {item_idx + 1}/{total_items}: creating agent")
        agent = client.agents.create(
            name=f"locomo_agent_{item_idx}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {
                    "label": "human",
                    "value": f"I am talking to {item['conversation']['speaker_a']} and {item['conversation']['speaker_b']}.",
                },
            ],
        )

        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)

        conversation = item["conversation"]
        sessions = [key for key in conversation.keys() if key.startswith("session_") and not key.endswith("_date_time")]
        sessions.sort(key=lambda session: int(session.split("_")[1]))
        print(f"[LOCOMO] Item {item_idx + 1}/{total_items}: loading {len(sessions)} sessions")

        for session_idx, session_key in enumerate(sessions, start=1):
            session_messages = conversation[session_key]
            formatted_messages = []
            for msg in session_messages:
                role = "user" if msg["speaker"] == conversation["speaker_a"] else "assistant"
                formatted_messages.append({"role": role, "content": f"{msg['speaker']}: {msg['text']}"})

            runner.bulk_add_messages(formatted_messages)
            print(
                f"[LOCOMO] Item {item_idx + 1}/{total_items}: "
                f"session {session_idx}/{len(sessions)} loaded ({len(formatted_messages)} messages)"
            )

        qa_results = []
        qa_items = item["qa"]
        # Limit QA items for faster validation during development
        if args.limit:
            qa_items = qa_items[: args.limit]

        total_qa = len(qa_items)
        for qa_idx, qa in enumerate(qa_items, start=1):
            question = qa.get("question")
            ground_truth = qa.get("answer", "")
            if not question:
                continue
            print(f"[LOCOMO] Item {item_idx + 1}/{total_items}: QA {qa_idx}/{total_qa}")

            response_messages = runner.run_interaction(f"Question: {question}\nAnswer briefly based on our conversation history.")

            prediction = extract_text_from_messages(response_messages)
            last_interaction = runner.get_history()[-1]
            latency = last_interaction.get("latency_seconds", 0)
            usage = last_interaction.get("usage")
            f1 = calculate_f1(prediction, str(ground_truth))

            qa_results.append(
                {
                    "question": question,
                    "ground_truth": ground_truth,
                    "prediction": prediction,
                    "f1": f1,
                    "latency_seconds": latency,
                    "usage": usage,
                }
            )

        avg_f1 = average(result["f1"] for result in qa_results)
        results.append(
            {
                "item_idx": item_idx,
                "avg_f1": avg_f1,
                "qa_count": len(qa_results),
                "qa_details": qa_results,
                "average_latency_seconds": average(qa["latency_seconds"] for qa in qa_results),
                "total_latency_seconds": sum(qa["latency_seconds"] for qa in qa_results),
                "usage": {
                    "completion_tokens": sum(qa.get("usage", {}).get("completion_tokens", 0) for qa in qa_results if qa.get("usage")),
                    "prompt_tokens": sum(qa.get("usage", {}).get("prompt_tokens", 0) for qa in qa_results if qa.get("usage")),
                    "total_tokens": sum(qa.get("usage", {}).get("total_tokens", 0) for qa in qa_results if qa.get("usage")),
                    "step_count": sum(qa.get("usage", {}).get("step_count", 0) for qa in qa_results if qa.get("usage")),
                },
            }
        )
        print(f"[LOCOMO] Item {item_idx + 1}/{total_items}: complete (avg_f1={avg_f1:.4f})")

        client.agents.delete(agent.id)

    overall_f1 = average(result["avg_f1"] for result in results)
    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "overall_f1": overall_f1,
        "items_processed": len(results),
        "average_latency_seconds": average(result["average_latency_seconds"] for result in results),
        "total_latency_seconds": sum(result["total_latency_seconds"] for result in results),
        "usage": {
            "completion_tokens": sum(result["usage"]["completion_tokens"] for result in results),
            "prompt_tokens": sum(result["usage"]["prompt_tokens"] for result in results),
            "total_tokens": sum(result["usage"]["total_tokens"] for result in results),
            "step_count": sum(result["usage"]["step_count"] for result in results),
        },
    }

    print("\nLOCOMO Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Overall F1 Score: {overall_f1:.4f}")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LOCOMO benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/locomo/data/locomo10.json", help="Path to LOCOMO dataset")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/locomo/results.json", help="Path to save results")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip benchmark preflight checks")

    args = parser.parse_args()
    run_locomo(args)
