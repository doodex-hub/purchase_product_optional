# Test Plan — purchase_product_optional

**Module:** `purchase_product_optional`
**Ref:** `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`
**Dibuat oleh:** BACKFILL (Step 03B, backfill)
**Last Updated:** 2026-07-29

> Peta AC → tipe test, pakai vocab test bawaan Odoo (`TransactionCase`/`HttpCase`/`Tour`/`QUnit`-`Hoot`)
> — `cicd/test_design/odoo-testing-taxonomy.md` tidak diakses sesi ini (opsional, bukan prasyarat).

---

## Catatan arsitektur yang mempengaruhi peta test

Sebagian besar business logic modul ini (BR-01 dialog auto-open, BR-02 harga per-vendor, BR-10
validasi kombinasi) berada di **sisi client (OWL/JS)**, bukan method Python — dipanggil lewat ORM
generik (`search_read`) atau RPC controller yang sudah ada. Ini berarti:
- Logic yang murni Python (currency conversion, compute attribute values, field registration) →
  **Unit** (`TransactionCase`).
- Logic yang lewat endpoint JSON-RPC modul ini sendiri (`controllers/main.py`) → **Integration**
  (`HttpCase`), dijalankan terhadap server yang benar-benar hidup (Mode B docker).
- Logic yang murni di JS/OWL (perhitungan harga per-vendor di `product_configurator_dialog.js`,
  disable tombol Confirm, dialog auto-open) → **tidak ada Python/HTTP equivalent langsung** untuk
  di-unit-test — diverifikasi di Step 07 lewat **AI-Browser** (Claude in Chrome) terhadap instance
  Odoo Mode B yang hidup, BUKAN Tour/QUnit otomatis (di luar scope menulis test JS baru untuk BACKFILL).

---

## Step 04 — Developer Testing (backfill)

**Output:** `04A_DEV_TESTING.md`. Tidak ada API eksternal (semua endpoint controller dipakai internal
oleh JS modul sendiri, `auth='user'`, bukan dikonsumsi sistem luar) → `04B_API_TEST.md` **N/A**.

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-03-01 | convert_price konversi currency berbeda | ✓ | | |
| AC-03-02 | convert_price currency sama (no-op) | ✓ | | |
| AC-03-03 | convert_price param belum di-set → TypeError | ✓ | | |
| AC-03-04 | onchange partner: currency tidak berubah (bug F-03) | ✓ | | |
| AC-03-05 | onchange_partner_id override core (bug F-02) | ✓ | | |
| AC-04-01 | compute custom attribute values bersih saat ganti produk | ✓ | | |
| AC-04-02 | compute no-variant attribute values bersih saat ganti produk | ✓ | | |
| AC-04-03 | compute kosong kalau tidak ada product_id | ✓ | | |
| AC-05-01 | `product_add_mode` tidak terdaftar sebagai field (bug F-01) | ✓ | | |
| AC-06-01 | create_product route buat variant dynamic | | ✓ | |
| AC-07-01 | get_values_purchase route: exclusions dikembalikan | | ✓ | |
| AC-08-01 | view arch: kolom product_template_id/product_id | ✓ | | |

**Ringkasan:** 9 AC → Unit, 2 AC → Integration (HttpCase terhadap controller), API N/A (modul tidak
expose/consume API eksternal — 4 route JSON-nya dipanggil internal oleh JS bundle modul sendiri,
`auth='user'` session-based, bukan kontrak API pihak ketiga).

---

## Step 07 — QA Testing (level AI-interaktif + Smoke human-confirmed, TANPA UAT)

**Output:** skenario detail → `07_QA_TESTING.md` §3 + `07B_QA_AI_BROWSER.md` (Claude in Chrome
tersedia di sesi ini, dipakai terhadap instance Mode B G2).

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser (07B) |
|---|---|---|---|
| AC-01-01/02/03 | Dialog konfigurator auto-open + warning block | ✓ | ✓ |
| AC-02-01/02/03 | Harga per-vendor di dialog | ✓ | ✓ |
| AC-06-02 | Confirm tanpa dynamic variant | ✓ | ✓ |
| AC-07-01/02 | Badge exclusion + tombol Confirm disabled | ✓ | ✓ |
| AC-08-01 | Kolom tree PO line | ✓ | ✓ |
| AC-09-01 | Auto-install (desk-review, tidak dieksekusi ulang instalasi fresh DB) | ✓ | |

**Ringkasan:** BACKFILL pakai AI-interaktif (`07_QA_TESTING.md` §3) sebagai default. AI-Browser
(`07B`) dipakai karena Claude in Chrome tersedia di sesi ini — verifikasi visual nyata terhadap
Mode B G2 (Odoo hidup di `localhost:{{ODOO_PORT}}`), bukan pengganti §3.

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 9 |
| 04 | Integration | 2 |
| 04 | Smoke | 3 happy path (dialog buka, currency convert, compute attribute) |
| 04 | API (kondisional) | N/A — tidak ada kontrak API eksternal |
| 07 | AI-interaktif (`07` §3) | 6 (semua area) |
| 07 | AI-Browser (`07B`) | 5 (subset — semua kecuali AC-09 auto-install) |
