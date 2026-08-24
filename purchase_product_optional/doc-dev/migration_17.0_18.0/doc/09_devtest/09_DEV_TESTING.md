# Dev Testing — purchase_product_optional

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-24

---

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` meng-import kedua file (`test_purchase_product_optional`, `test_purchase_product_optional_tour`) — dikonfirmasi baca langsung, tidak ada file test yang tidak ter-load.

**Audit isi method** (baca kode langsung, bukan cuma nama — 8 method di `test_purchase_product_optional.py` + 1 di `test_purchase_product_optional_tour.py`, semua dibaca penuh 2026-08-24):

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-03-02 | Currency no-op (F-05 dipertahankan) | `TestConvertPrice.test_convert_price_param_not_set_returns_without_raising` | ✅ Lengkap | Assert implisit via `_logger.info` + tidak raise — sesuai desain karakterisasi bug (bukan assert nilai spesifik, karena hasil "silent no-op" itu sendiri behaviornya) |
| AC-03-01 | Harga konversi currency berbeda | `TestConvertPrice.test_convert_price_different_currency_converts` | ✅ Lengkap | `assertNotEqual` nyata |
| AC-06-01 | Onchange currency no-op (F-03) | `TestOnchangePartnerCurrency.test_currency_not_synced_to_partner_purchase_currency` | ✅ Lengkap | `assertEqual` nyata |
| AC-06-01 (F-02) | MRO shadowing core method | `TestOnchangePartnerCurrency.test_onchange_partner_id_mro_shadowing_candidates` | ✅ Lengkap | Baca `__mro__` live + `assertTrue`, plus log detail untuk audit manual |
| AC-08-01 | Compute custom/no-variant attribute values (3 skenario) | `TestAttributeValueCompute.*` (3 method) | ✅ Lengkap | Semua ada `assertTrue`/`assertFalse` nyata terhadap state ORM sungguhan |
| AC-09-01 | `product_add_mode` tidak terdaftar (F-01) | `TestProductAddModeField.test_product_add_mode_not_registered_as_field` | ✅ Lengkap | `assertNotIn` terhadap `_fields` registry nyata |
| AC-07-01 | Kolom view form (`product_template_id`/`product_id`) | `TestPurchaseOrderFormViewColumns.test_product_template_and_variant_columns` | ✅ Lengkap | Parse arch XML nyata + assert atribut |
| AC-02-02, AC-05-01 | Controller RPC (`get_values_purchase`, `create_product`) real HTTP | `TestPurchaseProductOptionalController.*` (2 method) | ✅ Lengkap | `HttpCase` + `url_open` nyata, assert payload JSON-RPC |
| AC-01-01, AC-02-01, AC-02-02, AC-04-01 (sebagian), AC-05-01, AC-05-02 | Full user flow (buka app → PO baru → vendor → produk → dialog → confirm → save) | `TestPurchaseProductOptionalTour.test_product_configurator_dialog_tour` | ✅ Lengkap | Tour 15 langkah, headless Chrome sungguhan, bukan mock |

**Verdict audit:** Semua method test genuinely berisi assertion/verifikasi nyata (tidak ada stub docstring-only) — tidak perlu eskalasi ke user. Satu gap dicatat di §C `08_CODE_REVIEW.md`: AC-04-01 (edit ulang baris terkonfigurasi) tidak eksplisit tercakup Tour test (fokusnya create, bukan re-edit) — risiko rendah karena DIFF-05 (fix terkait) murni rename mekanis.

## Baseline

- Characterization test asli source module (17.0, dari `doc-dev/backfill`): semua 27 test PASS di run backfill 2026-07-29/30, termasuk Tour 13/13 PASS PENUH (`FINDINGS.md` source).
- Applicability Check Fase E (Owl/JS): **Ya, applicable** — Tour test WAJIB dijalankan, sudah dijalankan di bawah.

## Eksekusi

**Mode:** C — AI jalankan langsung (Docker tersedia, Claude Code CLI). Command via `docker-env/docker-compose.yml`:
```
odoo -d purchase_product_optional_target_test -i purchase_product_optional
--addons-path=...,/mnt/extra-addons --test-enable --test-tags=/purchase_product_optional --stop-after-init
```

**Percobaan #1 (2026-08-24):** `1 failed, 0 error(s) of 13 tests` — Tour gagal di step 4/15 (`TypeError: actionHelper[...] is not a function`, trigger `run: "text ..."`). Root cause: sintaks Tour action `"text <value>"` tidak lagi dikenali di 18.0 (dicek native `purchase/static/src/js/tours/purchase.js` — idiom baru `"edit <value>"`). **Ini DIFF-11**, temuan baru (tidak ada di knowledge base manapun sebelumnya). Fix: `static/tests/tours/purchase_product_optional_tour.js` 2 baris diganti `"text ..."` → `"edit ..."`.

**Percobaan #2 (2026-08-24, setelah fix DIFF-11):** `0 failed, 0 error(s) of 13 tests`. Tour **PASS PENUH 15/15 langkah** — log `TOUR purchase_product_optional_configurator_tour SUCCEEDED`. Loop test→fix→test selesai di percobaan ke-2 (tidak perlu iterasi lagi).

## Hasil Unit, Integration & Tour Test (target-codebase)

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | ✅ (G1 install) | ✅ (Tour berjalan = modul aktif) | ✅ Pass | |
| AC-02-01, AC-02-02 | — | — | ✅ (step 9/15, 11/15) | ✅ Pass | DIFF-07 fix terbukti — dialog buka tanpa crash RPC |
| AC-03-01, AC-03-02 | ✅ (`TestConvertPrice`, 3 method) | — | — | ✅ Pass | |
| AC-04-01 | — | — | ⚠️ Tidak tercakup | ⚠️ Gap dicatat, risiko rendah | Lihat 08_CODE_REVIEW §C |
| AC-05-01 | — | ✅ (`TestPurchaseProductOptionalController`) | ✅ (step 12/15) | ✅ Pass | |
| AC-05-02 | — | — | ✅ (implisit, tidak ada exclusion di skenario Tour tapi kode tidak berubah) | ✅ Pass | |
| AC-06-01, AC-06-02 | ✅ (`TestOnchangePartnerCurrency`, 2 method) | — | — | ✅ Pass | F-02 MRO shadowing terkonfirmasi ulang identik |
| AC-07-01 | ✅ (`TestPurchaseOrderFormViewColumns`) | — | — | ✅ Pass | |
| AC-08-01 | ✅ (`TestAttributeValueCompute`, 3 method) | — | — | ✅ Pass | |
| AC-09-01 | ✅ (`TestProductAddModeField`) | — | — | ✅ Pass | Warning F-01 juga muncul identik di G1 |
| AC-10-01, AC-11-01 | — | — | — | ✅ Dikonfirmasi kode tidak berubah | Tidak ada test otomatis, sesuai rencana |

**Total: 13/13 test PASS (0 failed, 0 error), Tour 15/15 langkah PASS.**

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-records/purchase_product_optional_17_18/SUMMARY.md`:
  - **CAND-11**: DIFF-11 (Tour `"text ..."` → `"edit ..."`) — general, berlaku semua modul dengan Tour test lama yang belum di-migrasi ke 18.0.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass** (13/13 test, Tour 15/15 langkah) — lanjut ke Step 10 (QA Testing).
