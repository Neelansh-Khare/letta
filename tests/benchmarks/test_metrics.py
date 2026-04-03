from tests.benchmarks.common.metrics import choice_accuracy, exact_match, task_success_rate


def test_exact_match_for_scalar_values():
    assert exact_match("Blue", "blue") == 1.0
    assert exact_match("blue", "green") == 0.0


def test_choice_accuracy_accepts_prefixed_choice():
    assert choice_accuracy("B: because of evidence", "B") == 1.0
    assert choice_accuracy("C", "B") == 0.0


def test_task_success_rate():
    assert task_success_rate([1.0, 1.0, 1.0]) == 1.0
    assert task_success_rate([1.0, 0.0, 1.0]) == 0.0
