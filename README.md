# Python Data Troubleshooting

This simulated enterprise transaction troubleshooting lab explores a support scenario: a transaction export has unexpected totals or statuses. It flags suspect records and produces evidence for investigation without changing the source file. All records are synthetic. This is a beginner-to-intermediate learning project, not a production system or a claim of professional support experience.

## Language Notes

This repository uses English as the primary technical language.

Short Traditional Chinese and conversational Malaysian Malay notes are included to support learning and interview revision.

Technical terms are intentionally kept in English where commonly used in the industry.

Traditional Chinese:
繁中備註主要用來快速理解和複習技術概念，部分常用技術詞會保留英文。

Bahasa Melayu:
Nota BM guna gaya yang biasa ditutur di Malaysia supaya lebih senang faham dan explain masa interview. Istilah technical yang biasa digunakan akan kekal dalam English.

See [Python Learning Notes](LEARNING_NOTES.md) for concise explanations of collections, validation, exception handling, and troubleshooting.

## Run

Use Python 3.10 or newer. No third-party dependencies are required. From this project folder:

```powershell
python src/investigate.py
python src/investigate.py --input data/transactions.csv --output output
```

Default paths are relative to the script's project folder, so the first command also works when called using its full path from elsewhere. A successful investigation exits with code 0 even when it finds invalid records. An unreadable input, invalid header, or report-writing failure exits with code 1. Existing reports in the chosen output folder are replaced; use a different folder to preserve earlier runs.

Run regression checks from this project folder with `python -m unittest discover -s tests -v`. They cover known report counts, amount rules, overlapping issues, header-only input, wrong column counts, repeated and missing IDs, and fatal input errors.

## Approach and business rules

The script reads CSV rows, strips surrounding whitespace, validates fields, tracks seen transaction IDs in a set, and collects rule failures. Amounts use `Decimal` to avoid binary floating-point rounding. The lab assumes nonnegative amounts, including zero, are allowed. Refunds would need a separate rule agreed with the business. Statuses are case-sensitive: `COMPLETED`, `PENDING`, and `FAILED`.

Transaction ID, customer ID, amount, status, and timestamp are required. Timestamps must parse using Python's ISO-format parser; timezone presence is not enforced. A structurally malformed row is flagged. A malformed CSV stream or unexpected header stops processing with an error. A CSV that contains only the correct header produces empty reports.

## Example input and output

The 15 sample rows include a repeated `TX001`, a missing customer, a negative amount, `abc`, blank amounts, `NaN`, `Infinity`, an unknown status, missing fields, and an invalid timestamp.

- `output/duplicates.csv`: later occurrences of a previously seen nonempty transaction ID. The first occurrence is not included; this is an investigation flag, not proof of an identical financial event.
- `output/invalid_records.csv`: one row per rejected record, with semicolon-separated issues, original row evidence as JSON, and a logical CSV row number (header is row 1).
- `output/summary.json`: 15 total, 3 valid, 12 invalid, and 1 later duplicate occurrence.
- `output/examples/`: verified example reports committed for review. Fresh reports directly under `output/` are ignored by Git.

The first occurrence of `TX001` passes validation. The later occurrence fails the duplicate rule. Counts describe this sequential policy, not all members of a duplicate group. Issue counts can exceed invalid-record counts when one record has several issues. Original CSV data remains the authoritative evidence; normalized report fields have whitespace removed. Do not open untrusted CSV reports in spreadsheet software without considering formula injection. This lab does not sanitize source values into spreadsheet-safe text.

## Root cause analysis workflow

1. **Understand:** confirm the incident, affected time range, and business rules.
2. **Reproduce:** run validation against the same export and retain the source.
3. **Isolate:** group failures by issue, ID, and time; compare application logs.
4. **Validate:** verify a suspected explanation against independent evidence.
5. **Fix:** propose an approved correction at the source; this script makes no corrections.
6. **Prevent:** add upstream validation, idempotency checks, alerts, and regression checks.

A duplicate ID is a symptom. Retried requests, export duplication, or integration mapping errors are hypotheses until logs and source-system records support them. This distinction matters in enterprise application support.

## Interview Talking Points

- A set provides average O(1) membership checks, avoiding a repeated scan of earlier IDs.
- Reading and validating n rows is approximately O(n) for bounded field lengths. Sorting k duplicate IDs for the summary costs O(k log k).
- Memory is O(n) in the worst case because IDs and invalid records are retained. Reading through an iterator alone does not make the whole program constant-memory.
- For larger exports, stream reports to disk and use a database unique index, external sort, or partitioned processing for duplicate detection. Keep reconciliation rules explicit.
- Similar validation could help investigate approved SAP/ERP exports, checking IDs, statuses, relationships, and totals. This exercise does not connect to SAP and does not claim SAP experience.
- Skills demonstrated: functions, exceptions, reusable validation, CSV/JSON handling, command-line arguments, and evidence-based diagnosis.

> 🇹🇼 繁中備註：set 的 membership check 平均是 O(1)，但保存 ID 和報表仍會使用記憶體。面試時要分清楚執行時間、記憶體用量和真正已驗證的能力。
>
> 🇲🇾 BM: Membership check dalam set purata O(1), tapi simpan ID dan report masih guna memory. Masa interview, bezakan masa proses, penggunaan memory dan apa yang lab ni betul-betul tunjuk.

## Quick Interview Revision

### Why use a set?

English: Check whether an ID has already appeared before adding it; average membership lookup is O(1).

> 🇹🇼 繁中備註：先用 set 查 ID 是否出現過，再加入；平均查找時間是 O(1)。
>
> 🇲🇾 BM: Check ID tu dah ada dalam set atau belum, baru tambah. Lookup purata O(1).

### What is an invalid record?

English: A row that violates one or more validation rules; record all issues without silently changing the input.

> 🇹🇼 繁中備註：一筆資料可能違反多個規則；要完整回報，不要默默改掉來源資料。
>
> 🇲🇾 BM: Satu row boleh langgar beberapa rule. Report semua isu, jangan ubah data asal senyap-senyap.

### How do you establish root cause?

English: Reproduce and isolate the issue, then validate the suspected cause with logs and source records before fixing it.

> 🇹🇼 繁中備註：先重現並縮小問題範圍，再用 log 和來源資料確認原因，不能只看現象就下結論。
>
> 🇲🇾 BM: Reproduce dan kecilkan skop dulu, kemudian semak log dan rekod asal untuk sahkan punca sebelum fix.

## Interview questions

**Why Decimal?** Financial decimal values should not acquire binary floating-point rounding artifacts. Currency precision and rounding policies still need business rules.

**Why catch exceptions?** Invalid amounts should become reportable issues; inaccessible files should produce a clear failure rather than a misleading success.

**Would you delete duplicate rows automatically?** No. Check transaction identity, source logs, and business rules before an approved correction.

**How do you validate the output?** Compare known faulty input rows with report issues, check totals, and test empty data, malformed rows, and missing files.
