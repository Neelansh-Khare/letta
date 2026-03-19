import argparse
from pathlib import Path
from typing import Any

from tests.benchmarks.common.utils import load_json


def _get_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("summary", {})


def _get_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("metadata", {})


def normalize_result_payload(payload: dict[str, Any], path: str) -> dict[str, Any]:
    summary = _get_summary(payload)
    metadata = _get_metadata(payload)

    benchmark = payload.get("benchmark") or metadata.get("benchmark") or Path(path).stem
    model = summary.get("model") or metadata.get("model")
    run_at = metadata.get("run_at")
    base_url = summary.get("base_url") or metadata.get("base_url")

    normalized = {
        "path": path,
        "benchmark": benchmark,
        "model": model,
        "run_at": run_at,
        "base_url": base_url,
        "summary": summary,
    }

    scalar_metrics = {}
    for key, value in summary.items():
        if isinstance(value, (int, float, str, bool)) or value is None:
            scalar_metrics[key] = value
    normalized["metrics"] = scalar_metrics
    return normalized


def load_and_normalize(paths: list[str]) -> list[dict[str, Any]]:
    return [normalize_result_payload(load_json(path), path) for path in paths]


def print_human_summary(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        print(f"- benchmark: {row['benchmark']}")
        print(f"  path: {row['path']}")
        print(f"  model: {row['model']}")
        print(f"  run_at: {row['run_at']}")
        metrics = row["metrics"]
        printable_metrics = ", ".join(f"{key}={value}" for key, value in metrics.items() if key not in {"benchmark", "model", "base_url"})
        print(f"  metrics: {printable_metrics or 'none'}")


def main():
    parser = argparse.ArgumentParser(description="Summarize one or more Letta benchmark result JSON files.")
    parser.add_argument("paths", nargs="+", help="Benchmark result JSON files")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    rows = load_and_normalize(args.paths)
    if args.format == "json":
        import json

        print(json.dumps(rows, indent=2))
        return

    print_human_summary(rows)


if __name__ == "__main__":
    main()
