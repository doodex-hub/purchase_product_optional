# Test Plan — purchase_product_optional

**Module:** `purchase_product_optional`
**Ref:** `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** `cicd/test_design/odoo-testing-taxonomy.md`
**Dibuat oleh:** BACKFILL (Step 03B, backfill)
**Last Updated:** 2026-07-28 (revisi 2 — tambah JS Unit/Tour, lihat catatan di bawah)

> Peta AC → tipe test, mengikuti taxonomy resmi Doodex (`odoo-testing-taxonomy.md`) — jangan buat
> istilah tipe test sendiri. Rujuk file itu untuk decision guide tiap tipe kalau ragu.
>
> **Beda dari SOP normal (`dev-workflow`):** kolom "Step 08 UAT" TIDAK ADA di sini — BACKFILL
> berhenti di Step 07 (QA Testing induk + bug consolidation), tidak pernah sampai UAT.

---

## Revisi 2 (2026-07-28) — JS Unit (QUnit) & Tour ditambahkan

Draft awal Test Plan ini (revisi 1) menandai 13 AC sebagai "tidak bisa dicentang Unit/Integration
sama sekali karena logic-nya JS-only" — ini KELIRU sebagai kesimpulan akhir. `odoo-testing-taxonomy.md`
sendiri sudah diperbaiki hari ini (lihat catatan revisi di dalam file itu) untuk menyertakan **JS Unit
(QUnit, bundle `web.qunit_suite_tests`)** dan **Tour** (`HttpCase.start_tour()`, browser headless
built-in Odoo) — dua mekanisme resmi Odoo yang sebelumnya tidak disebut. Test plan di bawah sudah
direvisi memakai ini. Sebagian besar AC yang tadinya "JS-only, tidak bisa ditest" sekarang punya
QUnit unit test (lihat `static/tests/*.js`) — SEMUA ditulis dengan status **belum dieksekusi
nyata** (sama seperti test Python, Cowork sandbox tidak bisa jalankan browser headless), risiko
ketidakcocokan sintaks API Odoo 17 lebih tinggi dari test Python biasa karena tidak ada environment
nyata untuk verifikasi silang saat menulis — lihat catatan risiko per file di `04A_DEV_TESTING.md`.

---

## Keputusan `04B_API_TEST.md` — TIDAK DIBUAT (N/A)

`controllers/main.py` expose 4 route JSON, HANYA dikonsumsi JS modul sendiri (internal), bukan
konsumen eksternal. Per `odoo-testing-taxonomy.md` §"API Test — kapan aktif" ("skip jika modul
hanya untuk internal Odoo"): `04B_API_TEST.md` **TIDAK dibuat**. Keempat route tetap diverifikasi
lewat Integration test biasa di `04A_DEV_TESTING.md`.

---

## Step 04 — Developer Testing (backfill)

**Output:** `04A_DEV_TESTING.md` + `tests/*.py` (Unit/Integration/Tour-wrapper) +
`static/tests/*.js` (QUnit) + `static/tests/tours/*.js` (Tour). Tidak ada `04B_API_TEST.md`.

| AC | Deskripsi singkat | Unit | JS Unit (QUnit) | Integration | Tour | API |
|---|---|---|---|---|---|---|
| AC-01-01 s/d AC-01-06 | Trigger dialog configurator/grid/warning | | ✓ (`purchase_product_field_tests.js`, risiko lebih tinggi soal `patch()`/`super`) | | ✓ (happy path, 1 skenario) | |
| AC-02-01 | Onchange tanpa partner — currency tidak berubah, param global ditulis | ✓ | | | | |
| AC-02-02 | Onchange partner currency == currency PO — no-op observable | ✓ | | | | |
| AC-02-03 | Onchange partner currency != currency PO — currency TETAP tidak berubah (bug) | ✓ | | | | |
| AC-03-01 | `convert_price` short-circuit kalau currency sama | ✓ | | | | |
| AC-03-03 (F-05) | `convert_price` diduga crash kalau currency benar-benar beda | ✓ | | | | |
| AC-04-01 | Modul load tanpa `SyntaxError` meski parenthesis salah | ✓ | | | | |
| AC-04-02 | `product_add_mode` tidak terdaftar sebagai field nyata | ✓ | | | | |
| AC-05-01 s/d AC-05-03 | Pemilihan harga per-vendor | | ✓ (`product_configurator_dialog_tests.js`, testing method via `.call()`, bukan mount penuh) | | ✓ (tercakup sebagai bagian happy path) | |
| AC-06-01 | Vendor ID dibaca dari DOM (kondisi normal) | | | | ✓ (tour happy path pakai vendor sungguhan) | |
| AC-06-02 | Elemen `id_vendor_0` hilang dari DOM (kondisi anomali) | | ✓ (test penanda perilaku `TypeError`, BUKAN mount dialog sungguhan — lihat catatan di file) | | | |
| AC-07-01 | Optional product diambil rekursif — DATA layer (`get_optional_products` route) | | | ✓ | | |
| AC-07-02 | Optional product dihapus berantai saat parent terakhir hilang | | ✓ (`.call()` pada `_removeProduct`/`_getChildProducts`) | | | |
| AC-08-01 | `_compute_custom_attribute_values` membersihkan value tidak valid | ✓ | | | | |
| AC-08-02 | `_compute_no_variant_attribute_values` membersihkan value tidak valid | ✓ | | | | |
| AC-09-01 | Pembuatan varian dynamic via route `create_product` | | | ✓ | | |
| AC-09-02 | Confirm diblok kalau kombinasi tidak valid (`isPossibleConfiguration`) | | ✓ (`_isPossibleCombination`, pure logic, risiko PALING RENDAH di antara semua QUnit test) | | | |

**Ringkasan:** 9 AC → Unit Python, 5 AC → JS Unit (QUnit — AC-01, AC-05, AC-06-02, AC-07-02,
AC-09-02), 2 AC → Integration, 1 skenario Tour (mencakup AC-01/AC-05/AC-06-01/AC-09 sebagai bagian
alur, bukan 1:1 per-AC), API **N/A**. **0 AC tersisa tanpa test Python/JS sama sekali** — turun
dari 13 di revisi 1. Step 07 (Manual/AI-Browser) TETAP dijalankan untuk semua ini sebagai verifikasi
visual tambahan — QUnit `.call()` style test di modul ini TIDAK mem-verify rendering DOM sungguhan
(kecuali AC-06-02), jadi bukan pengganti penuh untuk AC-01/05/06/07/09-02.

**Smoke Test (happy path, sekarang jadi Tour `purchase_product_optional_happy_path`, bukan cuma
checklist manual):**
1. Buka Purchase Order baru, pilih vendor.
2. Pilih produk template yang punya optional products + atribut varian → dialog Product Configurator
   terbuka (BR-01).
3. Confirm dialog → baris PO tersimpan dengan harga sesuai vendor (BR-05, BR-09).
4. (Belum di-tour, masih manual/07) Buka kembali baris yang sudah dikonfigurasi (edit) → dialog
   terbuka dengan kombinasi tersimpan (US-03).

---

## Step 07 — QA Testing (level AI-interaktif + Smoke human-confirmed, TANPA UAT)

**Output:** `07_QA_TESTING.md` (§3) + `07B_QA_AI_BROWSER.md`. Tour/QUnit di Step 04 TIDAK
menghilangkan kebutuhan Step 07 — keduanya saling melengkapi (QUnit `.call()` = logic terisolasi
tanpa render; Tour = 1 skenario happy path otomatis; AI-Browser = verifikasi visual manusia-sudut-
pandang, termasuk edit-flow US-03 yang belum di-tour).

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser (07B) |
|---|---|---|---|
| AC-01-01 s/d AC-01-06 | Trigger dialog configurator/grid/warning | ✓ | ✓ |
| AC-02-01 s/d AC-02-03 | Onchange currency (cross-check visual field, bug BR-02) | ✓ | |
| AC-03-01 s/d AC-03-03 | Konversi harga di dialog (cross-check angka tampil, F-05) | ✓ | |
| AC-04-01 s/d AC-04-02 | `product_add_mode` dead field (tidak ada UI terkait) | ✓ | |
| AC-05-01 s/d AC-05-03 | Harga per-vendor di dialog | ✓ | ✓ |
| AC-06-01 | Vendor ID dibaca dari DOM (kondisi normal) | ✓ | ✓ |
| AC-06-02 | Elemen `id_vendor_0` hilang dari DOM (kondisi anomali) | ✓ | ✓ (opsional/eksploratif — hapus elemen via `javascript_tool` lalu buka dialog) |
| AC-07-01 s/d AC-07-02 | Optional products rekursif (tambah/hapus berantai) | ✓ | ✓ |
| AC-08-01 s/d AC-08-02 | Sinkronisasi custom/no-variant value saat ganti produk | ✓ | |
| AC-09-01 s/d AC-09-02 | Pembuatan varian dynamic + guard kombinasi tidak valid | ✓ | ✓ |

**Ringkasan:** AI-interaktif tetap default untuk semua 24 AC. AI-Browser dipakai untuk 14 AC yang
observable visual (sama seperti revisi 1) — QUnit/Tour di Step 04 MENGURANGI risiko regresi logic,
tapi TIDAK menggantikan verifikasi visual manusia/AI-Browser untuk modul UI-heavy seperti ini.

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit (Python) | 9 |
| 04 | JS Unit (QUnit) | 5 |
| 04 | Integration | 2 |
| 04 | Tour | 1 skenario (lintas beberapa AC) |
| 04 | Smoke | 1 alur happy path (sekarang via Tour) |
| 04 | API (kondisional) | N/A |
| 07 | AI-interaktif (`07` §3) | 24 (semua) |
| 07 | AI-Browser (`07B`) | 14 (subset — AC-01, AC-05, AC-06, AC-07, AC-09) |
