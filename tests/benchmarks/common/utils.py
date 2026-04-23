import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

BENCHMARK_SCHEMA_VERSION = "0.1"


def load_json(file_path: str) -> Any:
    """Loads data from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, file_path: str):
    """Saves data to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def utc_now_iso() -> str:
    """Returns a UTC ISO8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def default_benchmark_model() -> str:
    """Returns the default model handle for local benchmark runs."""
    return os.getenv("LETTA_BENCHMARK_MODEL", "ollama/llama3.1:latest")


def default_benchmark_base_url() -> str:
    """Returns the default Letta server base URL for benchmark runs."""
    return os.getenv("LETTA_BENCHMARK_BASE_URL", "http://localhost:8283")


def split_model_handle(model_handle: str) -> tuple[str, str]:
    """Splits a model handle into provider name and provider model."""
    if "/" not in model_handle:
        raise ValueError(f"Model handle '{model_handle}' must be in '<provider>/<model>' format, " "for example 'ollama/llama3.1:latest'.")
    provider, model_name = model_handle.split("/", 1)
    if not provider or not model_name:
        raise ValueError(f"Invalid model handle '{model_handle}'.")
    return provider, model_name


def extract_text_from_messages(messages: Iterable[Any]) -> str:
    """Extracts the last assistant/user-visible text from a Letta response message list."""
    for message in reversed(list(messages)):
        content = getattr(message, "content", None)
        if not content:
            continue
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                text = getattr(item, "text", None)
                if text:
                    text_parts.append(text)
            if text_parts:
                return " ".join(text_parts)
    return ""


def average(values: Iterable[float]) -> float:
    """Computes the arithmetic mean for a finite iterable."""
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def get_git_commit() -> Optional[str]:
    """Returns the current git commit hash when available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    commit = result.stdout.strip()
    return commit or None


def build_environment_metadata() -> dict[str, Any]:
    """Builds runtime environment metadata for benchmark outputs."""
    from letta import __version__ as letta_version

    selected_env = {
        key: os.getenv(key)
        for key in ["LETTA_BENCHMARK_BASE_URL", "LETTA_BENCHMARK_MODEL", "OLLAMA_BASE_URL", "LETTA_PG_URI"]
        if os.getenv(key)
    }
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "letta_version": letta_version,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        },
        "runtime": {
            "executable": sys.executable,
            "cwd": str(Path.cwd()),
        },
        "source_control": {
            "git_commit": get_git_commit(),
        },
        "selected_env": selected_env,
    }


def build_run_metadata(
    *,
    benchmark_name: str,
    model: str,
    base_url: str,
    data_path: str,
    limit: Optional[int],
    output_path: Optional[str],
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Builds standard metadata for benchmark result payloads."""
    metadata = {
        "benchmark": benchmark_name,
        "model": model,
        "base_url": base_url,
        "data_path": str(Path(data_path)),
        "limit": limit,
        "output_path": str(Path(output_path)) if output_path else None,
        "run_at": utc_now_iso(),
        "environment": build_environment_metadata(),
    }
    if extra:
        metadata.update(extra)
    return metadata


def build_output_payload(
    *,
    benchmark_name: str,
    summary: dict[str, Any],
    details: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Builds the standard benchmark output payload."""
    return {
        "benchmark": benchmark_name,
        "metadata": metadata,
        "summary": summary,
        "details": details,
    }


def normalize_answer(s: str) -> str:
    """Lowercases, removes punctuation, articles and extra whitespace."""

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        return re.sub(r"[^\w\s]", "", text)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(str(s)))))


def calculate_f1(prediction: str, ground_truth: str) -> float:
    """Calculates token-level F1 score."""
    prediction_tokens = normalize_answer(prediction).split()
    ground_truth_tokens = normalize_answer(ground_truth).split()
    if not prediction_tokens or not ground_truth_tokens:
        return 1.0 if prediction_tokens == ground_truth_tokens else 0.0

    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1
