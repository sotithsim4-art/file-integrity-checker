# File Integrity Checker

A Python tool that detects if files have been tampered with by comparing their cryptographic hashes against a saved baseline.

## What it does
- Creates a baseline snapshot of all files in a folder using SHA-256 hashing
- Detects if any file has been modified, deleted, or added since the baseline was taken
- Alerts you to any changes

## How to run

```
python file_integrity.py
```

## Example

```
File Integrity Checker
----------------------
Enter the folder path to monitor: C:\Users\16194\Documents\test

1. Create baseline
2. Check integrity

Choose an option: 2

Integrity Check Results:
------------------------
ALERT: 'secret.txt' has been MODIFIED.
OK: 'notes.txt' is unchanged.
```

## Why this matters

File integrity monitoring is a core technique in cybersecurity used to detect malware, unauthorized changes, and insider threats.
