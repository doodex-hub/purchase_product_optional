# Migration Spec (Teknis) — purchase_product_optional

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-24

> Memandu IMPLEMENTASI (Step 6). Bukan dasar testing — dasar testing = `01b_BASELINE_SPEC.md`.

---

## 1. Ringkasan Strategi

Port kompatibilitas dengan perubahan **minimal**, meniru pola yang dipakai native 20.0 pada kode
kembarannya (`sale` product configurator, `purchase_product_matrix`). Tidak ada perubahan logika
bisnis. Empat area wajib disentuh: (1) view xpath (`<column>`), (2) Python `ir.config_parameter` API
baru, (3) controller — hapus `parent_combination` dari 2 panggilan native tanpa mengubah kontrak JSON,
(4) JS/template Owl 3 (`useProps`/`proxy`/`this.` di template, import `orm_plugin`). Plus manifest bump
dan penyesuaian test (API param, tour registry).

## 2. Strategi per File/Simbol

| File/simbol | Ref DIFF | Strategi | Risiko | Ref BSL |
|---|---|---|---|---|
| `__manifest__.py` `version` | — | `19.0.1.0.0` → `20.0.1.0.0` (A1). Key lain tidak disentuh (MF-01) | Rendah | BSL-012 |
| `views/purchase_order_views.xml` | DIFF-17 | `//list/field[@name='product_template_id']` → `//list//field[@name='product_template_id']` untuk `position="attributes"` (tetap set `column_invisible=0`, no-op visual, dipertahankan untuk parity/test). Field tersembunyi tambahan (4 field + subview) dipindah ke `<xpath expr="//list/column[@name='product_and_description']" position="after">` (pola native matrix 20.0, di luar column supaya tetap tidak terlihat). `//list/field[@name='product_id']` → `//list//field[@name='product_id']` (tetap `optional=hide`, `string=Product Variant`). `currency_id`/`form` xpath tidak diubah | Sedang — posisi field tersembunyi berubah dari "setelah product_template_id" ke "setelah column" (tidak terlihat user, tidak mempengaruhi data/onchange) | BSL-011, BSL-023 |
| `models/purchase_order.py` `onchange_partner_id` | DIFF-10 | Ganti 3× `set_param('currency_id', self.currency_id.id)` → `set_int('currency_id', self.currency_id.id)`. Semantik: id → disimpan; `False` → "undefined" (19: record dihapus) — pembacaan berikutnya identik (`0`). Tidak menambah `super()` (BSL-005 dipertahankan) | Rendah | BSL-005, 006, 019 |
| `models/product_template.py` `convert_price` | DIFF-10 | `int(get_param('currency_id'))` → `get_int('currency_id')` (kosong → `0`, sama dengan `int(False)`) | Rendah | BSL-013, 018 |
| `controllers/main.py` | DIFF-11 | `_get_first_possible_combination(parent_combination=...)` → `_get_first_possible_combination()` (2×); `_get_attribute_exclusions(parent_combination=..., combination_ids=...)` → `_get_attribute_exclusions(combination_ids=...)`; key respons `parent_exclusions` tetap dikirim sebagai `{}` (kontrak JS tidak berubah). Parameter `parent_combination` di signature helper/route DIPERTAHANKAN (tidak dipakai) agar payload JS tidak perlu berubah | Sedang — hilangnya parent exclusions = konsekuensi platform (MF-03) | BSL-016, 020, 026 |
| `static/src/js/purchase_product_field.js` | DIFF-06, 07 | `@web/core/orm_service` → `@web/core/orm_plugin`. Sisanya tidak diubah (patch tetap valid ke base class baru) | Rendah | BSL-001, 004, 021, 022 |
| `.../product_configurator_dialog.js` | DIFF-01, 02, 04, 05 | `useState` → `proxy`; `useSubEnv` dari `@web/owl2/utils`; `static props` + `static defaultProps` → `props = useProps({...})` dengan schema `t.*` yang setara 1:1 (`edit: t.boolean().optional(false)`) | Sedang | BSL-024, 027, 028 |
| `.../product_list.js` | DIFF-01, 04 | `static props/defaultProps` → `useProps({products: t.array(), areProductsOptional: t.boolean().optional(false)})` | Rendah | BSL-024 |
| `.../product.js`, `.../product_template_attribute_line.js`, `.../badge_extra_price.js` | DIFF-04 | `static props` → `props = useProps({...})` setara (pola native `sale` 20.0). Logika method tidak diubah | Rendah | — |
| 5 file template `.xml` | DIFF-03 | Tambah `this.` di depan setiap member komponen yang dirujuk tanpa prefix (daftar di DIFF-03). **Quirk dipertahankan:** `this.hasPTAVCustom && ...` (tanpa `()`), `size="this.size"` (tetap `undefined`) | Sedang — harus lengkap; satu yang terlewat = error runtime | BSL-025 |
| `static/tests/tours/purchase_product_optional_tour.js` | DIFF-09 | Hapus `test: true`; selector tambah baris disesuaikan ke control "Add a product" bila perlu (divalidasi G2) | Rendah (test-only) | — |
| `tests/test_purchase_product_optional.py` | DIFF-10 | `set_param(...)` → `set_int(...)` di test `TestConvertPrice` (test ikut API baru, asersi tidak diubah) | Rendah (test-only) | BSL-018 |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan |
|---|---|---|---|
| 1 | Manifest version | `__manifest__.py` | — |
| 2 | Xpath list baris PO tidak ketemu → install gagal | `views/purchase_order_views.xml` | DIFF-17 |
| 3 | `get_param/set_param` hilang → onchange PO crash | `models/purchase_order.py`, `product_template.py` | DIFF-10 |
| 4 | `parent_combination` kwarg → dialog RPC `TypeError` | `controllers/main.py` | DIFF-11 |

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `ProductConfiguratorDialogPurchase` | `product_configurator_dialog.js/.xml` | Tinggi | defaultProps throw, `useState` hilang, template `this.` |
| `ProductList` | `product_list.js/.xml` | Tinggi | defaultProps throw, `this.getFormattedTotal()` |
| `Product` | `product.js/.xml` | Tinggi | handler `t-on-click`/`t-on-change` bare, `getFormattedPrice()` |
| `ProductTemplateAttributeLine` | `.js/.xml` | Tinggi | dynamic `t-call="{{this.getPTAVTemplate()}}"`, handler bare |
| `BadgeExtraPrice` | `.js/.xml` | Sedang | `this.getFormattedPrice()` |
| patch `PurchaseOrderLineProductField` | `purchase_product_field.js` | Tinggi | import `orm_plugin` (tanpa ini seluruh file tidak ter-load) |

**Urutan wajib:** Fase E (semua `.js`) selesai dulu, baru Fase F (semua `.xml`).

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `parent_combination` dihapus native | `controllers/main.py` 3 titik | HIGH |
| 2 | `type='jsonrpc'` stabil | 4 route | — |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Glob `static/src/**/*` dan `static/tests/tours/**/*` tetap valid | manifest | — |
| 2 | SCSS var/mixin tetap ada (DIFF-19) | `*.scss` | — |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref |
|---|---|---|---|---|
| 1 | Tidak ada perubahan field/model modul | — | — | — |
| 2 | `ir.config_parameter` "currency_id" disimpan sebagai string int (sama) | — | — | BSL-019 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Native `PurchaseOrderLineProductField` observer kini `useEffect` (tiap render) — pemicu `_onProductTemplateUpdate` bisa sedikit beda timing | native | MEDIUM — divalidasi Tour |
| 2 | Dua dialog (grid native + configurator modul) — CAND-08 tetap | patch | Info |
| 3 | Reaktivitas `proxy` Owl 3: mutasi objek produk di dalam `state` harus memicu render (dipakai native `sale` dengan pola sama) | dialog | MEDIUM — divalidasi Tour |

### Urutan Prioritas Testing

1. Install (G1) — manifest + view xpath.
2. Onchange PO partner/currency (config param API).
3. Controller route (HttpCase).
4. Dialog configurator end-to-end (Tour: buka, add optional, confirm, save).
5. Edit ulang baris (T-03 gap lama) — kandidat tour tambahan.

### View List Checklist

Tidak ada `<tree>` tersisa (sudah `<list>` sejak 17→18). Satu-satunya perubahan view: DIFF-17.

## 3. Data Migration

Tidak ada (port kode saja). Param `currency_id` format tetap string int.

## 4. Scope

### Termasuk
- Semua item tabel §2.

### Di Luar Scope
- Port aset store dari branch rilis `19.0` (MF-01).
- Implementasi ulang parent exclusions (MF-03).
- Perbaikan quirk 19.0 (MF-02).
- Cleanup `console.log`, import `useRecordObserver` tak terpakai, `type` hints — refactor non-wajib.
