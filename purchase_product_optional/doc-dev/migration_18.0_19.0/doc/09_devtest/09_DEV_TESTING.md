# Dev Testing — purchase_product_optional

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-26

---

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` meng-import kedua file test (`test_purchase_product_optional`,
`test_purchase_product_optional_tour`) — dikonfirmasi, tidak ada file test yang tidak ke-load.

**Audit isi (AST, dijalankan di dalam container Odoo 19.0, 2026-08-26):** SEMUA 13 method test
berstatus **ok** (bukan stub) — tidak ada satupun yang cuma docstring tanpa assertion.

**PERINGATAN MSYS diterapkan:** run pertama (`--test-tags /purchase_product_optional` tanpa
`MSYS_NO_PATHCONV=1`) kena persis isu yang didokumentasikan `USAGE_GUIDE.md`/template ini — tag
di-mangle Git Bash jadi `C:/Program Files/Git/purchase_product_optional`, hasil "0 failed, 0 error(s)
of 0 tests" (false pass). Terdeteksi dari log `odoo.tests.tag_selector: Invalid tag ...` dan jumlah
"0 tests" yang jelas tidak masuk akal untuk 13 method yang ada. **Fix:** prefix `MSYS_NO_PATHCONV=1`
— run kedua berhasil genuinely mengeksekusi 13 test.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Instalasi modul | — (divalidasi G1, bukan test suite) | ✅ Lengkap | G1 pass terpisah |
| AC-02-01, AC-02-03 | Dialog terbuka otomatis, RPC | `test_purchase_product_optional_tour.py` | ✅ Lengkap | Tour end-to-end |
| AC-02-02 | Fallback grid configurator | — | ❌ Tidak ada (gap, sudah dicatat non-blocking di step 5) | Tidak diperbaiki di step ini, risiko rendah (CAND-07) |
| AC-03-01, AC-03-02 | Harga per-vendor & currency | `TestConvertPrice` (3 method) | ✅ Lengkap | |
| AC-04-01 | Edit baris terkonfigurasi | — | ❌ Tidak ada (gap, sudah dicatat non-blocking di step 5) | |
| AC-05-01 | Variant dinamis & Confirm | `TestPurchaseProductOptionalController.test_create_product_creates_dynamic_variant` + Tour | ✅ Lengkap | |
| AC-05-02 | Exclusion kombinasi | — | ❌ Tidak ada (gap, sudah dicatat non-blocking di step 5) | |
| AC-06-01, AC-06-02 | Onchange partner & sync id_vendor | `TestOnchangePartnerCurrency` (2 method) | ✅ Lengkap | |
| AC-06-03 | Dua dialog bersamaan | — | ⚠️ Tidak diotomasi (konsisten 17→18, gotcha desain dicatat bukan diuji aktif) | |
| AC-07-01 | Kolom view | `TestPurchaseOrderFormViewColumns` | ✅ Lengkap | |
| AC-08-01 | Compute attribute values | `TestAttributeValueCompute` (3 method) | ✅ Lengkap | |
| AC-09-01 | `product_add_mode` tidak terdaftar | `TestProductAddModeField` | ✅ Lengkap | |
| AC-10-01 | Multi-company | — | ⚠️ Tidak diotomasi (konsisten 17→18) | |
| AC-11-01 | Label `id_vendor` | — | ✅ Divalidasi via warning registry G1 (bukan test case terpisah) | |

**Verdict audit:** AC prioritas tinggi (AC-02-01, DIFF-01/02) **Lengkap** dan sudah dieksekusi via Tour
— lanjut ke eksekusi. 3 gap (AC-02-02, AC-04-01, AC-05-02) sudah dikonfirmasi non-blocking di step 5
(risiko rendah, behavior tidak berubah dari 18.0), tidak menghalangi gate.

## Baseline

- Characterization test source module (18.0): 13 test yang sama (warisan penuh dari `source-codebase`,
  tidak ada test baru ditulis migrasi ini) — sudah pernah pass di 18.0 (dikonfirmasi migrasi 17→18
  sebelumnya, `SUMMARY.md` 17_18).
- Applicability Check Fase E (Owl/JS) step 6: **Ya, applicable** — Tour test WAJIB ada dan pass. Tour
  `purchase_product_optional_configurator_tour` (15 langkah) dijalankan.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 19.0)

**Command:** `MSYS_NO_PATHCONV=1 docker compose run --rm odoo odoo -d purchase_product_optional_19_test2 -i purchase_product_optional --test-enable --test-tags /purchase_product_optional --stop-after-init`
**Hasil:** `0 failed, 0 error(s) of 13 tests when loading database 'purchase_product_optional_19_test2'`

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | — | — | ✅ Pass | G1, 60 modul termuat bersih |
| AC-02-01 | — | — | ✅ Pass | ✅ Pass | Tour step 9 "BR-01: product configurator dialog opened automatically" — MEMBUKTIKAN DIFF-01 (format many2one objek) benar, dialog terbuka tanpa error JS |
| AC-02-03 | — | — | ✅ Pass | ✅ Pass | Tour step 9-11, tidak ada error RPC di browser log |
| AC-03-01 | `test_convert_price_different_currency_converts`, `test_convert_price_same_currency_no_conversion` | — | — | ✅ Pass | |
| AC-03-02 | `test_convert_price_param_not_set_returns_without_raising` | — | — | ✅ Pass | Bug dipertahankan, tidak raise |
| AC-05-01 | `test_create_product_creates_dynamic_variant` | — | ✅ Pass (Tour step 11-13, optional product ditambahkan) | ✅ Pass | Tour step 12 "Confirm the configuration" MEMBUKTIKAN DIFF-01 write `product_id`/`custom_product_template_attribute_value_id` format objek benar |
| AC-06-01 | `test_currency_not_synced_to_partner_purchase_currency` | — | — | ✅ Pass | Bug dipertahankan |
| AC-06-02 | (implisit dari `TestOnchangePartnerCurrency`) | — | — | ✅ Pass | |
| AC-07-01 | `test_product_template_and_variant_columns` | — | — | ✅ Pass | |
| AC-08-01 | `test_custom_attribute_values_pruned_on_product_change`, `test_no_variant_attribute_values_pruned_on_product_change`, `test_attribute_values_cleared_without_product` | — | — | ✅ Pass | |
| AC-09-01 | `test_product_add_mode_not_registered_as_field` | — | — | ✅ Pass | Warning registry tetap muncul, tidak fatal — identik 18.0 |
| AC-11-01 | — | — | — | ✅ Pass (via G1 warning log) | Warning label collision muncul persis seperti diprediksi baseline |
| DIFF-02 (`useMatrixConfigurator` hook) | — | — | Tidak tereksekusi Tour ini (jalur `result.mode !== 'configurator'` tidak terpicu skenario Tour existing, konsisten catatan step 5) | ⚠️ Tidak tervalidasi runtime | Kode sudah benar (mirror pola native persis), tapi jalur fallback ini butuh skenario Tour tambahan untuk validasi runtime — dicatat sebagai residual risk rendah (CAND-07: `result.mode` untuk konteks Purchase kemungkinan besar tidak pernah terisi di produksi) |

**Ringkasan console browser (Tour):** 0 error/exception JS (`grep` log Tour, tidak ada match
`error`/`TypeError`/`undefined is not`/`Cannot read`). `tour succeeded` (log eksplisit).

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-tool/migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md`:
  **CAND-04** (baru, ditulis sesi ini) — normalisasi format many2one saat sumber data campuran
  (`record.data` vs `orm.read()`) di modul yang extend Odoo 19.0 relational_model field widget, temuan
  konkret dari implementasi (bukan cuma dari diff native).

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration/Tour pass** (13/13 test, 0 failed, 0 error; Tour
  `tour succeeded`, 0 JS error). 3 gap non-blocking (AC-02-02, AC-04-01, AC-05-02) dan 1 residual risk
  rendah (DIFF-02 fallback belum tervalidasi runtime, kode sudah benar secara analisis) dicatat
  transparan, tidak menghalangi gate — lanjut ke Step 10 (QA Testing).
