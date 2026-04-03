import argparse
from pathlib import Path

from letta_client import Letta
from tqdm import tqdm

from tests.benchmarks.common.metrics import average_latency, choice_accuracy, exact_match, f1_for_any
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

BENCHMARK_NAME = "evermembench"


def load_topics(data_dir: str) -> list[tuple[str, list[dict], list[dict]]]:
    topics = []
    for topic_dir in sorted(Path(data_dir).glob("*")):
        if not topic_dir.is_dir():
            continue
        dialogue_path = topic_dir / "dialogue.json"
        qa_candidates = sorted(topic_dir.glob("qa_*.json"))
        if not dialogue_path.exists() or not qa_candidates:
            continue
        topics.append((topic_dir.name, load_json(str(dialogue_path)), load_json(str(qa_candidates[0]))))
    return topics


def flatten_dialogues(dialogue_days: list[dict]) -> list[str]:
    entries = []
    for day in dialogue_days:
        date = day.get("date", "")
        dialogues = day.get("dialogues", {})
        for group_name, messages in dialogues.items():
            for message in messages:
                speaker = message.get("speaker", "Unknown")
                time = message.get("time", "")
                content = message.get("dialogue", "")
                entries.append(f"[EverMemBench][{date}][{group_name}][{time}][{speaker}] {content}")
    return entries


def format_mcq_prompt(question: dict) -> str:
    prompt = question["Q"]
    if question.get("options"):
        choices = []
        for option in question["options"]:
            if isinstance(option, dict):
                choices.append(f"{option.get('id', '')}: {option.get('text', '')}")
            else:
                choices.append(str(option))
        prompt += "\n\nChoices:\n" + "\n".join(choices)
        prompt += "\nAnswer with the best option ID and a brief explanation."
    else:
        prompt += "\nAnswer briefly based only on the prior conversation history."
    return prompt


def run_evermembench(args):
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
    topics = load_topics(args.data_dir)
    if args.limit:
        remaining = args.limit
    else:
        remaining = None

    results = []
    for topic_id, dialogue_days, qa_items in topics:
        if remaining == 0:
            break
        agent = client.agents.create(
            name=f"evermembench_agent_{topic_id}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with long-horizon memory."},
                {"label": "human", "value": "I am evaluating your memory of a long group-chat history."},
            ],
        )
        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)
        entries = flatten_dialogues(dialogue_days)
        print(f"[EverMemBench] Topic {topic_id}: ingesting {len(entries)} dialogue entries")
        runner.ingest_text_entries(entries, batch_size=25)

        topic_results = []
        latencies = []
        for qa in tqdm(qa_items, desc=f"EverMemBench topic {topic_id}", leave=False):
            if remaining == 0:
                break
            prompt = format_mcq_prompt(qa)
            response_messages, latency = runner.run_interaction_timed(prompt)
            prediction = extract_text_from_messages(response_messages)
            answer = qa.get("A", "")
            option_items = qa.get("options")
            mcq = 1.0 if option_items else None
            if option_items:
                correct_choice_id = None
                for option in option_items:
                    if isinstance(option, dict) and option.get("text") == answer:
                        correct_choice_id = option.get("id")
                        break
                mcq = choice_accuracy(prediction, correct_choice_id)

            item_result = {
                "topic_id": topic_id,
                "question_id": qa.get("id"),
                "question": qa.get("Q"),
                "answer": answer,
                "prediction": prediction,
                "f1": f1_for_any(prediction, answer),
                "exact_match": exact_match(prediction, answer),
                "mcq_accuracy": mcq,
                "latency_seconds": latency,
                "usage": runner.get_history()[-1].get("usage"),
            }
            topic_results.append(item_result)
            latencies.append(latency)
            if remaining is not None:
                remaining -= 1

        results.extend(topic_results)
        client.agents.delete(agent.id)

    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "items_processed": len(results),
        "overall_f1": average(item["f1"] for item in results),
        "exact_match_rate": average(item["exact_match"] for item in results),
        "mcq_accuracy": average(item["mcq_accuracy"] for item in results if item["mcq_accuracy"] is not None),
        "average_latency_seconds": average_latency(item["latency_seconds"] for item in results),
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
            data_path=args.data_dir,
            limit=args.limit,
            output_path=args.output_path,
        )
        save_json(build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=results, metadata=metadata), args.output_path)
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EverMemBench on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url())
    parser.add_argument("--model", type=str, default=default_benchmark_model())
    parser.add_argument("--data_dir", type=str, default="tests/benchmarks/evermembench/data")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/evermembench/results.json")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()
    run_evermembench(args)
