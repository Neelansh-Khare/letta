import argparse
import subprocess

from tests.benchmarks.common.utils import default_benchmark_base_url, default_benchmark_model


def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Run all Letta memory benchmarks.")
    parser.add_argument("--base_url", type=str, default=default_benchmark_base_url(), help="Letta server base URL")
    parser.add_argument("--model", type=str, default=default_benchmark_model(), help="Model handle to use for the benchmarks")
    parser.add_argument("--limit", type=int, default=5, help="Limit the number of items/tasks per benchmark")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading datasets")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip benchmark preflight checks")

    args = parser.parse_args()

    benchmarks = [
        ("LOCOMO", "tests/benchmarks/locomo/run_locomo.py", "tests/benchmarks/locomo/download_data.py"),
        ("MemBenchSynthetic", "tests/benchmarks/membench/run_membench.py", "tests/benchmarks/membench/download_data.py"),
        ("MemBenchReal", "tests/benchmarks/membench/run_membench_real.py", "tests/benchmarks/membench/download_data.py"),
        ("LongMemEval", "tests/benchmarks/longmemeval/run_longmemeval.py", "tests/benchmarks/longmemeval/download_data.py"),
        ("LongMemEvalS", "tests/benchmarks/longmemevals/run_longmemevals.py", "tests/benchmarks/longmemevals/download_data.py"),
        ("EverMemBench", "tests/benchmarks/evermembench/run_evermembench.py", "tests/benchmarks/evermembench/download_data.py"),
        ("MemoryArena", "tests/benchmarks/memoryarena/run_memoryarena.py", "tests/benchmarks/memoryarena/download_data.py"),
        ("CloneMem", "tests/benchmarks/clonemem/run_clonemem.py", "tests/benchmarks/clonemem/download_data.py"),
    ]

    for name, run_script, download_script in benchmarks:
        print(f"\n{'='*20} {name} Benchmark {'='*20}")

        if not args.skip_download:
            print(f"Ensuring data for {name}...")
            if not run_command(["uv", "run", "python", download_script]):
                print(f"Skipping {name} due to download failure.")
                continue

        print(f"Running {name}...")
        command = [
            "uv",
            "run",
            "python",
            run_script,
            "--base_url",
            args.base_url,
            "--model",
            args.model,
            "--limit",
            str(args.limit),
        ]
        if args.skip_preflight:
            command.append("--skip-preflight")
        run_command(command)


if __name__ == "__main__":
    main()
