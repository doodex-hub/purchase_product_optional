# Baseline Spec — purchase_product_optional

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di **19.0**.
**Tanggal:** 2026-09-24
**Sumber:** Direkonsiliasi dari `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md`
(baseline 18.0) + cross-check LANGSUNG ke kode `migration/19.0` (`models/`, `controllers/`, `views/`,
`static/src/`) dan ke native 19.0 (`odoo19`) untuk perilaku yang bergantung pada core. Test lama
(BACKFILL) ada di `purchase_product_optional/tests/` pada branch yang sama.

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan testing Step 9-11 —
> BUKAN `03_MIGRATION_SPEC.md`. Provenance `[MATCH]` = cocok dengan baseline 18.0 (ref BSL lama) setelah
> cross-check kode 19.0; `[NO-SPEC]` = klaim baru dari baca kode 19.0 langsung (tidak pernah
> didokumentasikan sebelumnya).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally:** 18 `[MATCH]` (BSL-001..014, 016..018 — perilaku 19.0 identik baseline 18.0 secara
fungsional; representasi data JS berubah tuple→objek di 18→19 tapi perilaku sama), 0 `[GAP]`,
10 `[NO-SPEC]` (BSL-019..028 — detail yang baru terlihat saat membaca kode 19.0 untuk kebutuhan 20.0).
`BSL-015` tidak pernah dipakai (warisan penomoran).

1. **[BSL-020] Eksklusi atribut lintas-produk (parent exclusions)** — di 19.0 optional product bisa
   punya nilai atribut yang di-disable berdasarkan kombinasi produk utama (`exclude_for` →
   `product.template.attribute.exclusion`). **Native 20.0 menghapus fitur data ini** — perilaku ini
   tidak bisa dipertahankan (lihat MF-03). Mohon konfirmasi apakah fitur ini pernah dipakai produksi.
2. **[BSL-028] Quirk harga setelah ganti atribut** — di 19.0, begitu user mengubah atribut di dialog,
   harga produk tertimpa `standard_price` (bukan harga vendor) karena `Object.assign(product,
   updatedValues)`. Dipertahankan apa adanya (bug-for-bug parity).
3. **[BSL-021] Perbandingan `product_id` selalu true** — `data.product_id != result.product_id.id`
   (`result.product_id` adalah angka, `.id` = `undefined`) — jalur "produk sederhana + optional" selalu
   masuk. Dipertahankan.
4. **[BSL-005/006] Override total `onchange_partner_id` core** — masih berlaku di 19.0 (core
   `odoo19/addons/purchase/models/purchase_order.py:444-445` punya nama sama). Dipertahankan (keputusan
   dev 18→19).
5. **[BSL-019] Semantik `ir.config_parameter` "currency_id"** — `set_param(key, False)` MENGHAPUS key
   (PO tanpa currency), `get_param` → `False` → `int(False)=0`. API ini dihapus di 20.0 — semantik
   wajib dipertahankan lewat API baru (lihat Step 2 DIFF-04).
6. **CAND-08 dua dialog** — tetap: `super._onProductTemplateUpdate()` native membuka grid matrix untuk
   template configurable, modul lalu membuka dialog sendiri (BSL-001, BSL-004).

---

## 1. Tujuan Modul

Product Configurator untuk baris Purchase Order: saat produk dipilih, dialog "Configure your product"
menampilkan atribut (varian/no-variant/custom/dynamic), optional products, dan harga yang mengikuti
harga vendor (`product.supplierinfo`) PO, dikonversi ke currency yang disimpan global di
`ir.config_parameter`. Juga override onchange partner/currency PO.

## 2. Model & Tanggung Jawab

| Model | Tanggung jawab |
|---|---|
| `purchase.order` (`_inherit`, 2 class di 2 file) | Field `id_vendor` + `onchange_id_vendor`; override `onchange_partner_id` (BSL-005/006/019) |
| `purchase.order.line` (`_inherit`) | `product_custom_attribute_value_ids` (O2M compute store precompute), `product_no_variant_attribute_value_ids` (M2M compute, mendefinisikan ULANG field native `purchase`), `product_add_mode` tertelan (BSL-009) |
| `product.template` (`_inherit`) | `convert_price(price, from_currency)` (BSL-003/013/018) |
| `product.attribute.custom.value` (`_inherit`) | `purchase_order_line_id` (M2O, cascade) |

## 3. Field dengan Makna Bisnis

- `purchase.order.id_vendor` — Char `string='ID'`, disembunyikan CSS, membawa id partner ke JS via DOM
  `#id_vendor_0` (BSL-007, BSL-017).
- `purchase.order.line.product_custom_attribute_value_ids` — nilai custom atribut per baris.
- `purchase.order.line.product_no_variant_attribute_value_ids` — nilai atribut no_variant (compute
  modul menggantikan definisi field native).
- `product_add_mode` — BUKAN field (BSL-009).

## 4. Business Workflow

- `[BSL-001]` `[MATCH]` (ref: BSL-001 18.0, CAND-08) Saat `product_template_id` baris PO berubah
  (native `useRecordObserver` → `_onProductTemplateUpdate`): (a) `super` native dipanggil TANPA await —
  native memanggil `get_single_product_variant()` lalu `record.update(product_id)` untuk produk
  sederhana ATAU `matrixConfigurator.open(record,false)` untuk template configurable; (b) modul memanggil
  `get_single_product_variant()` lagi: kalau ada `product_id` & `has_optional_products` → buka dialog
  modul; kalau ada `product_id` tanpa optional → `record.update(product_id)`; kalau TIDAK ada
  `product_id` (configurable) → `purchase_warning` tidak pernah terisi (CAND-07) → `!result.mode` true →
  buka dialog modul. Akibat (a)+(b): template configurable membuka DUA dialog (grid + configurator).
  Jalur `matrixConfigurator.open` di cabang `else` modul praktis tak terjangkau. Lokasi:
  `static/src/js/purchase_product_field.js:1292-1332`.
- `[BSL-002]` `[MATCH]` (ref: BSL-002 18.0, F-06) Harga produk utama & optional di dialog: cari
  `product.supplierinfo` template yang `partner_id` == `id_vendor` (dibaca dari DOM `#id_vendor_0`);
  kalau `id_vendor` kosong → supplierinfo pertama; fallback `standard_price`. Currency ikut supplierinfo
  yang dipakai, fallback `currency_id` template. Lokasi: `product_configurator_dialog.js`
  `get_product_update_price()`/`get_optional_product_prices()`.
- `[BSL-003]` `[MATCH]` (ref: BSL-003) Harga BSL-002 dikonversi via RPC
  `product.template.convert_price(price, from_currency)` (`orm.call` dengan `[[], price, from]`).
- `[BSL-004]` `[MATCH]` (ref: BSL-004) Edit ulang baris (`onEditConfiguration`, tombol edit di field
  produk): `super` native membuka grid matrix kalau `is_configurable_product`, lalu modul membuka dialog
  modul `edit=true` dengan ptav existing + custom values (normalisasi `record.data` vs `orm.read`, CAND-04).
- `[BSL-014]` `[MATCH]` (ref: BSL-014) "Confirm": produk tanpa `id` yang punya PTAL `create_variant ==
  'dynamic'` → RPC `/purchase_product_optional/create_product` membuat variant dulu.
- `[BSL-016]` `[MATCH]` (ref: BSL-016) Nilai yang ada di `exclusions`/`parent_exclusions`/
  `archived_combinations` ditandai `excluded`; kombinasi tidak valid → pesan "This option or combination
  of options is not available", tombol Confirm disabled, tombol "Add" optional product disabled.

## 5. Server-Side Logic dengan Side Effect

- `[BSL-005]` `[MATCH]` (ref: BSL-005, F-02) `purchase.order.onchange_partner_id` modul (decorator
  `@api.onchange('currency_id','partner_id')`) menimpa TOTAL method core bernama sama di 19.0 (core:
  `@api.onchange('partner_id','company_id')`, set fiscal position/payment term/dll) — tanpa `super()`.
- `[BSL-006]` `[MATCH]` (ref: BSL-006, F-03) Isi: partner kosong → simpan currency form ke param;
  currency partner == currency PO → set (no-op) + simpan; beda → `self.currency_id = self.currency_id`
  (no-op) + simpan currency yang tidak berubah.
- `[BSL-007]` `[MATCH]` (ref: BSL-007) `onchange_id_vendor`: `id_vendor = partner_id.id`.
- `[BSL-008]` `[MATCH]` (ref: BSL-008) Compute custom/no-variant values: tanpa `product_id` → False;
  kosong → dibiarkan; selain itu hapus value yang tidak valid untuk template baru.
- `[BSL-009]` `[MATCH]` (ref: BSL-009, F-01) `product_add_mode` tertelan kwarg `Many2many(...)` →
  warning registry `Field purchase.order.line.product_no_variant_attribute_value_ids: unknown parameter
  'product_add_mode'`, tidak ada field ORM.
- `[BSL-013]` `[MATCH]` (ref: BSL-013, F-04) `convert_price`: `to_currency` = param global
  `currency_id` (bukan per user/PO); currency sama → harga apa adanya; beda → `_convert()` (tanpa
  company/date eksplisit).
- `[BSL-018]` `[MATCH]` (ref: BSL-018, F-05) Param belum di-set → `int(False)=0` → tidak raise
  (terverifikasi test `test_convert_price_param_not_set_returns_without_raising` di 19.0).
- `[BSL-019]` `[NO-SPEC]` (ref: BSL-006 — mekanisme penyimpanan tidak dirinci) Semantik simpan param:
  `set_param('currency_id', <id>)` menyimpan string id; kalau `self.currency_id.id` False →
  `set_param(key, False)` **menghapus** record param (native 19.0 `ir_config_parameter.py:82-103`).
  Baca: `get_param('currency_id')` → string atau `False`; `int(...)`.

### Controller (`controllers/main.py`, 4 route `type='jsonrpc'`, `auth='user'`)

- `[BSL-026]` `[NO-SPEC]` (ref: 18.0 §6 "RPC/route" — kontrak tidak dirinci)
  - `get_values_purchase`: combination dari `ptav_ids` (difilter template, lengkapi PTAL non-multi yang
    belum ada dengan nilai aktif pertama) atau `_get_first_possible_combination()`; mengembalikan
    `products` (1, `parent_product_tmpl_ids=[]`) + `optional_products` (tiap `optional_product_ids`
    dengan kombinasi pertama yang mungkin relatif ke parent, `parent_product_tmpl_ids=[main]`) kecuali
    `only_main_product`.
  - Info produk: `product_tmpl_id`, `id` (False kalau template), `description_purchase`,
    `display_name` (+ nama kombinasi untuk template), **`price = standard_price`**, `quantity`,
    `attribute_lines` (id, attribute{id,name,display_type}, attribute_values{id,name,html_color,image,
    is_custom,price_extra dikonversi ke currency transaksi}, `selected_attribute_value_ids`,
    `create_variant`), `exclusions`, `archived_combinations`, `parent_exclusions`.
  - `create_product` → id variant baru; `update_combination` → info dasar (termasuk `price =
    standard_price`); `get_optional_products` → optional dengan parent combination.

## 6. Client-Side Behavior (Views, JS, Owl)

### View (`views/purchase_order_views.xml`, inherit `purchase.purchase_order_form`)
- `[BSL-011]` `[MATCH]` (ref: BSL-011) Kolom `product_template_id` terlihat (`column_invisible=0`);
  `product_id` `optional=hide` label "Product Variant".
- `[BSL-023]` `[NO-SPEC]` Modul menambah field tersembunyi SETELAH `product_template_id`:
  `product_template_attribute_value_ids`, `product_custom_attribute_value_ids` (subview list
  `custom_product_template_attribute_value_id`/`custom_value`), `product_no_variant_attribute_value_ids`,
  `is_configurable_product` (sebagian duplikat field yang sudah ditambahkan native matrix — tanpa error
  di 19.0); field `id_vendor` (`nolabel`, class `id_vendor`) setelah `currency_id` PERTAMA di form,
  disembunyikan lewat `<style>.id_vendor{visibility:hidden}</style>` yang disisipkan ke dalam `<form>`.

### Owl (5 komponen + patch)
- `ProductConfiguratorDialogPurchase`, `ProductList`, `Product`, `ProductTemplateAttributeLine`,
  `BadgeExtraPrice` (Owl 2, `static props`, `static defaultProps` di dialog `edit:false` dan ProductList
  `areProductsOptional:false`, `useState`, `useSubEnv`, `onWillStart`), patch `PurchaseOrderLineProductField`.
- `[BSL-024]` `[NO-SPEC]` Dialog: judul "Configure your product"; tabel produk utama (Product/
  Quantity/Price + Total) dan "Add optional products" (tombol "Add"); footer "Confirm" (disabled kalau
  kombinasi tidak valid) dan "Cancel" (non-edit: hapus baris PO; edit: cuma tutup). Qty: tombol −/+ dan
  input; produk utama tidak bisa < 1; "Remove product" untuk optional yang sudah ditambahkan.
- `[BSL-027]` `[NO-SPEC]` `_setQuantity` menimpa `product.price` dengan
  `price_product_dialog[tmpl] || this.price` (harga optional hasil RPC, atau harga produk utama).
- `[BSL-028]` `[NO-SPEC]` Ganti atribut → `_updateCombination` → `Object.assign(product,
  updatedValues)` menimpa `price` dengan `standard_price` dari server (harga vendor hilang untuk produk
  itu). Quirk, dipertahankan.
- `[BSL-025]` `[NO-SPEC]` Quirk template: input custom value tampil dengan kondisi
  `hasPTAVCustom && isSelectedPTAVCustom()` (`hasPTAVCustom` referensi fungsi → selalu truthy);
  `Dialog size="size"` → `undefined` → ukuran default Dialog.
- `[BSL-022]` `[NO-SPEC]` Props dialog: `productUOMId` dibaca dari `record.data.product_uom` (field POL
  19.0 bernama `product_uom_id`) → selalu `undefined`; `pricelistId` dari `order.data.pricelist_id`
  (PO tidak punya field itu) → `undefined`. Route menerima None → recordset kosong.
- `[BSL-021]` `[NO-SPEC]` `this.props.record.data.product_id != result.product_id.id` — `.id` pada
  angka = `undefined` → selalu true.
- Save (`applyProductPurchase`): `record.update({product_id:{id,display_name},
  product_no_variant_attribute_value_ids:[set], product_custom_attribute_value_ids:[set([]), create...]})`
  lalu `record.update({product_qty})`; optional → `order_line.addNewRecord({position:'bottom',
  mode:'readonly'})` + apply. Side effect `console.log` ("Main Product Quantity:", "tes",
  "Checking configuration:") dipertahankan.
- `[BSL-012]` `[MATCH]` `auto_install: True` (purchase + purchase_product_matrix + sale).

## 7. Dependency Eksternal

- Eksplisit: `purchase`, `purchase_product_matrix`, `sale`.
- Implisit: `product_matrix` (hook JS), `account` (base class field widget native), `web_tour` (test).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-010]` `[MATCH]` (ref: BSL-010, F-07) Supplierinfo tidak difilter company.
- `[BSL-017]` `[MATCH]` (ref: BSL-017, F-08) Label `id_vendor` = "ID" (eksplisit).
- `[BSL-020]` `[NO-SPEC]` (ref: BSL-016 — mekanisme parent tidak dirinci) Parent exclusions:
  `_get_attribute_exclusions(parent_combination=...)` native 19.0 mengembalikan `parent_exclusions`
  dari `exclude_for` lintas template (mis. "Optional X warna Merah tidak tersedia kalau produk utama
  Kaki: Baja"); `_get_first_possible_combination(parent_combination=...)` melewati kombinasi yang
  tereksklusi parent. JS menandai `excluded` untuk nilai di `parent_exclusions[ptavId]`.

---

## Cara Pakai

ID `BSL-NNN` dibawa dari baseline 18.0 untuk perilaku yang tidak berubah; BSL-019..028 baru. Dirujuk
`03_MIGRATION_SPEC.md` dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`. Jangan dipakai ulang untuk klaim lain.
