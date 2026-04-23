import json
import re
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
    Placeholder for simple contradiction detection.
    In a real implementation, use contradiction_score_llm with an LLM judge.
    """
    p_norm = normalize_answer(prediction)
    r_norm = normalize_answer(reference)
    # Simple heuristic: if the prediction explicitly contains a 'not' or different value for a key entity
    if " not " in p_norm and " not " not in r_norm:
        return 0.0
    return 1.0


def contradiction_score_llm(prediction: str, reference: str, judge_fn: Any) -> float:
    """
    Uses an LLM judge function to evaluate if the prediction contradicts the reference.
    judge_fn should take a prompt string and return a float score 0.0 to 1.0.
    """
    prompt = (
        "Does the following prediction contradict the reference ground truth?\n\n"
        f"Reference: {reference}\n"
        f"Prediction: {prediction}\n\n"
        "Respond ONLY with a number: 0.0 if there is a contradiction, and 1.0 if there is no contradiction."
    )
    try:
        score_str = judge_fn(prompt)
        # Attempt to find a float in the response
        match = re.search(r"(\d+(\.\d+)?)", str(score_str))
        if match:
            return float(match.group(1))
        return 1.0
    except Exception:
        return 1.0  # Default to no contradiction on error


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
        # Require more than just a token match for quality
        piece_norm = normalize_answer(piece)
        if not piece_norm:
            matches += 1
            continue

        # Check if most of the piece content is present
        piece_tokens = piece_norm.split()
        if not piece_tokens:
            matches += 1
            continue

        token_matches = sum(1 for token in piece_tokens if token in prediction_norm)
        if token_matches / len(piece_tokens) >= 0.7:  # 70% of tokens present
            matches += 1

    return matches / len(evidence_pieces)


def multi_hop_attribution_quality(prediction: str, evidence_pieces: list[str], judge_fn: Any) -> float:
    """
    Uses an LLM judge to evaluate multi-hop synthesis quality.
    """
    evidence_str = "\n".join([f"- {p}" for p in evidence_pieces])
    prompt = (
        "Evaluate if the following prediction correctly synthesizes all the provided evidence pieces.\n\n"
        f"Evidence Pieces:\n{evidence_str}\n\n"
        f"Prediction: {prediction}\n\n"
        "Respond ONLY with a number from 0.0 to 1.0, where 1.0 means all evidence is correctly used."
    )
    try:
        score_str = judge_fn(prompt)
        match = re.search(r"(\d+(\.\d+)?)", str(score_str))
        if match:
            return float(match.group(1))
        return 0.0
    except Exception:
        return 0.0


def average_latency(latencies: Iterable[float]) -> float:
    values = list(latencies)
    return sum(values) / len(values) if values else 0.0


def timed_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start
