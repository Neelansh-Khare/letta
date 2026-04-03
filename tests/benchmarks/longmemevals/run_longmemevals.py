import argparse

from tests.benchmarks.common.utils import default_benchmark_base_url, default_benchmark_model
from tests.benchmarks.longmemeval.run_longmemeval import run_longmemeval

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LongMemEvalS benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url())
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/longmemeval/data/longmemeval_s_cleaned.json")
    parser.add_argument("--model", type=str, default=default_benchmark_model())
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/longmemevals/results.json")
    parser.add_argument("--skip-preflight", action="store_true")
    run_longmemeval(parser.parse_args())
