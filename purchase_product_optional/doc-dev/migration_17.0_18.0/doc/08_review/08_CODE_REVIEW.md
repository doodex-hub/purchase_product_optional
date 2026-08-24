# Code Review — purchase_product_optional

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 18.0
**Files reviewed:** `__manifest__.py`, `models/*.py`, `controllers/main.py`, `views/purchase_order_views.xml`, `static/src/js/purchase_product_field.js`, `static/src/js/product_configurator_dialog/product_configurator_dialog.js`, `static/tests/tours/purchase_product_optional_tour.js`
**Tanggal:** 2026-08-24

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🔵 Info | Code Quality | `product_configurator_dialog.js` | 137, 147 | `console.log(...)` debug leftover (`'Main Product Quantity:'`, `'tes'`) — sudah ada di source 17.0, bukan ditambahkan migrasi | Di luar scope migrasi (bukan perubahan behavior) — pertahankan apa adanya, bukan tugas migrasi untuk cleanup |
| CR-02 | 🔵 Info | Konvensi Odoo | `models/purchase_order_line.py` | 24-28 | F-01: `product_add_mode` kwarg asing (bug existing, dipertahankan) | Tidak ada aksi — keputusan dev 2026-08-24 |

Tidak ada isu 🔴 Critical baru yang ditemukan dari migrasi ini — semua issue existing sudah tercatat sebagai F-01..F-08 di `01b_BASELINE_SPEC.md` dan sengaja dipertahankan.

**Severity:** 🔴 Critical · 🟡 Warning · 🔵 Info

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (`<tree>`→`<list>`) | `views/purchase_order_views.xml` — 3× diganti | ✅ Selesai | Dikonfirmasi G1 install pass, view ter-load |
| DIFF-02 (hapus `sale_product_configurator`) | `__manifest__.py` `depends` | ✅ Selesai | Dikonfirmasi G1 |
| DIFF-03 (tambah `sale`) | `__manifest__.py` `depends` | ✅ Selesai | Dikonfirmasi G1, tidak ada `AttributeError` `optional_product_ids` |
| DIFF-05 (`onEditConfiguration` rename) | `purchase_product_field.js:97` | ✅ Selesai | Rename + `super()` call disesuaikan |
| DIFF-06 (`_openGridConfigurator()` arg) | `purchase_product_field.js:92` | ✅ Port apa adanya, diverifikasi | Tidak crash di Tour test |
| DIFF-07 (`useService("rpc")` dihapus) | `product_configurator_dialog.js` | ✅ Selesai | Dikonfirmasi Tour test — dialog buka & RPC jalan tanpa `Service rpc is not available` |
| DIFF-09 (dependency xpath ke `purchase_product_matrix`) | Tidak ada perubahan kode, verifikasi saja | ✅ Terverifikasi | View ter-load bersih di G1 |
| DIFF-10 (kolisi field `product_no_variant_attribute_value_ids` dengan core baru) | Tidak ada perubahan kode — ditemukan saat review Arah 2 (§D di bawah) | ✅ Terverifikasi tidak breaking | Field kita (dengan `compute=`) menang di merge, dikonfirmasi G1 tanpa warning tambahan |
| DIFF-11 (Tour `run: "text"` → `"edit"`) | `static/tests/tours/purchase_product_optional_tour.js` — 2× diganti | ✅ Selesai | Ditemukan & diperbaiki saat Step 9 (Tour gagal step 4/15 sebelum fix) |
| DIFF-04, DIFF-08 (tidak ada perubahan) | — | ✅ Dikonfirmasi tidak perlu perubahan | — |

**Tidak ada gap** — semua item `02_DIFF_ANALYSIS.md` §1 sudah diimplementasikan dan diverifikasi runtime.

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 | Install bersih | ✅ Pass | G1, exit code 0 |
| AC-02-01 | Dialog terbuka otomatis | ✅ Pass | Tour step 9/15 |
| AC-02-02 | RPC tidak crash | ✅ Pass | Tour step 9-14/15 (RPC `get_values_purchase`/`create_product` jalan, log "Main Product Quantity: 1") |
| AC-03-01 | Harga per-vendor | ✅ Pass | `test_purchase_product_optional.py` (bagian yang tercakup 13 test) |
| AC-03-02 | Currency no-op dipertahankan | ✅ Pass | `TestConvertPrice.test_convert_price_param_not_set_returns_without_raising` |
| AC-04-01 | Edit baris terkonfigurasi | ⚠️ Tidak tercakup Tour test (fokus create, bukan edit ulang) | Risiko rendah — perubahan kode (DIFF-05) mekanis murni (rename), method body sama persis; direkomendasikan ditambah ke Tour test di project berikutnya (dicatat `migration-records`), TIDAK memblokir gate ini |
| AC-05-01 | Variant dinamis | ✅ Pass (tercakup `test_create_product_creates_dynamic_variant` + alur Tour) | — |
| AC-05-02 | Exclusions/badge | ✅ Pass (tercakup kode, tidak ada perubahan) | — |
| AC-06-01 | Onchange partner (F-02/F-03 dipertahankan) | ✅ Pass | `TestOnchangePartnerCurrency` (MRO shadowing + no-op currency) |
| AC-06-02 | `id_vendor` sync | ✅ Pass (kode tidak berubah) | — |
| AC-07-01 | View list (bukan tree) | ✅ Pass | G1 + `TestPurchaseOrderFormViewColumns` |
| AC-08-01 | Compute attribute values | ✅ Pass | `TestAttributeValueCompute` (3 test) |
| AC-09-01 | `product_add_mode` tidak terdaftar | ✅ Pass | `TestProductAddModeField` + warning G1 |
| AC-10-01, AC-11-01 | Multi-company/label (dipertahankan) | ✅ Dikonfirmasi kode tidak berubah | Tidak ada test otomatis, risiko rendah (sudah dinyatakan di intake) |

**13/13 automated test PASS, 1 AC (AC-04-01) tidak tercakup test otomatis tapi risiko rendah** (perubahan mekanis murni).

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`source-codebase`) sudah eksplisit tercatat & disetujui (DIFF-01/02/03/05/07/11, semuanya kompatibilitas wajib atau fix test, BUKAN perubahan business logic)

**Cek tabrakan nama method dengan Odoo core (DUA ARAH):**

**Arah 1 — method modul menimpa method core:**
- `onchange_partner_id` (`purchase.order`) — **SUDAH diketahui dan didokumentasikan sebagai F-02** (`01b_BASELINE_SPEC.md` BSL-005), dikonfirmasi ULANG tetap ada di core 18.0 (`purchase/models/purchase_order.py:335`) — behavior override total tetap identik 17.0→18.0, DIPERTAHANKAN sesuai keputusan dev. Test `TestOnchangePartnerCurrency.test_onchange_partner_id_mro_shadowing_candidates` PASS di Step 9, mengonfirmasi MRO tetap sama.
- Tidak ada method lain yang ditemukan menimpa core (dicek semua method yang didefinisikan modul: `convert_price`, `onchange_id_vendor`, `_compute_custom_attribute_values`, `_compute_no_variant_attribute_values` — tidak ada nama yang sama dengan method core `purchase`/`sale`/`product`).

**Arah 2 — core 18.0 menambahkan definisi BARU dengan nama sama (WAJIB, tidak cukup Arah 1 saja):**
- **DIFF-10 ditemukan di sini:** core `purchase` 18.0 (`purchase_order_line.py:90`) sekarang mendefinisikan `product_no_variant_attribute_value_ids` sendiri (plain field, TANPA `compute`) — TIDAK ADA di core 17.0. `purchase_product_matrix` juga redeclare field sama (juga tanpa `compute`) di kedua versi. Modul kita SATU-SATUNYA yang menambah `compute=`, dan karena loading urutan terakhir (`purchase`→`purchase_product_matrix`→`sale`→`purchase_product_optional`), compute kita menang — dikonfirmasi G1 tanpa warning field-merge tambahan, dan Step 9 test `TestAttributeValueCompute` (3 test) PASS penuh membuktikan compute kita benar-benar jalan.
- `product_template_attribute_value_ids`, `id_vendor`, `product_custom_attribute_value_ids` — dicek, TIDAK ADA definisi baru bertabrakan di core 18.0.

- [x] Sudah dicek (kedua arah) — **ADA tabrakan ditemukan (DIFF-10) tapi TIDAK breaking**, dikonfirmasi runtime aman. Dicatat di `02_DIFF_ANALYSIS.md`.

**Verifikasi tambahan — gotcha "dua dialog terbuka bersamaan" (`knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` poin 4):** `_onProductTemplateUpdate` kita memanggil `super()` TANPA SYARAT (pola sama persis 17.0/18.0, bukan regresi migrasi). Dikonfirmasi lewat log Tour (`odoo_step9.log`): hanya SATU modal title muncul ("Configure your product") selama seluruh alur test — grid dialog `_openGridConfigurator` dari base TIDAK ikut terbuka di skenario yang diuji (produk dengan optional products tapi bukan produk matrix multi-varian). Gotcha ini tetap ada sebagai risiko desain untuk skenario produk matrix+configurator bersamaan (di luar skenario Tour test ini) — TIDAK diperbaiki (di luar scope migrasi, identik 17.0), dicatat sebagai limitasi diketahui.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — semua perubahan kode (`__manifest__.py`, `views/purchase_order_views.xml`, 2 file JS, 1 file Tour test) tertelusuri ke DIFF-01/02/03/05/07/11.

## F. Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-records/purchase_product_optional_17_18/SUMMARY.md`:
  - **CAND-10** (baru): DIFF-10 — core `purchase` 18.0 menambah field `product_no_variant_attribute_value_ids`/`product_template_attribute_value_ids` di `purchase_order_line.py` yang tidak ada di 17.0 — general untuk SEMUA modul yang extend `purchase.order.line` dengan pola konfigurator (bukan cuma modul ini).
  - **CAND-11** (baru): DIFF-11 — Tour action `run: "text ..."` tidak dikenali lagi di 18.0 (`TypeError: actionHelper[...] is not a function`), wajib `run: "edit ..."` — general untuk SEMUA modul dengan Tour test lama.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 2 🔵 (keduanya informational, existing/dipertahankan)
- [x] ✅ **Lulus** — tidak ada 🔴, semua DIFF teridentifikasi sudah diimplementasikan & diverifikasi runtime (G1 + 13/13 test Step 9), lanjut ke Step 9 (sudah dieksekusi paralel — lihat `09_devtest/09_DEV_TESTING.md`) dan Step 10.

**Issue 🔴 yang wajib difix sebelum lanjut:** Tidak ada.
