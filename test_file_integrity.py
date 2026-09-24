import tempfile
import unittest
from pathlib import Path

import file_integrity


class FileIntegrityTests(unittest.TestCase):
    def test_nested_added_and_modified_files_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watched = root / "watched"
            nested = watched / "nested"
            nested.mkdir(parents=True)
            (watched / "a.txt").write_text("one", encoding="utf-8")
            (nested / "c.txt").write_text("deep", encoding="utf-8")
            baseline = root / "baseline.json"

            created = file_integrity.create_baseline(watched, baseline)
            self.assertEqual(set(created["files"]), {"a.txt", "nested/c.txt"})

            (watched / "a.txt").write_text("two", encoding="utf-8")
            (watched / "a.txt").unlink()
            (watched / "b.txt").write_text("new", encoding="utf-8")
            findings = {
                name: kind
                for kind, name in file_integrity.check_integrity(watched, baseline)
            }

            self.assertEqual(findings["a.txt"], "missing")
            self.assertEqual(findings["b.txt"], "added")
            self.assertEqual(findings["nested/c.txt"], "ok")

    def test_corrupt_baseline_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watched = root / "watched"
            watched.mkdir()
            baseline = root / "baseline.json"
            baseline.write_text("{", encoding="utf-8")
            self.assertEqual(file_integrity.check_integrity(watched, baseline), [])


if __name__ == "__main__":
    unittest.main()
