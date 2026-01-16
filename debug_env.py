import sys
import os

site_packages = next((p for p in sys.path if 'site-packages' in p), None)
pth_file = os.path.join(site_packages, '_letta.pth')
if os.path.exists(pth_file):
    print(f"Content of {pth_file}:")
    with open(pth_file, 'r') as f:
        print(f.read())
else:
    print(f"{pth_file} not found")
