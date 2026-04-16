import argparse
import sys
from typing import Any

from tests.benchmarks.common.utils import load_json


def compare_metrics(baseline: dict[str, Any], current: dict[str, Any]):
    b_summary = baseline.get("summary", {})
    c_summary = current.get("summary", {})
    
    benchmark = current.get("benchmark") or current.get("metadata", {}).get("benchmark", "Unknown")
    
    print(f"=== Regression Analysis: {benchmark} ===")
    print(f"Baseline: {baseline.get('metadata', {}).get('run_at', 'unknown')}")
    print(f"Current:  {current.get('metadata', {}).get('run_at', 'unknown')}")
    print("-" * 40)
    
    all_keys = sorted(set(b_summary.keys()) | set(c_summary.keys()))
    
    found_regression = False
    
    for key in all_keys:
        if key in ["benchmark", "model", "base_url", "usage"]:
            continue
            
        b_val = b_summary.get(key)
        c_val = c_summary.get(key)
        
        if b_val is None or c_val is None:
            continue
            
        if not isinstance(b_val, (int, float)) or not isinstance(c_val, (int, float)):
            continue
            
        diff = c_val - b_val
        diff_pct = (diff / b_val * 100) if b_val != 0 else 0
        
        status = " "
        if diff < 0:
            # For most metrics, lower is worse (accuracy, F1)
            # For latency/tokens, lower is better.
            if any(term in key for term in ["latency", "tokens", "cost", "growth"]):
                status = "[IMPROVED]"
            else:
                status = "[REGRESS]"
                found_regression = True
        elif diff > 0:
            if any(term in key for term in ["latency", "tokens", "cost", "growth"]):
                status = "[REGRESS]"
                found_regression = True
            else:
                status = "[IMPROVED]"
                
        print(f"{status:<10} {key:<30}: {b_val:>8.4f} -> {c_val:>8.4f} ({diff:>+8.4f}, {diff_pct:>+7.2f}%)")

    # Compare usage
    b_usage = b_summary.get("usage", {})
    c_usage = c_summary.get("usage", {})
    if b_usage and c_usage:
        print("\nResource Usage Comparison:")
        for key in sorted(set(b_usage.keys()) | set(c_usage.keys())):
            b_val = b_usage.get(key, 0)
            c_val = c_usage.get(key, 0)
            diff = c_val - b_val
            diff_pct = (diff / b_val * 100) if b_val != 0 else 0
            status = " "
            if diff > 0:
                status = "[REGRESS]"
            elif diff < 0:
                status = "[IMPROVED]"
            print(f"{status:<10} {key:<30}: {b_val:>8d} -> {c_val:>8d} ({diff:>+8d}, {diff_pct:>+7.2f}%)")

    return found_regression

def main():
    parser = argparse.ArgumentParser(description="Compare two Letta benchmark result JSON files.")
    parser.add_argument("baseline", help="Baseline result JSON file")
    parser.add_argument("current", help="Current result JSON file")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit with non-zero code if regression found")
    args = parser.parse_args()

    try:
        baseline = load_json(args.baseline)
        current = load_json(args.current)
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)

    has_regression = compare_metrics(baseline, current)
    
    if args.fail_on_regression and has_regression:
        print("\n[FAIL] Regression detected!")
        sys.exit(1)

if __name__ == "__main__":
    main()
