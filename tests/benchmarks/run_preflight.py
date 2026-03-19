import argparse

from tests.benchmarks.common.preflight import assert_preflight_ok, print_preflight_report, run_benchmark_preflight
from tests.benchmarks.common.utils import default_benchmark_base_url, default_benchmark_model


def main():
    parser = argparse.ArgumentParser(description="Run benchmark preflight checks for Letta benchmarks.")
    parser.add_argument("--benchmark", type=str, default="custom", help="Benchmark name for reporting")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to validate")
    parser.add_argument("--data_path", type=str, required=True, help="Dataset path to validate")
    parser.add_argument("--output_path", type=str, default=None, help="Optional output path to validate")
    parser.add_argument("--require-dataset", action="store_true", help="Fail if the dataset path is missing")
    args = parser.parse_args()

    results = run_benchmark_preflight(
        benchmark_name=args.benchmark,
        base_url=args.base_url,
        model=args.model,
        data_path=args.data_path,
        output_path=args.output_path,
        require_dataset=args.require_dataset,
    )
    print_preflight_report(results)
    assert_preflight_ok(results)
    print("Benchmark preflight succeeded.")


if __name__ == "__main__":
    main()
