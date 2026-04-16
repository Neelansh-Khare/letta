import json
import os
import subprocess
import sys
import pytest

def test_compare_results_cli():
    baseline_path = "baseline.json"
    current_path = "current.json"
    
    baseline = {
        "benchmark": "test_bench",
        "summary": {
            "overall_f1": 0.8,
            "average_latency_seconds": 1.0,
            "usage": {"total_tokens": 100}
        },
        "metadata": {"run_at": "2024-01-01T00:00:00Z"}
    }
    current = {
        "benchmark": "test_bench",
        "summary": {
            "overall_f1": 0.7, # Regression
            "average_latency_seconds": 1.2, # Regression
            "usage": {"total_tokens": 120} # Regression
        },
        "metadata": {"run_at": "2024-01-02T00:00:00Z"}
    }
    
    with open(baseline_path, "w") as f:
        json.dump(baseline, f)
    with open(current_path, "w") as f:
        json.dump(current, f)
        
    try:
        # Should fail with --fail-on-regression
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        result = subprocess.run(
            [sys.executable, "tests/benchmarks/compare_results.py", baseline_path, current_path, "--fail-on-regression"],
            capture_output=True, text=True, env=env
        )
        assert result.returncode != 0
        assert "[REGRESS]" in result.stdout
        assert "overall_f1" in result.stdout
        assert "average_latency_seconds" in result.stdout
        
    finally:
        if os.path.exists(baseline_path):
            os.remove(baseline_path)
        if os.path.exists(current_path):
            os.remove(current_path)
