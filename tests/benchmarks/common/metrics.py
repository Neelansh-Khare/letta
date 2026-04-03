import json
import time
from typing import Any, Iterable

from tests.benchmarks.common.utils import calculate_f1, normalize_answer


def normalize_for_exact_match(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    return normalize_answer(str(value))


def exact_match(prediction: Any, ground_truth: Any) -> float:
    return 1.0 if normalize_for_exact_match(prediction) == normalize_for_exact_match(ground_truth) else 0.0


def contains_match(prediction: Any, expected: Any) -> float:
    prediction_text = normalize_answer(str(prediction))
    expected_text = normalize_answer(str(expected))
    if not expected_text:
        return 0.0
    return 1.0 if expected_text in prediction_text else 0.0


def choice_accuracy(prediction: str, correct_choice_id: str | None) -> float:
    if not correct_choice_id:
        return 0.0
    prediction_norm = normalize_answer(prediction)
    choice_norm = normalize_answer(correct_choice_id)
    return 1.0 if prediction_norm == choice_norm or prediction_norm.startswith(choice_norm) else 0.0


def f1_for_any(prediction: Any, ground_truth: Any) -> float:
    return calculate_f1(str(prediction), str(ground_truth))


def task_success_rate(step_scores: Iterable[float], threshold: float = 1.0) -> float:
    scores = list(step_scores)
    if not scores:
        return 0.0
    return 1.0 if all(score >= threshold for score in scores) else 0.0


def average_latency(latencies: Iterable[float]) -> float:
    values = list(latencies)
    return sum(values) / len(values) if values else 0.0


def timed_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start
