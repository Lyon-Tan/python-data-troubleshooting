# Python Data Troubleshooting

## Overview

This simulated enterprise transaction troubleshooting lab explores a support scenario: a transaction export has unexpected totals or statuses. It flags suspect records and produces evidence for investigation without changing the source file. All records are synthetic. This is a beginner-to-intermediate learning project, not a production system or a claim of professional support experience.

The Python foundation of the Technical Interview Foundation Portfolio: reusable practice in validation, automation, and evidence-based investigation.

## Language Notes

This repository uses English as the primary technical language.

Short Traditional Chinese and conversational Malaysian Malay notes are included to support learning and interview revision.

Technical terms are intentionally kept in English where commonly used in the industry.

Traditional Chinese:
繁中備註主要用來快速理解和複習技術概念，部分常用技術詞會保留英文。

Bahasa Melayu:
Nota BM guna gaya yang biasa ditutur di Malaysia supaya lebih senang faham dan explain masa interview. Istilah technical yang biasa digunakan akan kekal dalam English.

See [Python Learning Notes](LEARNING_NOTES.md) for concise explanations of collections, validation, exception handling, and troubleshooting.

## Why This Project Exists

Build a small investigation tool that is easy to explain, rerun, and adapt to new interview scenarios. The emphasis is on clear rules, trustworthy evidence, and knowing when a suspicious row needs investigation rather than automatic correction.

## Business / Technical Scenario

An analyst receives a transaction CSV after a reported discrepancy. The task is to identify suspect records, explain why they were flagged, and preserve the source for follow-up investigation. The scenario and all records are simulated.

## Skills Demonstrated

- Python functions, loops, dictionaries, sets, and exception handling.
- CSV/JSON processing, command-line arguments, and reusable input validation.
- Decimal amount checks, duplicate semantics, and interpretable reports.
- Regression checks, basic complexity reasoning, and root cause analysis.

## Architecture / Data Flow

```text
data/transactions.csv
  -> src/investigate.py
  -> normalize fields -> validate rules -> check seen IDs
  -> output/duplicates.csv + output/invalid_records.csv + output/summary.json
```

This is one local command-line process. There is no database, API service, or automatic repair step.

## Dataset / Data Model

The 15 sample rows include a repeated `TX001`, a missing customer, a negative amount, `abc`, blank amounts, `NaN`, `Infinity`, an unknown status, missing fields, and an invalid timestamp.

Each row contains `transaction_id`, `customer_id`, `amount`, `status`, and `timestamp`. The input is [data/transactions.csv](data/transactions.csv); the required header order is defined in [src/investigate.py](src/investigate.py).

## How It Works

The script reads CSV rows, strips surrounding whitespace, validates fields, tracks seen transaction IDs in a set, and collects rule failures. Amounts use `Decimal` to avoid binary floating-point rounding. The lab assumes nonnegative amounts, including zero, are allowed. Refunds would need a separate rule agreed with the business. Statuses are case-sensitive: `COMPLETED`, `PENDING`, and `FAILED`.

Transaction ID, customer ID, amount, status, and timestamp are required. Timestamps must parse using Python's ISO-format parser; timezone presence is not enforced. A structurally malformed row is flagged. A CSV parser error or unexpected header stops processing with an error. A CSV that contains only the correct header produces empty reports.

> 繁中備註：逐列讀取 CSV，檢查欄位和金額，再用 set 判斷 ID 是否重複；來源資料不會被修改。
>
> ENG: Read each CSV row, validate its fields and amount, and check IDs against a set without changing the source.
>
> BM: Baca CSV row demi row, check field dan amount, kemudian guna set untuk cari ID berulang tanpa ubah data asal.

## How to Run

Use Python 3.10 or newer. No third-party dependencies are required. From this project folder:

```powershell
python src/investigate.py
python src/investigate.py --input data/transactions.csv --output output
```

Default paths are relative to the script's project folder, so the first command also works when called using its full path from elsewhere. A successful investigation exits with code 0 even when it finds invalid records. An unreadable input, invalid header, or report-writing failure exits with code 1. Existing reports in the chosen output folder are replaced; use a different folder to preserve earlier runs.

Run regression checks from this project folder with `python -m unittest discover -s tests -v`. They cover known report counts, amount rules, overlapping issues, header-only input, wrong column counts, repeated and missing IDs, and fatal input errors.

> 繁中備註：在 repository 資料夾執行上方 Python 指令，再執行測試；重跑會覆寫指定 output 資料夾的報表。
>
> ENG: Run the Python commands from this repository folder, then run the tests; reruns replace reports in the selected output folder.
>
> BM: Run command Python di atas dari folder repo, kemudian run test. Kalau run semula, report dalam folder output yang dipilih akan diganti.

## Example Investigation

Inspect the two `TX001` rows in the sample. The first passes the duplicate check, while the later occurrence is included in `duplicates.csv` and carries `duplicate_transaction_id` in `invalid_records.csv`. Compare the source rows before proposing a cause: the repeated identifier alone does not establish a retry or a duplicated financial event.

> 繁中備註：比較兩筆 `TX001`；後出現的那筆會被標記為重複，但仍要查來源資料才能確認原因。
>
> ENG: Compare the two `TX001` rows; the later occurrence is flagged, but the cause still needs source evidence.
>
> BM: Bandingkan dua row `TX001`. Yang muncul kemudian akan kena flag duplicate, tapi punca masih kena semak dengan rekod asal.

## Expected Results

- `output/duplicates.csv`: later occurrences of a previously seen nonempty transaction ID. The first occurrence is not included; this is an investigation flag, not proof of an identical financial event.
- `output/invalid_records.csv`: one row per rejected record, with semicolon-separated issues, original row evidence as JSON, and a logical CSV row number (header is row 1).
- `output/summary.json`: 15 total, 3 valid, 12 invalid, and 1 later duplicate occurrence.
- `output/examples/`: verified example reports committed for review. Fresh reports directly under `output/` are ignored by Git.

The first occurrence of `TX001` passes validation. The later occurrence fails the duplicate rule. Counts describe this sequential policy, not all members of a duplicate group. Issue counts can exceed invalid-record counts when one record has several issues. Original CSV data remains the authoritative evidence; normalized report fields have whitespace removed. Do not open untrusted CSV reports in spreadsheet software without considering formula injection. This lab does not sanitize source values into spreadsheet-safe text.

> 繁中備註：範例共有 15 筆，3 筆通過、12 筆被標記；1 次後續重複也包含在被標記的 12 筆內。
>
> ENG: Expect 15 rows: 3 pass and 12 are flagged, with the one later duplicate included among the flagged rows.
>
> BM: Jangka 15 row: 3 lulus dan 12 kena flag. Satu duplicate yang muncul kemudian termasuk dalam 12 row tu.

## Troubleshooting / Root Cause Analysis

1. **Understand:** confirm the incident, affected time range, and business rules.
2. **Reproduce:** run validation against the same export and retain the source.
3. **Isolate:** group failures by issue, ID, and time; compare application logs.
4. **Validate:** verify a suspected explanation against independent evidence.
5. **Fix:** propose an approved correction at the source; this script makes no corrections.
6. **Prevent:** add upstream validation, idempotency checks, alerts, and regression checks.

A duplicate ID is a symptom. Retried requests, export duplication, or integration mapping errors are hypotheses until logs and source-system records support them. This distinction matters in enterprise application support.

> 繁中備註：先重現並縮小問題範圍，再用證據確認原因；不要看到 duplicate 就直接刪除或修正資料。
>
> ENG: Reproduce and isolate the issue, then validate its cause before proposing a correction.
>
> BM: Reproduce dan kecilkan skop masalah dulu. Sahkan punca dengan bukti sebelum cadang pembetulan.

## Limitations

- Rules are deliberately simple: no refund policy, currency field, decimal-place rule, or mandatory timezone validation.
- IDs and reports remain in memory; the full process is not constant-memory.
- CSV quoting uses the standard reader defaults, not comprehensive strict syntax validation.
- Reports flag symptoms; they do not establish root cause, reconcile payments, or correct source data.
- Output writes are not atomic; a write failure may leave partial reports. Existing reports are replaced.
- CSV values are not escaped for spreadsheet formula safety. This is a local synthetic lab, not a production data-control system.

## Interview Talking Points

- A set provides average O(1) membership checks, avoiding a repeated scan of earlier IDs.
- Reading and validating n rows is approximately O(n) for bounded field lengths. Sorting k duplicate IDs for the summary costs O(k log k).
- Memory is O(n) in the worst case because IDs and invalid records are retained. Reading through an iterator alone does not make the whole program constant-memory.
- For larger exports, stream reports to disk and use a database unique index, external sort, or partitioned processing for duplicate detection. Keep reconciliation rules explicit.
- Similar validation could help investigate approved SAP/ERP exports, checking IDs, statuses, relationships, and totals. This exercise does not connect to SAP and does not claim SAP experience.
- Skills demonstrated: functions, exceptions, reusable validation, CSV/JSON handling, command-line arguments, and evidence-based diagnosis.

> 繁中備註：set 的 membership check 平均是 O(1)，但保存 ID 和報表仍會使用記憶體。面試時要分清楚執行時間、記憶體用量和真正已驗證的能力。
>
> 🇲🇾 BM: Membership check dalam set purata O(1), tapi simpan ID dan report masih guna memory. Masa interview, bezakan masa proses, penggunaan memory dan apa yang lab ni betul-betul tunjuk.

### Interview questions

**Why Decimal?** Financial decimal values should not acquire binary floating-point rounding artifacts. Currency precision and rounding policies still need business rules.

**Why catch exceptions?** Invalid amounts should become reportable issues; inaccessible files should produce a clear failure rather than a misleading success.

**Would you delete duplicate rows automatically?** No. Check transaction identity, source logs, and business rules before an approved correction.

**How do you validate the output?** Compare known faulty input rows with report issues, check totals, and test empty data, malformed rows, and missing files.

## Quick Interview Revision

### Why use a set?

English: Check whether an ID has already appeared before adding it; average membership lookup is O(1).

> 繁中備註：先用 set 查 ID 是否出現過，再加入；平均查找時間是 O(1)。
>
> 🇲🇾 BM: Check ID tu dah ada dalam set atau belum, baru tambah. Lookup purata O(1).

### What is an invalid record?

English: A row that violates one or more validation rules; record all issues without silently changing the input.

> 繁中備註：一筆資料可能違反多個規則；要完整回報，不要默默改掉來源資料。
>
> 🇲🇾 BM: Satu row boleh langgar beberapa rule. Report semua isu, jangan ubah data asal senyap-senyap.

### How do you establish root cause?

English: Reproduce and isolate the issue, then validate the suspected cause with logs and source records before fixing it.

> 繁中備註：先重現並縮小問題範圍，再用 log 和來源資料確認原因，不能只看現象就下結論。
>
> 🇲🇾 BM: Reproduce dan kecilkan skop dulu, kemudian semak log dan rekod asal untuk sahkan punca sebelum fix.

## Role Relevance

These are examples of transferable practice, not proof of employment experience, SAP/FICO expertise, or production operations.

| Relevant area | Transferable practice demonstrated |
| --- | --- |
| Application Support | Triage invalid records, preserve evidence, and distinguish record failures from run failures. |
| ERP / Enterprise Operations | Validate exported identifiers, amounts, and statuses; no ERP connection is implemented. |
| System Analyst | Explain field contracts, business rules, failure behaviour, and data flow. |
| Data Analyst | Recognize data quality issues before trusting transaction totals. |
| Automation | Replace repetitive CSV inspection with a repeatable command-line check. |
| Technical Consulting | Explain assumptions, findings, limitations, and proportionate next steps. |
| Fraud Technology | Practise checking suspicious transaction data; this does not detect or prove fraud. |

## Future Improvements

Planned possibilities only; none of the following is implemented:

- Database-backed validation and duplicate checks.
- Structured logging with useful run context.
- Larger dataset handling through streamed reports and bounded memory.
- API input with an explicit request contract.
- Automated reconciliation against independent payment records.

Choose one improvement at a time and define acceptance criteria before changing the implementation.

## Learning Notes

Use [LEARNING_NOTES.md](LEARNING_NOTES.md) for concise English-led revision with Traditional Chinese and conversational Malaysian Malay notes. Begin with sets and validation, then practise explaining duplicate counts and root cause analysis. The simulated scope applies in every language.
