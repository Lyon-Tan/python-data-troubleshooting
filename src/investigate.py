"""Inspect synthetic transactions without changing the source data."""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ["transaction_id", "customer_id", "amount", "status", "timestamp"]
VALID_STATUSES = {"COMPLETED", "PENDING", "FAILED"}
PROJECT_DIR = Path(__file__).resolve().parents[1]


def validate_record(record):
    """Return all rule failures; a row can fail more than one rule."""
    issues = []
    if not record["transaction_id"]:
        issues.append("missing_transaction_id")
    if not record["customer_id"]:
        issues.append("missing_customer_id")
    if not record["amount"]:
        issues.append("missing_amount")
    else:
        try:
            amount = Decimal(record["amount"])
            if not amount.is_finite():
                issues.append("non_finite_amount")
            elif amount < 0:
                issues.append("negative_amount")
        except InvalidOperation:
            issues.append("malformed_amount")
    if record["status"] not in VALID_STATUSES:
        issues.append("invalid_status")
    if not record["timestamp"]:
        issues.append("missing_timestamp")
    else:
        try:
            datetime.fromisoformat(record["timestamp"])
        except ValueError:
            issues.append("invalid_timestamp")
    return issues


def inspect_transactions(input_path):
    seen_ids = set()
    duplicate_ids = set()
    duplicates = []
    invalid_records = []
    issue_counts = Counter()
    total_records = 0
    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"CSV header must be exactly: {','.join(FIELDS)}")
        for row_number, raw_record in enumerate(reader, start=2):
            total_records += 1
            # Preserve malformed source rows as JSON evidence in the report.
            record = {field: (raw_record.get(field) or "").strip() for field in FIELDS}
            issues = validate_record(record)
            if None in raw_record or any(raw_record.get(field) is None for field in FIELDS):
                issues.append("wrong_column_count")
            transaction_id = record["transaction_id"]
            if transaction_id:
                if transaction_id in seen_ids:
                    duplicate_ids.add(transaction_id)
                    duplicates.append({"row_number": row_number, **record})
                    issues.append("duplicate_transaction_id")
                seen_ids.add(transaction_id)
            if issues:
                issue_counts.update(issues)
                invalid_records.append({
                    "row_number": row_number,
                    **record,
                    "issues": ";".join(issues),
                    "raw_record": json.dumps(raw_record, ensure_ascii=False),
                })
    summary = {
        "total_records": total_records,
        "valid_records": total_records - len(invalid_records),
        "invalid_records": len(invalid_records),
        "duplicate_occurrences": len(duplicates),
        "duplicate_transaction_ids": sorted(duplicate_ids),
        "issue_counts": dict(sorted(issue_counts.items())),
    }
    return duplicates, invalid_records, summary


def write_csv(path, fieldnames, records):
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_DIR / "data/transactions.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "output")
    args = parser.parse_args()
    try:
        # Prevent output report names from overwriting the input file.
        report_paths = [args.output / name for name in
                        ("duplicates.csv", "invalid_records.csv", "summary.json")]
        if args.input.resolve() in [path.resolve() for path in report_paths]:
            raise ValueError("Input file must not use an output report path")
        duplicates, invalid_records, summary = inspect_transactions(args.input)
        args.output.mkdir(parents=True, exist_ok=True)
        write_csv(args.output / "duplicates.csv", ["row_number", *FIELDS], duplicates)
        write_csv(args.output / "invalid_records.csv",
                  ["row_number", *FIELDS, "issues", "raw_record"], invalid_records)
        (args.output / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Investigation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    print(f"Reports written to: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
