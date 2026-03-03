import os
import requests

def download_locomo_data():
    url = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
    target_dir = "tests/benchmarks/locomo/data"
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "locomo10.json")
    
    print(f"Downloading LOCOMO data from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded to {target_path}")
    else:
        print(f"Failed to download data: {response.status_code}")

if __name__ == "__main__":
    download_locomo_data()
