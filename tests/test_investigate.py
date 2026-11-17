"""Regression checks for business rules and failure behaviour."""

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_DIR / "src/investigate.py"
spec = importlib.util.spec_from_file_location("investigate", SCRIPT)
investigate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(investigate)


class InvestigationTests(unittest.TestCase):
    def test_sample_reports_match_known_input(self):
        duplicates, invalid, summary = investigate.inspect_transactions(
            PROJECT_DIR / "data/transactions.csv")
        self.assertEqual(summary["total_records"], 15)
        self.assertEqual(summary["valid_records"], 3)
        self.assertEqual(summary["invalid_records"], 12)
        self.assertEqual(summary["duplicate_occurrences"], 1)
        self.assertEqual(duplicates[0]["row_number"], 4)
        self.assertEqual(summary["issue_counts"]["non_finite_amount"], 2)
        self.assertEqual(len(invalid), 12)

    def test_amount_rules_and_multiple_issues(self):
        valid = dict(zip(investigate.FIELDS,
                         ["A", "C1", "0", "COMPLETED", "2026-11-16T09:00:00"]))
        self.assertEqual(investigate.validate_record(valid), [])
        for amount, expected in [("-1", "negative_amount"), ("abc", "malformed_amount"),
                                 ("", "missing_amount"), ("NaN", "non_finite_amount"),
                                 ("Infinity", "non_finite_amount")]:
            with self.subTest(amount=amount):
                self.assertEqual(investigate.validate_record({**valid, "amount": amount}),
                                 [expected])
        issues = investigate.validate_record({field: "" for field in investigate.FIELDS})
        self.assertEqual(len(issues), 5)

    def test_empty_wrong_columns_and_repeated_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.csv"
            header = ",".join(investigate.FIELDS) + "\n"
            source.write_text(header, encoding="utf-8")
            self.assertEqual(investigate.inspect_transactions(source)[2]["total_records"], 0)
            source.write_text(header + "A,C1,10,COMPLETED,2026-11-16\n" * 3
                              + ",C1,10,COMPLETED,2026-11-16\n" * 2
                              + "B,C1,10,COMPLETED\n"
                              + "C,C1,10,COMPLETED,2026-11-16,extra\n", encoding="utf-8")
            _, invalid, summary = investigate.inspect_transactions(source)
            self.assertEqual(summary["duplicate_occurrences"], 2)
            self.assertEqual(summary["issue_counts"]["missing_transaction_id"], 2)
            self.assertEqual(summary["issue_counts"]["wrong_column_count"], 2)
            self.assertIn("extra", invalid[-1]["raw_record"])

    def test_cli_reports_and_fatal_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "reports"
            result = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            for filename, expected in [("duplicates.csv", 1), ("invalid_records.csv", 12)]:
                with (output / filename).open(newline="", encoding="utf-8") as report:
                    self.assertEqual(len(list(csv.DictReader(report))), expected)
            self.assertEqual(summary["invalid_records"], 12)
            bad = Path(temp) / "bad.csv"
            bad.write_text("incorrect,header\n", encoding="utf-8")
            for source in [bad, Path(temp) / "missing.csv"]:
                failed = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)],
                                        capture_output=True, text=True)
                self.assertEqual(failed.returncode, 1)
                self.assertIn("Investigation failed", failed.stderr)


if __name__ == "__main__":
    unittest.main()
