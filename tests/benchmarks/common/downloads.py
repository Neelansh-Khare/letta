import os
from pathlib import Path

import requests


def download_file(url: str, target_path: str) -> None:
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)


def download_if_missing(url: str, target_path: str) -> None:
    if os.path.exists(target_path):
        print(f"File already exists: {target_path}")
        return
    print(f"Downloading {url} -> {target_path}")
    download_file(url, target_path)


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
