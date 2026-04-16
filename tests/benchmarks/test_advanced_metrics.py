import pytest
from tests.benchmarks.common.metrics import (
    contradiction_score,
    contradiction_score_llm,
    multi_hop_quality,
    multi_hop_attribution_quality
)

def test_contradiction_score_basic():
    assert contradiction_score("The sky is blue", "The sky is blue") == 1.0
    assert contradiction_score("The sky is NOT blue", "The sky is blue") == 0.0

def test_contradiction_score_llm():
    def mock_judge(prompt):
        if "contradict" in prompt.lower():
            return "0.0"
        return "1.0"
    
    assert contradiction_score_llm("The sky is red", "The sky is blue", mock_judge) == 0.0

def test_multi_hop_quality_threshold():
    # 70% threshold test
    # "cat mat" -> "cat", "mat"
    # "The cat is on mat" -> contains "cat", "mat". 100% of tokens. Match.
    assert multi_hop_quality("The cat is on the mat", ["cat mat"]) == 1.0
    
    # "The cat is here" -> contains "cat". 50% of tokens. No match.
    assert multi_hop_quality("The cat is here", ["cat mat"]) == 0.0
    
    # "The cat is on mat" -> contains "cat", "mat".
    # Evidence 1: "cat mat" (100% match)
    # Evidence 2: "dog yard" (0% match)
    # Score: 0.5
    assert multi_hop_quality("The cat is on the mat", ["cat mat", "dog yard"]) == 0.5

def test_multi_hop_attribution_quality():
    def mock_judge(prompt):
        return "0.8"
    
    assert multi_hop_attribution_quality("Prediction", ["Evidence"], mock_judge) == 0.8
