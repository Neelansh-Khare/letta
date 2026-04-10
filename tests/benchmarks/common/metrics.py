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


def staleness_score(prediction: str, current_ground_truth: str, obsolete_ground_truth: str) -> float:
    """
    Measures if the prediction correctly uses the newest information rather than obsolete info.
    Returns 1.0 if the prediction matches current_ground_truth, 0.0 if it matches obsolete_ground_truth,
    or a value in between based on contains_match.
    """
    current_match = contains_match(prediction, current_ground_truth)
    obsolete_match = contains_match(prediction, obsolete_ground_truth)

    if current_match > 0 and obsolete_match == 0:
        return 1.0
    if obsolete_match > 0 and current_match == 0:
        return 0.0
    return 0.5 if current_match > 0 and obsolete_match > 0 else 0.0


def deletion_compliance(agent_response: str, deleted_keyword: str) -> float:
    """
    Returns 1.0 if the agent response correctly avoids mentioning information that was supposed to be deleted.
    """
    return 1.0 if normalize_answer(deleted_keyword) not in normalize_answer(agent_response) else 0.0


def contradiction_score(prediction: str, reference: str) -> float:
    """
    Placeholder for LLM-based contradiction detection.
    In a real implementation, this would call an LLM to evaluate if the prediction contradicts the reference.
    For now, it uses basic overlap logic.
    """
    # Simple heuristic: if the prediction explicitly contains a 'not' or different value for a key entity
    # This should be replaced with a proper LLM-as-a-judge call
    p_norm = normalize_answer(prediction)
    r_norm = normalize_answer(reference)
    if " not " in p_norm and " not " not in r_norm:
        return 0.0
    return 1.0


def multi_hop_quality(prediction: str, evidence_pieces: list[str]) -> float:
    """
    Evaluates if the prediction correctly synthesizes multiple pieces of evidence.
    Returns a score from 0.0 to 1.0 based on how many evidence pieces are reflected in the answer.
    """
    if not evidence_pieces:
        return 1.0
    
    prediction_norm = normalize_answer(prediction)
    matches = 0
    for piece in evidence_pieces:
        piece_tokens = normalize_answer(piece).split()
        if not piece_tokens:
            matches += 1
            continue
        # Check if all tokens from the evidence piece are present in the normalized prediction
        if all(token in prediction_norm for token in piece_tokens):
            matches += 1
            
    return matches / len(evidence_pieces)


def average_latency(latencies: Iterable[float]) -> float:
    values = list(latencies)
    return sum(values) / len(values) if values else 0.0


def timed_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start
