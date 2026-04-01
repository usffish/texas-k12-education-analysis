import os
import sys
import json
import requests
from datetime import datetime

# Create the folder where we will save the downloaded files
os.makedirs("data/raw/", exist_ok=True)

# ----- Dataset 1: Annual Leavers 2023-24 -----

# The URL where the file lives on the TEA website
leavers_url = "https://tea.texas.gov/reports-and-data/school-performance/accountability-research/completion-graduation-and-dropout/annual-leavers-2023-24"

# Where we want to save it on our computer
leavers_path = "data/raw/leavers_2023_24.xlsx"

# Download the file
print("Downloading leavers dataset...")
leavers_response = requests.get(leavers_url)

# Make sure the download worked (200 means OK)
if leavers_response.status_code != 200:
    print(f"ERROR: Failed to download {leavers_url} — HTTP {leavers_response.status_code}")
    sys.exit(1)

# Save the file to disk
with open(leavers_path, "wb") as f:
    f.write(leavers_response.content)

print(f"Saved to {leavers_path}")

# ----- Dataset 2: Enrollment Trends 2023-24 -----

enrollment_url = "https://tea.texas.gov/reports-and-data/school-performance/accountability-research/enrollment-trends"
enrollment_path = "data/raw/enrollment_2023_24.html"

print("Downloading enrollment dataset...")
enrollment_response = requests.get(enrollment_url)

if enrollment_response.status_code != 200:
    print(f"ERROR: Failed to download {enrollment_url} — HTTP {enrollment_response.status_code}")
    sys.exit(1)

with open(enrollment_path, "wb") as f:
    f.write(enrollment_response.content)

print(f"Saved to {enrollment_path}")

# ----- Write the manifest -----
# The manifest is a record of what we downloaded and when

now = datetime.utcnow().isoformat() + "Z"

manifest = [
    {
        "dataset": "leavers_2023_24",
        "source_url": leavers_url,
        "file_format": "xlsx",
        "local_path": leavers_path,
        "collected_at": now,
    },
    {
        "dataset": "enrollment_2023_24",
        "source_url": enrollment_url,
        "file_format": "html",
        "local_path": enrollment_path,
        "collected_at": now,
    },
]

# Save the manifest as a JSON file
with open("data/raw/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("Manifest saved to data/raw/manifest.json")
print("All done! 2 datasets downloaded successfully.")
