from unittest.mock import Mock, patch

import pytest

from tests.benchmarks.common.preflight import (
    assert_preflight_ok,
    check_dataset_path,
    check_model_available,
    check_model_handle,
    check_server_health,
    run_benchmark_preflight,
)


def _mock_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_check_model_handle_invalid():
    result = check_model_handle("llama3.1:latest")
    assert not result.ok
    assert result.name == "model_handle"


def test_check_dataset_path_optional_missing(tmp_path):
    result = check_dataset_path(str(tmp_path / "missing.json"), required=False)
    assert result.ok
    assert result.details["fallback"] is True


@patch("tests.benchmarks.common.preflight.httpx.get")
def test_check_server_health_success(mock_get):
    mock_get.return_value = _mock_response({"status": "ok", "version": "0.16.6"})
    result = check_server_health("http://localhost:8283")
    assert result.ok
    assert result.details["payload"]["status"] == "ok"


@patch("tests.benchmarks.common.preflight.httpx.get")
def test_check_model_available_reports_missing_handle(mock_get):
    mock_get.return_value = _mock_response([{"handle": "ollama/other-model:latest"}])
    result = check_model_available("http://localhost:8283", "ollama/llama3.1:latest")
    assert not result.ok
    assert "not found" in result.message


@patch("tests.benchmarks.common.preflight.httpx.get")
def test_run_benchmark_preflight_returns_all_checks(mock_get, tmp_path):
    mock_get.side_effect = [
        _mock_response({"status": "ok", "version": "0.16.6"}),
        _mock_response([{"handle": "ollama/llama3.1:latest"}]),
    ]
    dataset = tmp_path / "data.json"
    dataset.write_text("[]", encoding="utf-8")

    results = run_benchmark_preflight(
        benchmark_name="locomo",
        base_url="http://localhost:8283",
        model="ollama/llama3.1:latest",
        data_path=str(dataset),
        output_path=str(tmp_path / "results.json"),
        require_dataset=True,
    )

    assert len(results) == 6
    assert all(result.ok for result in results)


def test_assert_preflight_ok_raises_on_failure():
    with pytest.raises(RuntimeError):
        assert_preflight_ok([check_model_handle("bad-model-handle")])
