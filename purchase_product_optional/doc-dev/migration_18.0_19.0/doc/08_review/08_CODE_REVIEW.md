# Code Review — purchase_product_optional

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0
**Files reviewed:** `__manifest__.py`, `controllers/main.py`, `static/src/js/purchase_product_field.js`
**Tanggal:** 2026-08-26

> **Catatan urutan:** review ini dikerjakan SETELAH G1/G2/Step 9 test suite (yang sudah PASS) —
> penyimpangan urutan dari alur normal (step 8 sebelum 9). Tidak mengubah validitas hasil (kode yang
> direview di sini persis kode yang sudah diuji), tapi dicatat transparan sesuai prinsip audit.

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| — | — | — | — | — | Tidak ada issue baru ditemukan pada 3 file yang diubah migrasi ini. Perubahan murni mekanis (format many2one, method call, version bump, route type) — tidak ada logic baru, tidak ada `sudo()`/ORM/decorator baru, tidak ada perubahan performa (tidak ada loop/query baru ditambah). | — |

**Catatan:** kualitas kode PRA-EXISTING modul (mis. BSL-005 override core, BSL-009 kwarg tertelan, `console.log` debug yang tertinggal di `_openProductConfigurator`) SENGAJA TIDAK ditandai sebagai issue di sini — itu bug/quirk lama yang dipertahankan sesuai keputusan dev (`01a_MIGRATION_INTAKE.md` "Ringkasan untuk Review"), bukan sesuatu yang diperkenalkan migrasi ini. Menandainya di sini akan salah mengarahkan seolah-olah ini regresi baru.

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (format many2one tuple→objek) | `purchase_product_field.js` — 8 titik akses/tulis diganti `.id`/`{id,display_name}` | ✅ Sesuai | Diverifikasi via Tour test pass |
| DIFF-02 (`_openGridConfigurator`→hook) | Import `useMatrixConfigurator`, assign di `setup()`, panggil `this.matrixConfigurator.open()` | ✅ Sesuai | Kode mirror pola native 19.0 persis — belum tervalidasi runtime (jalur fallback tidak tereksekusi Tour existing, dicatat sebagai residual risk rendah di `09_DEV_TESTING.md`) |
| DIFF-06 (`type='json'`→`'jsonrpc'`, opsional) | 4 route di `controllers/main.py` diganti | ✅ Sesuai (opsional, dikerjakan) | Non-breaking, dikonfirmasi G1 install bersih |
| Manifest version bump | `19.0.1.0.0` | ✅ Sesuai | |
| Fase B/C/D2/F (N/A) | Tidak ada perubahan kode | ✅ Sesuai | Konsisten Applicability Check step 6 |
| Temuan tambahan: normalisasi `customAttributeValues` (di luar spec awal, DIFF-01 turunan) | Ternormalisasi di titik ekstraksi, `_openProductConfigurator` | ✅ Sesuai, dicatat CAND-04 | Ditemukan saat implementasi (bukan step 2), diverifikasi Tour pass |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-02-01 | Dialog terbuka otomatis, format many2one benar | ✅ Tercover | Tour pass |
| AC-02-02 | Fallback grid configurator tidak `TypeError` | ⚠️ Tercover secara kode (mirror native), BELUM tervalidasi runtime | Residual risk rendah (CAND-07), sudah dicatat step 5/9 sebagai gap non-blocking |
| AC-03-01, AC-03-02 | Harga & currency | ✅ Tercover | Unit test pass |
| AC-05-01 | Variant dinamis & Confirm, format objek | ✅ Tercover | Tour + unit test pass |
| AC-06-01, AC-06-02, AC-06-03 | Bug dipertahankan | ✅ Tercover | Tidak disentuh kode migrasi, behavior identik (dikonfirmasi DIFF-05 step 2) |
| AC-07-01, AC-08-01, AC-09-01, AC-11-01 | View, compute, product_add_mode, label | ✅ Tercover | Tidak disentuh, unit test pass |
| AC-04-01, AC-05-02 | Edit baris, exclusion | ⚠️ Tidak disentuh kode (tidak perlu, behavior tidak berubah dari 18.0), TIDAK ada test otomatis | Gap non-blocking, sudah dicatat step 5 |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] **Tidak ada perubahan behavior yang tidak disengaja** — semua perubahan kode (DIFF-01, DIFF-02,
  DIFF-06, manifest) murni kompatibilitas API 19.0, tidak ada logic/fitur/business rule yang berubah.
  Baris `product_id != result.product_id.id` (perbandingan yang secara faktual selalu `true` lewat
  type coercion) SENGAJA TIDAK "diperbaiki" — preservasi eksplisit, dicatat `06c_IMPLEMENTATION_LOG.md`.

**Cek tabrakan nama method dengan Odoo core (DUA ARAH, dijalankan sesi ini 2026-08-26):**

**Arah 1 (method sama persis dengan core):**
- `onchange_partner_id` (`purchase.order`) — DIKONFIRMASI menimpa total core (DIFF-05, step 2). Core
  19.0 masih punya method sama nama, isi berbeda (`fiscal_position_id`/`payment_term_id`/dst). **Sudah
  ada sejak 17.0/18.0, dipertahankan sesuai keputusan dev** (BSL-005) — bukan temuan baru migrasi ini,
  tidak perlu fix.

**Arah 2 (field/method BARU yang ditambahkan core di target, nama sama dengan yang modul definisikan):**
- `id_vendor` — 0 match di `native-target` `purchase/**` — aman, tidak ada field core dengan nama sama.
- `onchange_id_vendor` — 0 match — aman.
- `product_custom_attribute_value_ids` — match HANYA di `sale/models/sale_order_line.py`/`sale_order.py`
  (model `sale.order.line`, BUKAN `purchase.order.line`) — model berbeda, TIDAK ada collision nyata.
  Sama persis kondisinya di 18.0 (source) — tidak ada perubahan.
- `product_no_variant_attribute_value_ids` — **match di `purchase/models/purchase_order_line.py`**
  (model SAMA, `purchase.order.line`!) — `Many2many('product.template.attribute.value', string='Product
  attribute values that do not create variants', ondelete='restrict')`. **Diverifikasi: definisi
  IDENTIK byte-per-byte di `native-source` (18.0) dan `native-target` (19.0)** — field ini SUDAH ada
  di core `purchase` sejak 18.0 (dicatat CAND-10, `migration-records/purchase_product_optional_17_18/SUMMARY.md`,
  belum dikurasi ke `knowledge/`), **BUKAN perubahan baru 18→19**. Modul ini sudah berjalan normal
  dengan kondisi ini sejak migrasi 17→18 (G1/G2/test pass di 18.0) — tidak ada regresi tambahan di
  19.0 karena definisi core tidak berubah. Tidak perlu fix.
- `product_add_mode` — match di `purchase_product_matrix/models/purchase.py` HANYA sebagai **komentar
  kode** (`# ... so no need to check product_add_mode`), BUKAN definisi field/method — dikonfirmasi
  baca langsung, identik di 18.0 dan 19.0. Bukan collision.
- `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values` — 0 match di model
  `purchase.order.line` manapun di `native-target` (match yang muncul di `sale/models/sale_order_line.py`
  beda model) — aman.
- `convert_price` (`product.template`) — 0 match di `native-target` — aman.
- `purchase_order_line_id` (`product.attribute.custom.value`) — 0 match di `native-target` — aman.

- [x] Sudah dicek (kedua arah) — **tidak ada tabrakan BARU** dengan core/Enterprise 19.0. Satu overlap
  nyata (`product_no_variant_attribute_value_ids`) sudah ada sejak 18.0, tidak berubah, tidak
  menyebabkan regresi (dikonfirmasi G1/test pass).

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — satu-satunya perubahan di luar
  `03_MIGRATION_SPEC.md` awal (normalisasi `customAttributeValues`) sudah ditelusuri balik ke DIFF-01
  sebagai konsekuensi langsungnya dan dicatat CAND-04 (`06c_IMPLEMENTATION_LOG.md`, `SUMMARY.md`).

## F. Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md`: CAND-01
  (format many2one), CAND-02 (`useMatrixConfigurator` hook), CAND-03 (registry field composition),
  CAND-04 (normalisasi sumber data campuran). Semua sudah dicatat sebelum step ini (step 2 & 9) —
  tidak ada temuan BARU dari code review itu sendiri (dua cek Arah 2 di atas mengonfirmasi ulang
  temuan CAND-10 lama, bukan temuan baru).

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 0 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, semua gap (AC-02-02, AC-04-01, AC-05-02) sudah dikonfirmasi
  non-blocking di step 5/9, tidak ada tabrakan nama core baru. Lanjut ke Step 10 (QA Testing).

**Issue 🔴 yang wajib difix sebelum lanjut:** Tidak ada.
