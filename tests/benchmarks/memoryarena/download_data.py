import os

from tests.benchmarks.common.downloads import download_if_missing


def download_memoryarena_data():
    base_url = "https://huggingface.co/datasets/ZexueHe/memoryarena/resolve/main"
    target_dir = "tests/benchmarks/memoryarena/data"
    for subset in [
        "bundled_shopping",
        "progressive_search",
        "group_travel_planner",
        "formal_reasoning_math",
        "formal_reasoning_phys",
    ]:
        download_if_missing(f"{base_url}/{subset}/data.jsonl?download=true", os.path.join(target_dir, subset, "data.jsonl"))


if __name__ == "__main__":
    download_memoryarena_data()
