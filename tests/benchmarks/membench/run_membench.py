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

BENCHMARK_NAME = "membench_synthetic"


def create_synthetic_membench():
    """Creates a synthetic MemBench dataset for testing store, retrieve, update, delete."""
    data = [
        {
            "id": "task_1",
            "name": "Basic Memory Operations",
            "steps": [
                {
                    "operation": "store",
                    "input": "My favorite color is blue.",
                    "thought": "Storing favorite color."
                },
                {
                    "operation": "retrieve",
                    "input": "What is my favorite color?",
                    "expected": "blue"
                },
                {
                    "operation": "update",
                    "input": "Actually, I changed my mind. My favorite color is now green.",
                    "thought": "Updating favorite color."
                },
                {
                    "operation": "retrieve_updated",
                    "input": "What is my favorite color now?",
                    "expected": "green"
                },
                {
                    "operation": "delete",
                    "input": "Please forget what my favorite color is.",
                    "thought": "Deleting favorite color from memory."
                },
                {
                    "operation": "retrieve_deleted",
                    "input": "What is my favorite color?",
                    "expected_not": "green"
                }
            ]
        },
        {
            "id": "task_2",
            "name": "Factual Memory - Person Info",
            "steps": [
                {
                    "operation": "store",
                    "input": "My friend Alice works at Google as a Software Engineer.",
                    "thought": "Storing info about Alice."
                },
                {
                    "operation": "retrieve",
                    "input": "Where does Alice work?",
                    "expected": "Google"
                },
                {
                    "operation": "retrieve",
                    "input": "What is Alice's job title?",
                    "expected": "Software Engineer"
                },
                {
                    "operation": "update",
                    "input": "Alice recently got a new job at Meta as a Product Manager.",
                    "thought": "Updating Alice's job info."
                },
                {
                    "operation": "retrieve_updated",
                    "input": "Where does Alice work now?",
                    "expected": "Meta"
                },
                {
                    "operation": "retrieve_updated",
                    "input": "What is Alice's new job title?",
                    "expected": "Product Manager"
                }
            ]
        }
    ]
    return data

def run_membench(args):
    if not args.skip_preflight:
        preflight_results = run_benchmark_preflight(
            benchmark_name=BENCHMARK_NAME,
            base_url=args.base_url,
            model=args.model,
            data_path=args.data_path,
            output_path=args.output_path,
            require_dataset=False,
        )
        print_preflight_report(preflight_results)
        assert_preflight_ok(preflight_results)

    client = Letta(base_url=args.base_url)

    try:
        data = load_json(args.data_path)
        data_source = "dataset"
    except FileNotFoundError:
        print(f"Data not found at {args.data_path}. Using synthetic data.")
        data = create_synthetic_membench()
        save_json(data, args.data_path)
        data_source = "synthetic_fallback"

    if args.limit:
        data = data[:args.limit]

    overall_results = []
    total_tasks = len(data)

    for task in tqdm(data, desc="Running MemBench tasks"):
        task_index = len(overall_results) + 1
        print(f"[MemBench] Task {task_index}/{total_tasks}: {task['name']} ({task['id']})")
        agent = client.agents.create(
            name=f"membench_agent_{task['id']}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {"label": "human", "value": "I am a user testing your memory."},
            ],
        )

        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)
        task_results = []
        total_steps = len(task["steps"])

        for step_idx, step in enumerate(task["steps"], start=1):
            op = step["operation"]
            input_text = step["input"]
            print(f"[MemBench] Task {task_index}/{total_tasks}: step {step_idx}/{total_steps} ({op})")
            response_messages = runner.run_interaction(input_text)

            prediction = extract_text_from_messages(response_messages)
            last_interaction = runner.get_history()[-1]
            latency = last_interaction.get("latency_seconds", 0)
            usage = last_interaction.get("usage")

            result = {
                "operation": op,
                "input": input_text,
                "prediction": prediction,
                "success": False,
                "latency_seconds": latency,
                "usage": usage,
            }

            if op.startswith("retrieve"):
                expected = step.get("expected")
                expected_not = step.get("expected_not")

                if expected:
                    f1 = calculate_f1(prediction, expected)
                    result["f1"] = f1
                    result["success"] = f1 > 0.5
                elif expected_not:
                    if expected_not.lower() not in prediction.lower():
                        result["success"] = True
            else:
                result["success"] = True

            task_results.append(result)

        overall_results.append({
            "task_id": task["id"],
            "task_name": task["name"],
            "steps": task_results,
            "average_latency_seconds": average(step["latency_seconds"] for step in task_results),
            "total_latency_seconds": sum(step["latency_seconds"] for step in task_results),
            "usage": {
                "completion_tokens": sum(step.get("usage", {}).get("completion_tokens", 0) for step in task_results if step.get("usage")),
                "prompt_tokens": sum(step.get("usage", {}).get("prompt_tokens", 0) for step in task_results if step.get("usage")),
                "total_tokens": sum(step.get("usage", {}).get("total_tokens", 0) for step in task_results if step.get("usage")),
                "step_count": sum(step.get("usage", {}).get("step_count", 0) for step in task_results if step.get("usage")),
            },
        })
        successes = sum(1 for step in task_results if step["success"])
        print(f"[MemBench] Task {task_index}/{total_tasks}: complete ({successes}/{total_steps} successful)")

        client.agents.delete(agent.id)

    total_steps = sum(len(result["steps"]) for result in overall_results)
    successful_steps = sum(sum(1 for step in result["steps"] if step["success"]) for result in overall_results)
    accuracy = successful_steps / total_steps if total_steps > 0 else 0

    retrieval_scores = [
        step["f1"]
        for result in overall_results
        for step in result["steps"]
        if "f1" in step
    ]
    retrieval_f1 = average(retrieval_scores)

    print("\nMemBench Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Accuracy: {accuracy:.4f} ({successful_steps}/{total_steps})")

    if args.output_path:
        all_steps = [step for res in overall_results for step in res["steps"]]
        summary = {
            "benchmark": BENCHMARK_NAME,
            "model": args.model,
            "base_url": args.base_url,
            "accuracy": accuracy,
            "retrieval_f1": retrieval_f1,
            "successful_steps": successful_steps,
            "total_steps": total_steps,
            "data_source": data_source,
            "average_latency_seconds": average(step["latency_seconds"] for step in all_steps),
            "total_latency_seconds": sum(step["latency_seconds"] for step in all_steps),
            "usage": {
                "completion_tokens": sum(res["usage"]["completion_tokens"] for res in overall_results),
                "prompt_tokens": sum(res["usage"]["prompt_tokens"] for res in overall_results),
                "total_tokens": sum(res["usage"]["total_tokens"] for res in overall_results),
                "step_count": sum(res["usage"]["step_count"] for res in overall_results),
            },
        }
        metadata = build_run_metadata(
            benchmark_name=BENCHMARK_NAME,
            model=args.model,
            base_url=args.base_url,
            data_path=args.data_path,
            limit=args.limit,
            output_path=args.output_path,
            extra={"data_source": data_source},
        )
        payload = build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=overall_results, metadata=metadata)
        save_json(payload, args.output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MemBench benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/membench/data/membench_synthetic.json", help="Path to MemBench dataset")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of tasks to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/membench/results.json", help="Path to save results")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip benchmark preflight checks")

    args = parser.parse_args()
    run_membench(args)
