import os
import requests


def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded to {target_path}")
    else:
        print(f"Failed to download {url}: {response.status_code}")


def download_membench_data():
    base_url = "https://raw.githubusercontent.com/import-myself/Membench/main/MemData/"
    # List of files to download
    paths = {
        "FirstAgent": [
            "RecMultiSession.json",
            "aggregative.json",
            "comparative.json",
            "conditional.json",
            "highlevel.json",
            "highlevel_rec.json",
            "knowledge_update.json",
            "lowlevel_rec.json",
            "noisy.json",
            "post_processing.json",
            "simple.json",
        ],
        "ThirdAgent": [
            "RecMultiSession.json",
            "aggregative.json",
            "comparative.json",
            "conditional.json",
            "highlevel.json",
            "highlevel_rec.json",
            "knowledge_update.json",
            "lowlevel_rec.json",
            "noisy.json",
            "post_processing.json",
            "simple.json",
        ],
    }
    target_dir = "tests/benchmarks/membench/data/MemData"

    for agent_type, files in paths.items():
        for file_name in files:
            url = f"{base_url}{agent_type}/{file_name}"
            target_path = os.path.join(target_dir, agent_type, file_name)
            if not os.path.exists(target_path):
                download_file(url, target_path)
            else:
                print(f"File already exists: {target_path}")


if __name__ == "__main__":
    download_membench_data()
