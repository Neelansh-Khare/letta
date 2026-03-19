from tests.benchmarks.summarize_results import load_and_normalize, normalize_result_payload


def test_normalize_result_payload_new_shape():
    payload = {
        "benchmark": "locomo",
        "metadata": {
            "benchmark": "locomo",
            "model": "ollama/llama3.1:latest",
            "base_url": "http://localhost:8283",
            "run_at": "2026-03-19T00:00:00+00:00",
        },
        "summary": {
            "benchmark": "locomo",
            "model": "ollama/llama3.1:latest",
            "overall_f1": 0.42,
        },
        "details": [],
    }

    normalized = normalize_result_payload(payload, "results/locomo.json")
    assert normalized["benchmark"] == "locomo"
    assert normalized["model"] == "ollama/llama3.1:latest"
    assert normalized["metrics"]["overall_f1"] == 0.42


def test_normalize_result_payload_old_shape():
    payload = {
        "summary": {
            "model": "ollama/llama3.1:latest",
            "accuracy": 0.66,
        },
        "details": [],
    }

    normalized = normalize_result_payload(payload, "results/membench.json")
    assert normalized["benchmark"] == "membench"
    assert normalized["model"] == "ollama/llama3.1:latest"
    assert normalized["metrics"]["accuracy"] == 0.66


def test_load_and_normalize(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(
        """{
  "benchmark": "longmemeval",
  "metadata": {"model": "ollama/llama3.1:latest"},
  "summary": {"overall_f1": 0.1}
}""",
        encoding="utf-8",
    )

    rows = load_and_normalize([str(result_path)])
    assert len(rows) == 1
    assert rows[0]["benchmark"] == "longmemeval"
