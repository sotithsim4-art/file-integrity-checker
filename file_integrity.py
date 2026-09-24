import hashlib
import json
import os
from pathlib import Path

BASELINE_FILE = "baseline.json"


def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as handle:
        for chunk in iter(lambda: handle.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def tracked_files(folder):
    root = Path(folder).resolve()
    found = {}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            relative = path.relative_to(root).as_posix()
            if relative == "baseline.json":
                continue
            found[relative] = path
    return root, found


def safe_path(root, relative):
    if not isinstance(relative, str) or relative == "":
        return None
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def create_baseline(folder, baseline_file=BASELINE_FILE):
    root, files = tracked_files(folder)
    baseline = {"folder": str(root), "files": {}}
    for relative, path in sorted(files.items()):
        try:
            baseline["files"][relative] = hash_file(path)
        except OSError as exc:
            print(f"Skipped '{relative}': {exc}")
    with open(baseline_file, "w", encoding="utf-8") as handle:
        json.dump(baseline, handle, indent=2)
    print(f"Baseline created for {len(baseline['files'])} file(s).")
    return baseline


def check_integrity(folder, baseline_file=BASELINE_FILE):
    if not os.path.exists(baseline_file):
        print("No baseline found. Run option 1 first.")
        return []

    try:
        with open(baseline_file, "r", encoding="utf-8") as handle:
            stored = json.load(handle)
    except (OSError, json.JSONDecodeError):
        print("Baseline file is unreadable. Create a new baseline.")
        return []

    if isinstance(stored, dict) and isinstance(stored.get("files"), dict):
        saved = stored["files"]
        saved_folder = stored.get("folder")
    elif isinstance(stored, dict):
        saved = stored
        saved_folder = None
    else:
        print("Baseline file is unreadable. Create a new baseline.")
        return []

    root, current = tracked_files(folder)
    if saved_folder and Path(saved_folder) != root:
        print(f"Note: this baseline was created for {saved_folder}.")

    print("\nIntegrity Check Results:")
    print("------------------------")
    findings = []

    for relative, original_hash in sorted(saved.items()):
        path = safe_path(root, relative)
        if path is None:
            print(f"ALERT: '{relative}' is outside the folder and was ignored.")
            findings.append(("ignored", relative))
            continue
        if not path.is_file():
            print(f"ALERT: '{relative}' is MISSING.")
            findings.append(("missing", relative))
            continue
        try:
            current_hash = hash_file(path)
        except OSError as exc:
            print(f"ALERT: '{relative}' could not be read ({exc}).")
            findings.append(("error", relative))
            continue
        if current_hash != original_hash:
            print(f"ALERT: '{relative}' has been MODIFIED.")
            findings.append(("modified", relative))
        else:
            print(f"OK: '{relative}' is unchanged.")
            findings.append(("ok", relative))

    for relative in sorted(set(current) - set(saved)):
        print(f"ALERT: '{relative}' has been ADDED.")
        findings.append(("added", relative))

    if not any(kind != "ok" for kind, _ in findings):
        print("All files are intact. No changes detected.")
    return findings


if __name__ == "__main__":
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
