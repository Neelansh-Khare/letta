from tests.benchmarks.common.metrics import (
    choice_accuracy,
    deletion_compliance,
    exact_match,
    multi_hop_quality,
    staleness_score,
    task_success_rate,
)


def test_exact_match_for_scalar_values():
    assert exact_match("Blue", "blue") == 1.0
    assert exact_match("blue", "green") == 0.0


def test_choice_accuracy_accepts_prefixed_choice():
    assert choice_accuracy("B: because of evidence", "B") == 1.0
    assert choice_accuracy("C", "B") == 0.0


def test_task_success_rate():
    assert task_success_rate([1.0, 1.0, 1.0]) == 1.0
    assert task_success_rate([1.0, 0.0, 1.0]) == 0.0


def test_staleness_score_detects_obsolete_info():
    # Correct (current) info
    assert staleness_score("The price is $50", "$50", "$40") == 1.0
    # Obsolete (old) info
    assert staleness_score("The price is $40", "$50", "$40") == 0.0
    # Ambiguous or both
    assert staleness_score("It was $40 but now it's $50", "$50", "$40") == 0.5


def test_deletion_compliance():
    # Compliance: keyword NOT in response
    assert deletion_compliance("I don't know that person", "John Doe") == 1.0
    # Non-compliance: keyword IS in response
    assert deletion_compliance("John Doe lives in NYC", "John Doe") == 0.0


def test_multi_hop_quality():
    # Full evidence synthesis
    assert multi_hop_quality("The cat is on the mat and the dog is in the yard", ["cat mat", "dog yard"]) == 1.0
    # Partial evidence synthesis
    assert multi_hop_quality("The cat is on the mat", ["cat mat", "dog yard"]) == 0.5
    # No evidence synthesis
    assert multi_hop_quality("Neither", ["cat mat", "dog yard"]) == 0.0
