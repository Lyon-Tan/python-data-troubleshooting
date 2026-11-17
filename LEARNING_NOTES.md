# Python Learning Notes

Short revision notes for this simulated transaction troubleshooting lab. English is primary; the notes below reinforce the existing [README](README.md) without translating the code.

## List and dictionary

A `list` stores an ordered sequence, such as invalid records. A `dictionary` maps keys to values, such as a CSV row's `amount` and `status`.

> 繁中備註：list 用來依序存放多筆資料；dictionary 用 key 找 value，例如一筆交易的 `amount` 和 `status`。
>
> 🇲🇾 BM: List simpan rekod ikut urutan. Dictionary pula guna key untuk dapatkan value, macam `amount` dan `status` bagi satu transaction.

## Set and duplicate detection

A `set` stores unique values and provides average O(1) membership checks. Check whether an ID is present **before** adding it; skip blank IDs here and report them through validation.

> 繁中備註：set 可以快速檢查 ID 是否已出現。先檢查再加入；空白 ID 要另外回報，不能當成正常 ID。
>
> 🇲🇾 BM: Set sesuai untuk check ID tu dah pernah muncul atau belum. Check dulu, baru tambah. ID kosong kena report berasingan.

## Functions and loops

A `function` groups reusable work, such as validating one record. A loop applies that work to each CSV row, keeping the validation rules in one place.

> 繁中備註：function 把可重用的步驟集中起來；loop 逐筆處理資料，不需要為每一筆重寫 validation。
>
> 🇲🇾 BM: Function kumpulkan kerja yang boleh guna semula. Loop proses setiap row, jadi tak perlu tulis validation yang sama berulang kali.

## CSV processing

`csv.DictReader` reads CSV rows as dictionaries and handles CSV quoting. Do not use a simple comma split: a quoted field may contain commas.

> 繁中備註：`csv.DictReader` 會把每列讀成 dictionary，也能處理引號內的逗號；直接用逗號切字串容易切錯。
>
> 🇲🇾 BM: `csv.DictReader` baca setiap row sebagai dictionary dan faham CSV quoting. Jangan terus split ikut koma sebab value dalam quotes pun boleh ada koma.

## Input validation and invalid records

Input validation checks required fields and business rules. An invalid record may have several issues, so issue counts can exceed the number of invalid records. Validation helps prevent misleading transaction totals and missing-identifier problems from going unnoticed.

> 繁中備註：validation 會檢查必填欄位和金額等規則。一筆 invalid record 可能有多個問題，所以問題總數不一定等於異常筆數；這有助於找出交易資料的錯誤。
>
> 🇲🇾 BM: Validation check field wajib dan rules macam amount. Satu invalid record boleh ada beberapa masalah, jadi jumlah isu boleh lebih daripada jumlah rekod yang invalid. Ini bantu elakkan jumlah transaction yang mengelirukan.

## Malformed data and exception handling

Malformed data has an unexpected format, such as `abc` in an amount field. Catch the expected parsing exception and report the issue. A missing file is a fatal run error; a malformed amount is a record-level issue. `NaN` and infinity also need a finite-value check even when parsing succeeds.

> 繁中備註：malformed data 是格式不對的資料。用 exception handling 回報解析問題；單筆金額錯誤和整個檔案讀不到，要分開處理。能解析的 `NaN` 也不代表有效金額。
>
> 🇲🇾 BM: Malformed data maksudnya format tak betul, macam amount jadi `abc`. Handle exception yang dijangka dan report isu tu. File tak jumpa lain daripada satu row yang salah; `NaN` pun kena reject walaupun boleh parse.

## Duplicate occurrences versus duplicate groups

For IDs `A, B, A, A`, this lab reports two later duplicate occurrences and one distinct duplicated ID. The first `A` is not placed in the duplicates report. Repeated IDs are investigation leads, not instructions to delete records.

> 繁中備註：`A, B, A, A` 有兩次後續重複，但只有一個重複 ID。第一筆 `A` 不列入重複報表；看到重複也不能直接刪資料。
>
> 🇲🇾 BM: Untuk `A, B, A, A`, ada dua kemunculan berulang tapi cuma satu ID yang berulang. `A` yang pertama tak masuk report duplicates. Kena siasat dulu sebelum padam rekod.

## Root cause analysis

Use **Understand → Reproduce → Isolate → Validate → Fix → Prevent**. A duplicate is a symptom; retry behaviour or an export defect remains a hypothesis until source records and logs support it.

> 繁中備註：先理解、重現和縮小問題範圍，再用證據確認原因，修正並預防。重複資料只是現象，不能直接認定是重試造成的。
>
> 🇲🇾 BM: Faham masalah, reproduce, kecilkan skop, verify punca, kemudian fix dan cegah berulang. Duplicate tu simptom; semak log dulu sebelum kata retry yang jadi punca.

## Time complexity and scale

For bounded field lengths, validation is approximately O(n), plus O(k log k) to sort k duplicated IDs. Retained IDs and reports can use O(n) memory. A set avoids repeatedly scanning a growing list; larger datasets may need streamed reports and database-backed duplicate checks.

> 繁中備註：主要工作大約是 O(n)，重複 ID 排序另需 O(k log k)。資料和報表仍會占用 O(n) 記憶體；逐列讀檔不代表整個程式只用固定記憶體。
>
> 🇲🇾 BM: Kerja utama lebih kurang O(n), tambah O(k log k) untuk sort ID berulang. Memory masih boleh jadi O(n) sebab ID dan report disimpan. Baca row satu-satu tak semestinya guna memory yang tetap.
