# Code Review — purchase_product_optional

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 20.0
**Diff reviewed:** `git diff migration/19.0 b8ca459 -- purchase_product_optional/` (base `4736c36`, head `b8ca459`)
**Files reviewed:** `__manifest__.py`, `models/purchase_order.py`, `models/product_template.py`, `controllers/main.py`, `views/purchase_order_views.xml`, `static/src/js/purchase_product_field.js`, `static/src/js/{product_configurator_dialog,product_list,product,product_template_attribute_line,badge_extra_price}/*.{js,xml}`, `static/tests/tours/purchase_product_optional_tour.js`, `tests/test_purchase_product_optional.py`, `docker-env/*`
**Tanggal:** 2026-09-24

---

## A. Issues

**Status skill `odoo-review`:**
- [x] Terinstall (`.claude/skills/odoo-review`, `odoo-guidelines`, `odoo-web-guidelines`, `odoo-security`) & dijalankan (rules pass + merits pass).

**Guidelines read:** Manifest; Imports; Naming and model layout; Computes, onchange and constraints;
Controllers; Views, actions and data records; Anchor view inheritance on names, never on position;
Tests; Changes in a stable version; (web) Avoid patching JavaScript code; (security) Access control,
Default to private methods, Don't over-sudo, Routes: auth, POST, CSRF.

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🔵 Info (pre-existing) | Security / Don't over-sudo | `models/purchase_order.py` | 13-22 | `onchange_partner_id` menulis `ir.config_parameter` global dengan `sudo()` dari onchange (state global lintas user, F-04). Diff hanya mengganti `set_param`→`set_int` | Dipertahankan (MF-02) |
| CR-02 | 🔵 Info (pre-existing) | Security / Default to private methods | `models/product_template.py` | 11 | `convert_price` publik → bisa dipanggil RPC oleh user manapun; membaca param via `sudo()` (hanya baca id currency) | Dipertahankan — dipanggil JS modul sendiri |
| CR-03 | 🔵 Info (pre-existing) | Views / "Don't re-add fields the parent view already renders" | `views/purchase_order_views.xml` | 16-26 | `product_template_attribute_value_ids`, `product_no_variant_attribute_value_ids`, `is_configurable_product` juga ditambahkan native `purchase_product_matrix` (BSL-023). Tidak error di 20.0 (G1/G2 pass) | Dipertahankan (parity) |
| CR-04 | 🔵 Info (judgement) | Code quality | `controllers/main.py` | 187-199, 215 | Argumen `parent_combination` di route/helper kini tidak dipakai | Sengaja dipertahankan agar payload JS & signature route tidak berubah (Stable: jangan ubah signature) |
| CR-05 | 🔵 Info (judgement, parity) | Web / props schema | `product_configurator_dialog.js` | 30-35 | `customAttributeValues[].value: t.string()` — kalau custom value baris tersimpan kosong (`false`), validasi Owl **dev mode** (debug/test) menolak props dialog edit. Setara 1:1 dengan `static props` 19.0 (`value: String`, Owl 2 juga memvalidasi hanya di dev mode) | Dipertahankan (bukan regresi) |
| CR-06 | 🔵 Info (pre-existing) | Code quality | `product_configurator_dialog.js`, `purchase_product_field.js` | — | `console.log` debug, import `useRecordObserver`/`WarningDialog` bertahan | Dipertahankan (refactor non-wajib, `03` §4) |

**Severity:** 🔴 0 · 🟡 0 · 🔵 6

**Merits pass (tidak menghasilkan temuan):**
- `set_int(key, False)` saat PO tanpa currency → record param bernilai kosong (19.0: record dihapus);
  pembacaan berikutnya `get_int` → `0` = `int(False)` 19.0. Cache `_get` (ormcache `stable`) di-clear oleh
  create/write model ini — dibuktikan `test_onchange_stores_currency_param` (unlink → onchange → get).
- `useProps(schema)` hanya mengekspos key schema: semua `this.props.*` yang dibaca 5 komponen (dan objek
  props yang diteruskan ke `env.isPossibleCombination(this.props)` → membaca `attribute_lines`) ada di
  schema.
- Reaktivitas `proxy`: jalur `_addProduct` (splice/push antar list) dieksekusi Tour dan hasilnya
  (baris optional) terbukti muncul.
- Xpath `//list//field[...]` anchored on name; match pertama = list `order_line` (list pertama di form),
  dibuktikan `test_product_template_and_variant_columns`.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item | Implementasi | Status | Catatan |
|---|---|---|---|
| Manifest `20.0.1.0.0` | `__manifest__.py:5` | ✅ Match | |
| DIFF-17 view | `views/purchase_order_views.xml` | ✅ Match | |
| DIFF-10 config param | `purchase_order.py` 3×, `product_template.py` 1× | ✅ Match | |
| DIFF-11 exclusions | `controllers/main.py` 3 titik + `parent_exclusions={}` | ✅ Match | |
| DIFF-06 `orm_plugin` | `purchase_product_field.js:4` | ✅ Match | |
| DIFF-01/02/04/05 Owl 3 JS | 5 komponen | ✅ Match | |
| DIFF-03 template `this.` | 5 template, audit 0 sisa | ✅ Match | |
| DIFF-09 tour | `test` dihapus, selector `button` | ✅ Match | |
| Tests `set_int` | `TestConvertPrice` | ✅ Match | |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01 | Install bersih | ✅ | `-i` → view inherit mencari `//list//field[product_template_id]` di arch gabungan (native matrix menaruhnya di dalam `<column>`) → ketemu; field tambahan setelah `column` | G1 #2 PASS, warning baseline saja |
| AC-02-01 | Dialog buka otomatis | ✅ | Pilih template → native `useEffect` → `_onProductTemplateUpdate` patch → `get_single_product_variant` → `has_optional_products` → `_openProductConfigurator` → `dialog.add` → constructor (tanpa `defaultProps`) → `onWillStart` RPC `get_values_purchase` (tanpa `parent_combination`) → render `this.title` = "Configure your product" | Tour step 9-10 |
| AC-02-02 | Produk sederhana tanpa dialog | ✅ | `result.product_id` & `!has_optional_products` → `record.update(product_id)` (kode tidak diubah) | Unit test input |
| AC-02-03 | Route tanpa error | ✅ | 4 route → `_get_product_information_purchase` → `_get_attribute_exclusions(combination_ids)` | 5 HttpCase |
| AC-03-01 | Harga vendor | ✅ | `get_product_update_price`/`get_optional_product_prices` tidak diubah; `convert_price` → `get_int` | Angka tidak diasersi otomatis — Step 10 |
| AC-03-02 | convert_price param | ✅ | `get_int('currency_id')` → int / 0 | 3 unit test |
| AC-04-01 | Edit ulang | ⚠️ Desk review saja | `onEditConfiguration` tidak diubah; dialog `edit=true` lewat schema `t.boolean().optional(false)`; normalisasi `record.data`/`orm.read` tetap | MF-04 — Step 10 |
| AC-05-01 | Variant dinamis | ✅ | `onConfirm` → `/create_product` (tidak diubah) | HttpCase |
| AC-05-02 | Eksklusi dalam template | ✅ (backend) | `exclusions` dari `excluded_value_ids` → JS `_checkExclusions` (tidak diubah) | HttpCase; visual Step 10 |
| AC-05-03 | Confirm + baris optional | ✅ | `applyProductPurchase` + `addNewRecord` (tidak diubah, `x2ManyCommands` dari `orm_plugin`) | Tour step 12-15 |
| AC-06-01/02 | Onchange quirk | ✅ | Method modul tetap tanpa `super()`; param via `set_int` | 3 unit test |
| AC-07-01 | View | ✅ | xpath attributes | unit test arch |
| AC-08-01 | Compute | ✅ | tidak diubah | 3 unit test |
| AC-09-01/02 | Quirk field | ✅ | tidak diubah | 2 unit test |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja. Satu deviasi terpaksa & tercatat: parent
      exclusions (MF-03, platform 20.0). Posisi field tersembunyi di arch (setelah column) tidak
      mengubah perilaku.

**Empat arah:**
1. Arah 1: `onchange_partner_id` core 20.0 masih ada → override total tetap (BSL-005, disengaja).
2. Arah 2: tidak ada definisi baru native 20.0 bernama sama (`02` §0d).
3. Arah 3: modul tidak me-replace item registry UI apa pun (hanya `patch` prototype field widget —
   method yang di-`super` masih ada di base class 20.0 dengan isi sama, DIFF-07).
4. Arah 4: modul tidak menambah entry registry UI (selain tour); `purchase`/`purchase_product_matrix`
   20.0 tidak menambah fitur configurator/optional product native (grep kosong di 19 & 20).

- [x] Sudah dicek (keempat arah) — tidak ada tabrakan/penyimpangan/tumpang-tindih.

## E. Perubahan Tak Tertelusuri

- [x] Tidak ada. `docker-env/*` = infra test (disebut `04` §cakupan).

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di luar CAND-01..06 (`migration-records/purchase_product_optional_19.0_20.0/SUMMARY.md`).

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 6 🔵
- [x] ✅ Lulus — lanjut ke Step 9.
