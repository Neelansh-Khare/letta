import os

from tests.benchmarks.common.downloads import download_if_missing


def download_evermembench_data():
    base_url = "https://huggingface.co/datasets/EverMind-AI/EverMemBench-Dynamic/resolve/main"
    target_dir = "tests/benchmarks/evermembench/data"
    topic_ids = ["01", "02", "03", "04", "05"]

    for topic_id in topic_ids:
        download_if_missing(
            f"{base_url}/{topic_id}/dialogue.json?download=true",
            os.path.join(target_dir, topic_id, "dialogue.json"),
        )
        download_if_missing(
            f"{base_url}/{topic_id}/qa_{topic_id}.json?download=true",
            os.path.join(target_dir, topic_id, f"qa_{topic_id}.json"),
        )


if __name__ == "__main__":
    download_evermembench_data()
