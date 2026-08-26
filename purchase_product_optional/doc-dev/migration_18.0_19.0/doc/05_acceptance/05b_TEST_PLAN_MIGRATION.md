# Test Plan (Migrasi) — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i purchase_product_optional --test-enable --test-tags /purchase_product_optional --stop-after-init`. Termasuk Owl/JS lewat tour test (`HttpCase.start_tour`, Fase E applicable — modul ini punya Owl widget yang di-patch).

Existing test suite (`source-codebase`, dikonfirmasi ada isi nyata bukan stub — 6 test class Python +
1 Tour): `TestConvertPrice`, `TestOnchangePartnerCurrency`, `TestAttributeValueCompute`,
`TestProductAddModeField`, `TestPurchaseOrderFormViewColumns`, `TestPurchaseProductOptionalController`
(`tests/test_purchase_product_optional.py`) + `TestPurchaseProductOptionalTour`
(`tests/test_purchase_product_optional_tour.py`, menjalankan `purchase_product_optional_configurator_tour`
di `static/tests/tours/`).

**Catatan penting — Tour existing TIDAK cover AC-02-02/AC-05-01 secara eksplisit:** Tour saat ini
menguji jalur "dialog Product Configurator terbuka otomatis + Confirm dengan optional product" (AC-02-01,
AC-02-03, AC-05-01 sebagian, AC-05-02 tidak — tidak ada exclusion di skenario Tour). Jalur fallback
`_openGridConfigurator`/`matrixConfigurator.open` (AC-02-02) **TIDAK** dipicu oleh Tour existing (skenario
Tour selalu match `result.mode === 'configurator'` lewat pemilihan "BACKFILL QA Main Product"). Kandidat
test BARU disarankan di step 6/9 kalau waktu memungkinkan — tapi BUKAN blocker gate manapun (jalur ini
menurut CAND-07 kemungkinan besar tidak pernah terisi `result.mode` untuk konteks Purchase, jadi risiko
produksi rendah meski tetap wajib diperbaiki secara kode).

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | Instalasi modul | — | Implisit (install check G1) | — |
| AC-02-01 | Dialog terbuka otomatis, format many2one benar | — | — | `purchase_product_optional_configurator_tour` (existing) |
| AC-02-02 | Fallback `_openGridConfigurator`→`matrixConfigurator.open` | — | — | **Gap — tidak ada test existing**, verifikasi manual/kode review di step 6, kandidat Tour baru (non-blocking) |
| AC-02-03 | RPC dialog tidak error | — | — | `purchase_product_optional_configurator_tour` (existing, implisit lewat AC-02-01) |
| AC-03-01 | Harga per-vendor | `TestConvertPrice` (existing) | — | — |
| AC-03-02 | Currency param unset (bug dipertahankan) | `TestConvertPrice` (existing) | — | — |
| AC-04-01 | Edit baris terkonfigurasi | — | — | Tidak ada Tour existing untuk re-edit — kandidat baru, non-blocking (behavior tidak berubah dari 18.0, risiko rendah) |
| AC-05-01 | Variant dinamis dibuat saat Confirm | — | Implisit lewat Tour (optional product ditambahkan) | `purchase_product_optional_configurator_tour` (existing) |
| AC-05-02 | Exclusion kombinasi disabled | — | — | Tidak ada Tour existing — kandidat baru, non-blocking (behavior tidak berubah dari 18.0) |
| AC-06-01 | Onchange partner (bug dipertahankan) | `TestOnchangePartnerCurrency` (existing) | — | — |
| AC-06-02 | Sync `id_vendor` | `TestOnchangePartnerCurrency` (existing) | — | — |
| AC-06-03 | Dua dialog (bug dipertahankan) | — | — | Tidak diverifikasi otomatis (CAND-08 dicatat sebagai gotcha desain, bukan regresi yang dites aktif — konsisten 17→18) |
| AC-07-01 | Kolom view | `TestPurchaseOrderFormViewColumns` (existing) | — | — |
| AC-08-01 | Compute attribute values | `TestAttributeValueCompute` (existing) | — | — |
| AC-09-01 | `product_add_mode` tidak terdaftar | `TestProductAddModeField` (existing) | — | — |
| AC-10-01 | Multi-company seller (bug dipertahankan) | — | — | Tidak ada test existing (dikonfirmasi 17→18 lewat baca kode + live test manual, tidak diotomasi) |
| AC-11-01 | Label `id_vendor` | — | — | Tidak ada test existing (dikonfirmasi via warning registry saat install, bukan test case terpisah) |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-02-01, AC-02-03, AC-05-01, AC-05-02 | Alur konfigurator utama | — | Sudah tercakup Tour step 9 — tidak perlu duplikasi step 10 kecuali Tour gagal | — |
| AC-02-02 | Fallback grid configurator | Ya — perlu skenario manual (produk dengan `mode` selain `'configurator'`, jarang terjadi produksi per CAND-07) | Opsional kalau environment browser tersedia | — |
| AC-04-01 | Edit baris terkonfigurasi | Ya | Opsional | — |
| AC-06-03 | Dua dialog bersamaan | Ya — reproduksi terkontrol (pola sama seperti 17→18, AC-10-01/02 lama) | Opsional | — |
| AC-10-01 | Multi-company | Ya — butuh environment 2 company | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Instalasi | AC-01-01 | Konfirmasi modul ter-install bersih di database 19.0 |
| Konfigurator produk (utama) | AC-02-01, AC-02-03, AC-05-01, AC-05-02 | Business user jalankan alur beli produk dengan optional products end-to-end |
| Harga & currency | AC-03-01, AC-03-02 | Business user verifikasi harga per-vendor tampil benar |
| Edit konfigurasi | AC-04-01 | Business user edit baris PO yang sudah dikonfigurasi |
| Bug lama dipertahankan (dikonfirmasi dev) | AC-03-02, AC-06-01, AC-06-03, AC-09-01, AC-10-01, AC-11-01 | Informasional saja — bukan item yang perlu "lulus", cukup dikonfirmasi behavior TIDAK berubah dari 18.0 |
| View | AC-07-01, AC-08-01 | Business user cek kolom & attribute values tampil benar |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour (Owl/JS) | Otomatis/background (semua, termasuk tour) | 16 AC — 12 tercakup test existing, 2 gap non-blocking (AC-02-02, AC-05-02/AC-04-01 sebagian), sisanya cross-check kode/manual |
| 10 | QA | Manual/AI-interaktif | Campuran, prioritas AC-02-02 & AC-06-03 (butuh reproduksi manual) | 5 AC |
| 11 | PM/FA/User | UAT | Manual (selalu) | 6 kelompok fitur |
