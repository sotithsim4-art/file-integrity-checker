import hashlib
import os
import json

BASELINE_FILE = "baseline.json"

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_baseline(folder):
    baseline = {}
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            baseline[filename] = hash_file(filepath)
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)
    print(f"Baseline created for {len(baseline)} file(s).")

def check_integrity(folder):
    if not os.path.exists(BASELINE_FILE):
        print("No baseline found. Run option 1 first.")
        return

    with open(BASELINE_FILE, "r") as f:
        baseline = json.load(f)

    print("\nIntegrity Check Results:")
    print("------------------------")
    changes_found = False

    for filename, original_hash in baseline.items():
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            print(f"ALERT: '{filename}' is MISSING.")
            changes_found = True
        else:
            current_hash = hash_file(filepath)
            if current_hash != original_hash:
                print(f"ALERT: '{filename}' has been MODIFIED.")
                changes_found = True
            else:
                print(f"OK: '{filename}' is unchanged.")

    if not changes_found:
        print("All files are intact. No changes detected.")

print("File Integrity Checker")
print("----------------------")
folder = input("Enter the folder path to monitor: ").strip()

if not os.path.isdir(folder):
    print("Invalid folder path.")
else:
    print("\n1. Create baseline")
    print("2. Check integrity")
    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        create_baseline(folder)
    elif choice == "2":
        check_integrity(folder)
    else:
        print("Invalid choice.")
