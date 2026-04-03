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

BENCHMARK_NAME = "clonemem"


def load_personas(data_dir: str, context_len: str) -> list[dict]:
    path_pattern = str(Path(data_dir, context_len, "*_benchmark_en.json"))
    paths = sorted(Path(data_dir, context_len).glob("*_benchmark_en.json"))
    print(f"[CloneMem] Searching for personas in {data_dir}/{context_len} (found {len(paths)} files)")
    if not paths:
        # Fallback to searching without context_len if not found in subfolder
        paths = sorted(Path(data_dir).glob("*_benchmark_en.json"))
        if paths:
            print(f"[CloneMem] Found {len(paths)} files in root data_dir instead")
            
    return [load_json(str(path)) for path in paths]


def format_context_entry(trace: dict) -> str:
    return (
        f"[CloneMem][{trace.get('event_date', '')}][{trace.get('medium', 'unknown')}] "
        f"{trace.get('content', '')}"
    )


def format_question_prompt(question: dict) -> str:
    prompt = question["question"]
    choices = question.get("choices")
    if choices:
        rendered = [f"{choice.get('id')}: {choice.get('text')}" for choice in choices]
        prompt += "\n\nChoices:\n" + "\n".join(rendered)
        prompt += "\nAnswer with the best option ID and a brief explanation."
    else:
        prompt += "\nAnswer briefly based on the known digital traces."
    return prompt


def run_clonemem(args):
    data_dir = f"{args.data_dir}/{args.context_len}"
    if not args.skip_preflight:
        preflight_results = run_benchmark_preflight(
            benchmark_name=BENCHMARK_NAME,
            base_url=args.base_url,
            model=args.model,
            data_path=data_dir,
            output_path=args.output_path,
            require_dataset=True,
        )
        print_preflight_report(preflight_results)
        assert_preflight_ok(preflight_results)

    client = Letta(base_url=args.base_url)
    personas = load_personas(args.data_dir, args.context_len)
    if args.limit:
        personas = personas[: args.limit]

    results = []
    for persona in tqdm(personas, desc="CloneMem personas"):
        agent = client.agents.create(
            name=f"clonemem_{persona.get('person_id')}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with detailed longitudinal memory."},
                {"label": "human", "value": f"I am recalling the life traces of {persona.get('person_name')}."},
            ],
        )
        runner = BenchmarkRunner(client, agent.id, model_handle=args.model)
        runner.ingest_text_entries([format_context_entry(trace) for trace in persona.get("context", [])], batch_size=20)

        persona_results = []
        latencies = []
        for question in persona.get("questions", []):
            response_messages, latency = runner.run_interaction_timed(format_question_prompt(question))
            prediction = extract_text_from_messages(response_messages)
            persona_results.append(
                {
                    "person_id": persona.get("person_id"),
                    "person_name": persona.get("person_name"),
                    "question_id": question.get("id"),
                    "question_type": question.get("question_type"),
                    "dimension": question.get("dimension"),
                    "question": question.get("question"),
                    "answer": question.get("answer"),
                    "prediction": prediction,
                    "f1": f1_for_any(prediction, question.get("answer", "")),
                    "exact_match": exact_match(prediction, question.get("answer", "")),
                    "mcq_accuracy": choice_accuracy(prediction, question.get("correct_choice_id")),
                    "latency_seconds": latency,
                    "usage": runner.get_history()[-1].get("usage"),
                }
            )
            latencies.append(latency)

        results.extend(persona_results)
        client.agents.delete(agent.id)

    summary = {
        "benchmark": BENCHMARK_NAME,
        "model": args.model,
        "base_url": args.base_url,
        "context_len": args.context_len,
        "items_processed": len(results),
        "overall_f1": average(item["f1"] for item in results),
        "exact_match_rate": average(item["exact_match"] for item in results),
        "mcq_accuracy": average(item["mcq_accuracy"] for item in results),
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
            data_path=data_dir,
            limit=args.limit,
            output_path=args.output_path,
            extra={"context_len": args.context_len},
        )
        save_json(build_output_payload(benchmark_name=BENCHMARK_NAME, summary=summary, details=results, metadata=metadata), args.output_path)
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CloneMem on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url())
    parser.add_argument("--model", type=str, default=default_benchmark_model())
    parser.add_argument("--data_dir", type=str, default="tests/benchmarks/clonemem/data")
    parser.add_argument("--context_len", choices=["100k", "500k"], default="100k")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/clonemem/results.json")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()
    run_clonemem(args)
