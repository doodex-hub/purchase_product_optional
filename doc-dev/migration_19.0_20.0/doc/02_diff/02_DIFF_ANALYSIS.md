# Diff & Compatibility Analysis — purchase_product_optional

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `01_intake/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

> Semua baris diverifikasi langsung `native-source` (`D:\Kuncoro\doodex\repo\odoo19`) vs `native-target`
> (`D:\Kuncoro\doodex\repo\odoo20`, `release.py` = 20.0 FINAL), hanya untuk simbol yang benar-benar
> dipakai/di-inherit modul.

---

## 0. Knowledge Base Check

| Sumber | Ada entry? | Relevan? |
|---|---|---|
| `version-diffs/19-to-20.md` | Ya (logout POST, `logOutItem` non-export, `ir.access`, `computeOptionalActiveFields`, pin message native) | **Tidak ada yang mengenai modul ini** (modul tidak menyentuh user menu, ACL, list optional fields, mail). Entry ini TIDAK menyebut Owl 3 / `get_param` / `orm_service` — semua temuan kritis di bawah BARU. |
| `dependency-compat/purchase_product_matrix/18-to-19.md` | Ya | Konteks: many2one objek + `useMatrixConfigurator` (sudah di-port 18→19, tetap valid di 20.0). |
| `dependency-compat/purchase_product_matrix/19-to-20.md` | Tidak ada | Temuan DIFF-07/09 kandidat file baru. |

## 0b. Gate Community vs Enterprise

- [x] `01a` §2: tidak ada dependency Enterprise. `purchase_product_matrix`/`product_matrix` 20.0 tetap
      LGPL-3 (manifest dicek).
- [x] `enterprise20` dicek (`ls` + grep): tidak ada modul yang men-patch `PurchaseOrderLineProductField`,
      `pol_product_many2one`, atau form baris PO. `ai_purchase` baru, tidak relevan.

## 0c. Gate Transitive Dependency

- [x] Tidak ada `depends` yang dihapus — N/A.

## 0d. Arah kedua (definisi modul vs definisi BARU native 20.0)

- [x] Nama yang didefinisikan modul (`id_vendor`, `onchange_id_vendor`, `convert_price`,
      `purchase_order_line_id`, `product_custom_attribute_value_ids`, `_compute_custom_attribute_values`,
      `_compute_no_variant_attribute_values`) di-grep ke `purchase`, `purchase_product_matrix`, `product`,
      `sale/models`, `account/models` 20.0: jumlah & lokasi match identik dengan 19.0 (hanya di
      `sale.order.line`/relasi M2M lain — model berbeda). **Tidak ada kolisi baru.**
- [x] `onchange_partner_id` core masih ada nama sama di 20.0 (`purchase/models/purchase_order.py:505-506`)
      → override total BSL-005 tetap berlaku identik.

---

## 1. Perubahan Native

### A. Framework Owl 3 (SEVERITY TERTINGGI — area JS/template)

Odoo 20.0 memakai **Owl `3.0.0-alpha.49`** (`web/static/lib/owl/owl.js`) + compat layer
`web/static/src/owl2/owl3_compatibility_layer.js` (dimuat di `web.assets_backend`).

| ID | Simbol modul | Perubahan 20.0 | Dampak | Sumber |
|---|---|---|---|---|
| DIFF-01 | `static defaultProps` di `ProductConfiguratorDialogPurchase` (`edit:false`) dan `ProductList` (`areProductsOptional:false`) | Compat `Component` constructor **melempar Error** kalau class punya `static defaultProps` ("Owl 3 ignores. Declare the defaults through the props schema") | **BREAKING — dialog crash saat dibuka** (constructor dialog throw) | `owl3_compatibility_layer.js:38-53` |
| DIFF-02 | `import { useState } from "@odoo/owl"` (dialog) | `useState` **tidak diekspor** Owl 3 (daftar export: `proxy`, `signal`, `computed`, `useProps`, ... — tanpa `useState`), compat layer juga tidak menambahkannya. Import → `undefined` | **BREAKING — `TypeError: useState is not a function`** di `setup()` dialog. Pengganti native: `proxy()` (lihat `sale/.../product_configurator_dialog.js` 20.0) | `owl.js` export list; grep `useState` di `web/static/src` 20.0 = 0 |
| DIFF-03 | Semua template XML modul (5 file) memakai nama member "telanjang": `getFormattedPrice()`, `getFormattedTotal()`, `onConfirm`, `onDiscard`, `isPossibleConfiguration()`, `title`, `size`, `decreaseQuantity`, `setQuantity`, `increaseQuantity`, `hasPTAVCustom`, `isSelectedPTAVCustom()`, `showValuesChoice`, `getPTAVTemplate()`, `getPTAVSelectName(ptav)`, `updateCustomValue`, `updateSelectedPTAV` | Owl 3 me-render dengan konteks `ctx = { this: component, __owl__ }` (`owl.js:3715`) — nama bebas dikompilasi jadi `ctx['nama']` (`owl.js:5194`), BUKAN properti komponen lagi. Harus `this.nama`. Native 20.0 mengubah semua template configurator `sale` dengan pola ini | **BREAKING** — render error (`undefined is not a function`), handler `t-on-*` melempar "Invalid handler expression", judul dialog jadi default "Odoo" | `owl.js:3715`, `5192-5197`, `4172-4179`; diff `sale/static/src/js/**.xml` 19 vs 20 |
| DIFF-04 | `static props = {...}` (5 komponen) | Compat `Component` men-set `this.props = owl.useProps()` tanpa schema → `static props` diabaikan (tidak ada validasi, tidak ada default). Pola native 20.0: `props = useProps({ ... t.* ... })`; `t.object` longgar (extra key diizinkan), validasi hanya `app.dev`; `useProps(schema)` HANYA mengekspos key di schema | Non-crash, tapi default props (DIFF-01) harus pindah ke schema `t.xxx().optional(default)` → konversi ke `useProps` diperlukan agar default `edit=false`/`areProductsOptional=false` identik | `owl.js:4722-4790`, `1252-1270` |
| DIFF-05 | `import { useSubEnv } from "@odoo/owl"` | Owl 3 tidak punya `useSubEnv`; compat layer memasangnya ke objek global `owl` (jadi import masih ter-resolve), tapi native 20.0 selalu `import { useSubEnv } from "@web/owl2/utils"` | Rendah — ikuti pola native untuk menghindari ketergantungan urutan load | `owl2/utils.js`, `sale/.../product_configurator_dialog.js` 20.0 baris 1 |

### B. Web client / JS API

| ID | Simbol modul | Perubahan 20.0 | Dampak | Sumber |
|---|---|---|---|---|
| DIFF-06 | `import { x2ManyCommands } from "@web/core/orm_service"` (`purchase_product_field.js`) | File `web/static/src/core/orm_service.js` **tidak ada**; `x2ManyCommands` pindah ke `@web/core/orm_plugin` (semua native 20.0 memakai path ini) | **BREAKING** — modul JS gagal didefinisikan (dependency hilang) → patch `PurchaseOrderLineProductField` tidak terpasang sama sekali + error dependensi di console | `web/static/src/core/orm_plugin.js:29`; grep native import |
| DIFF-07 | `patch(PurchaseOrderLineProductField.prototype, {setup, _onProductTemplateUpdate, onEditConfiguration})` | Base class native jadi `AccountProductField` (dulu `ProductLabelSectionAndNoteField`); observer `useRecordObserver` → `useEffect`; `get label()` dihapus; `setup`/`_onProductTemplateUpdate`/`onEditConfiguration`/`matrixConfigurator` tetap ada dengan isi sama | Non-breaking untuk `patch` (method yang di-`super` masih ada). Import `useRecordObserver` di modul (tidak dipakai) masih diekspor `@web/model/relational_model/utils` | diff `purchase_product_matrix/static/src/js/purchase_product_field.js` 19 vs 20 |
| DIFF-08 | Import lain: `serializeDateTime`, `WarningDialog`, `useService`, `patch`, `useMatrixConfigurator`, `Dialog`, `rpc`, `formatCurrency`, `_t`; service `orm` (`call`, `read`), `dialog` (`add` → prop `close`), `notification`; `StaticList.addNewRecord/delete/currentIds/records`, `Record.update(changes)`; DOM id field `id_vendor_0` (`${name}_${n}`) | Semua masih diekspor/ada dengan semantik sama. `Record.update` kehilangan opsi `{save}` (modul tidak memakainya). `Dialog` props: `title` `t.string().optional("Odoo")`, `size` default `"lg"`, `contentClass` | Tidak berubah | grep export 20.0; `dialog_plugin.js`; `form_arch_parser.js` 19/20 identik |
| DIFF-09 | Tour `static/tests/tours/purchase_product_optional_tour.js` (`{test: true, url, steps}`) | Registry `web_tour.tours` divalidasi `t.strictObject({steps, url})` (selalu, bukan dev-only) → key `test` ditolak; native tour 20.0 tidak punya `test`. Tombol tambah baris PO sekarang control `<create name="add_product_control" string="Add a product">` (native tour: `button:contains('Add a product')`) | **BREAKING (test-only)** — tour gagal registrasi → test Tour gagal | `web_tour/static/src/tour_plugin.js:54-59`; `purchase_product_matrix_tour.js` 20.0 |

### C. Python / ORM

| ID | Simbol modul | Perubahan 20.0 | Dampak | Sumber |
|---|---|---|---|---|
| DIFF-10 | `ir.config_parameter.set_param(...)` (`purchase_order.py`, 3×), `get_param('currency_id')` (`product_template.py`) | `get_param`/`set_param` **dihapus**; diganti API bertipe `get_bool/int/float/str`, `set_bool/int/float/str`. `set_int(key, False/None)` → value kosong ("undefined"); `get_int(key)` → default `0` kalau tidak ada/kosong/invalid | **BREAKING** — `AttributeError` di setiap onchange partner/currency PO (form PO praktis rusak) dan di `convert_price` (dialog harga gagal). Mapping semantik: `set_param(k, id)`→`set_int(k, id)`; `int(get_param(k))`→`get_int(k)` (19: kosong→`int(False)=0`; 20: kosong→`0`) — identik untuk semua nilai yang bisa ditulis modul | `odoo/addons/base/models/ir_config_parameter.py` 19 (60-103) vs 20 (66-161) |
| DIFF-11 | `controllers/main.py`: `product_template._get_attribute_exclusions(parent_combination=..., combination_ids=...)` dan `_get_first_possible_combination(parent_combination=...)` | Signature 20.0: `_get_attribute_exclusions(self, combination_ids=None)`, `_get_first_possible_combination(self, necessary_values=None)` — parent concept dihapus; return tidak lagi punya `parent_exclusions`/`parent_combination`/`parent_product_name`. Model `product.template.attribute.exclusion` (`exclude_for`) diganti `excluded_value_ids` (domain template yang sama) | **BREAKING — `TypeError` di setiap RPC `get_values_purchase`/`get_optional_products`** (dialog tidak bisa dibuka). Fitur parent exclusion (BSL-020) hilang dari platform → MF-03 | `product/models/product_template.py` 19 (926-972, 1282-1293) vs 20 (1273-1302, 1549-1560); `product_template_attribute_value.py` 20 (50-57) |
| DIFF-12 | `controllers/main.py` 4× `@route(type='jsonrpc', auth='user')`, `request.update_context`, `request.env` | Stabil | Tidak berubah | `odoo/http/routing_map.py:122-195`, `requestlib.py:155` |
| DIFF-13 | Helper product: `_get_variant_for_combination`, `_create_product_variant`, `_only_active`, `ptav_active`, `_get_combination_name`, `attribute_line_id`, field `description_purchase`/`seller_ids`/`standard_price`/`optional_product_ids`/`is_product_variant`, `res.currency._convert(from_amount, to_currency, company, date, round)`, `res.partner.property_purchase_currency_id` | Stabil | Tidak berubah | grep 19/20 |
| DIFF-14 | `fields.Many2many(..., product_add_mode=...)` (BSL-009) | `Field %s: unknown parameter %r` warning tetap sama (`orm/fields.py:564`) | Tidak berubah (quirk tetap) | `orm/fields.py` 19:533 / 20:564 |
| DIFF-15 | `sale.product.template.get_single_product_variant()` (dipanggil JS) | `has_optional_products` sekarang `op._get_possible_variants()` TANPA parent PTAV (19: dengan parent) — konsekuensi langsung hilangnya parent exclusions | Rendah — perilaku native, modul tidak override | `sale/models/product_template.py` 19:204-223 / 20:271-289 |
| DIFF-16 | POL UoM: modul membaca `record.data.product_uom` | Field POL 19 `product_uom_id` → 20 `uom_id`; modul membaca nama ketiga yang tidak pernah ada | Tidak berubah (`undefined` di keduanya, BSL-022) | `purchase/models/purchase_order_line.py` 19:43 / 20:182 |

### D. View

| ID | Simbol modul | Perubahan 20.0 | Dampak | Sumber |
|---|---|---|---|---|
| DIFF-17 | `views/purchase_order_views.xml`: `//list/field[@name='product_template_id']` (2×), `//list/field[@name='product_id']` | Form PO 20.0 membungkus `product_id` (+ `name`, `label`) di elemen baru `<column name="product_and_description">`; native matrix 20.0 menaruh `product_template_id` DI DALAM column itu (sebelum `product_id`) dan field tersembunyinya di luar (`<column ...> position="after"`). Xpath anak-langsung `//list/field` **tidak menemukan target** | **BREAKING — install gagal** (`Element ... cannot be located in parent view`). `<column>` merender semua `<field>` anaknya bertumpuk dalam SATU sel dan tidak memproses `column_invisible` per field → field tersembunyi modul TIDAK boleh ditaruh di dalam column | `purchase/views/purchase_views.xml` 20:255-300; `purchase_product_matrix/views/purchase_views.xml` 19 vs 20; `web/static/src/views/list/list_arch_parser.js:158-188` |
| DIFF-18 | `//field[@name='currency_id']` (id_vendor), `//form` (style) | Match pertama tetap field `currency_id` header form (`groups=base.group_multi_currency`) — 19:211 / 20:190 | Tidak berubah | `purchase_views.xml` |

### E. Aset/SCSS

| ID | Simbol | Status | Sumber |
|---|---|---|---|
| DIFF-19 | `$o-btns-bs-override`, `o-field-pointer`, `o-position-absolute`, `$o-view-background-color`, `$input-transition`, `str-replace` | Ada di 20.0; scss PTAL native `sale` 19↔20 identik (selain whitespace) | `web/static/src/scss/*`, bootstrap `_functions.scss` |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Status | Risiko |
|---|---|---|
| — | Tidak ada | — |

## 3. Temuan Baru — Kandidat Migration Records

- DIFF-01/02/03/04 (Owl 3 compat: `defaultProps` throw, `useState` hilang, konteks template
  `{this}`) — **version-diff general** (setiap modul Owl custom di 20.0), kandidat prioritas tertinggi
  `knowledge/version-diffs/19-to-20.md`.
- DIFF-06 (`@web/core/orm_service` → `@web/core/orm_plugin`) — version-diff general.
- DIFF-09 (tour registry strict, `test: true` ditolak) — version-diff general (semua Tour custom).
- DIFF-10 (`get_param`/`set_param` dihapus) — version-diff general, severity tinggi (sangat umum).
- DIFF-11 (parent exclusions dihapus) — dependency-compat `product`/`sale` configurator.
- DIFF-17 (`<column name="product_and_description">` di form PO) — dependency-compat
  `purchase`/`purchase_product_matrix` 19→20.

Dicatat ke `migration-tool/migration-records/purchase_product_optional_19.0_20.0/SUMMARY.md`.

## 4. Ringkasan Risiko

| Item | Risiko | Catatan |
|---|---|---|
| DIFF-17 view xpath | **Tinggi (install-blocking)** | Fase C1 |
| DIFF-10 config param | **Tinggi** | Fase B1 — form PO crash di onchange |
| DIFF-11 exclusions | **Tinggi** | Fase D1 — dialog tidak bisa load; MF-03 |
| DIFF-01/02/03/06 | **Tinggi** | Fase E/F — dialog/field patch rusak total |
| DIFF-04/05 | Sedang | Fase E — konversi `useProps` untuk default |
| DIFF-09 | Sedang (test-only) | Fase G2 |
| DIFF-07/08/12-16/18/19 | Rendah/tidak berubah | Verifikasi G1/G2 |

**Kesimpulan Step 2:** migrasi 19→20 ini jauh lebih berat daripada 18→19 — **7 breaking change pasti**
(view install-blocking, 2 API Python dihapus/berubah signature, 4 breaking Owl 3/JS), semua dengan
satu pola perbaikan yang jelas dari native 20.0 (tidak ada yang butuh pilihan desain berisiko,
kecuali konsekuensi fungsional MF-03 yang tidak bisa dihindari). Siap lanjut ke Step 3.
