from types import SimpleNamespace

import pytest

from tests.benchmarks.common.utils import (
    build_output_payload,
    build_run_metadata,
    extract_text_from_messages,
    split_model_handle,
)


def test_split_model_handle():
    provider, model = split_model_handle("ollama/llama3.1:latest")
    assert provider == "ollama"
    assert model == "llama3.1:latest"


def test_split_model_handle_requires_provider_prefix():
    with pytest.raises(ValueError):
        split_model_handle("llama3.1:latest")


def test_extract_text_from_messages_prefers_latest_text():
    messages = [
        SimpleNamespace(content="old"),
        SimpleNamespace(content=[SimpleNamespace(text="new"), SimpleNamespace(text="answer")]),
    ]
    assert extract_text_from_messages(messages) == "new answer"


def test_build_output_payload_wraps_summary_details_and_metadata():
    metadata = build_run_metadata(
        benchmark_name="locomo",
        model="ollama/llama3.1:latest",
        base_url="http://localhost:8283",
        data_path="tests/benchmarks/locomo/data/sample.json",
        limit=5,
        output_path="tests/benchmarks/locomo/results.json",
    )
    payload = build_output_payload(
        benchmark_name="locomo",
        summary={"overall_f1": 0.5},
        details=[{"item_idx": 0}],
        metadata=metadata,
    )

    assert payload["benchmark"] == "locomo"
    assert payload["summary"]["overall_f1"] == 0.5
    assert payload["details"] == [{"item_idx": 0}]
    assert payload["metadata"]["model"] == "ollama/llama3.1:latest"
    assert payload["metadata"]["environment"]["schema_version"] == "0.1"
    assert "platform" in payload["metadata"]["environment"]
