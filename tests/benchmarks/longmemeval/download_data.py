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


def download_longmemeval_data():
    base_url = "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/"
    files = ["longmemeval_oracle.json", "longmemeval_s_cleaned.json", "longmemeval_m_cleaned.json"]
    target_dir = "tests/benchmarks/longmemeval/data"

    for file_name in files:
        url = base_url + file_name
        target_path = os.path.join(target_dir, file_name)
        if not os.path.exists(target_path):
            download_file(url, target_path)
        else:
            print(f"File already exists: {target_path}")


if __name__ == "__main__":
    download_longmemeval_data()
