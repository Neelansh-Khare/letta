import argparse
import subprocess
import os
import sys

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
    parser.add_argument("--model", type=str, default="openai/gpt-4o-mini", help="Model to use for the benchmarks")
    parser.add_argument("--limit", type=int, default=5, help="Limit the number of items/tasks per benchmark")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading datasets")
    
    args = parser.parse_args()
    
    benchmarks = [
        ("LOCOMO", "tests/benchmarks/locomo/run_locomo.py", "tests/benchmarks/locomo/download_data.py"),
        ("MemBenchSynthetic", "tests/benchmarks/membench/run_membench.py", "tests/benchmarks/membench/download_data.py"),
        ("MemBenchReal", "tests/benchmarks/membench/run_membench_real.py", "tests/benchmarks/membench/download_data.py"),
        ("LongMemEval", "tests/benchmarks/longmemeval/run_longmemeval.py", "tests/benchmarks/longmemeval/download_data.py")
    ]
    
    for name, run_script, download_script in benchmarks:
        print(f"\n{'='*20} {name} Benchmark {'='*20}")
        
        if not args.skip_download:
            print(f"Ensuring data for {name}...")
            if not run_command(["uv", "run", "python", download_script]):
                print(f"Skipping {name} due to download failure.")
                continue
        
        print(f"Running {name}...")
        run_command(["uv", "run", "python", run_script, "--model", args.model, "--limit", str(args.limit)])

if __name__ == "__main__":
    main()
