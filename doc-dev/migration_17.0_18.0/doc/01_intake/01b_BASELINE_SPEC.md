# Baseline Spec — purchase_product_optional

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 17.0.
**Tanggal:** 2026-08-24
**Sumber:** Direkonsiliasi dari `FUNCTIONAL_SPEC.md`/`FINDINGS.md` lama di `source-codebase/purchase_product_optional/doc-dev/backfill/` + cross-check langsung ke kode aktual (`models/`, `controllers/`, `views/`).

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 12 `[MATCH]` (BSL-001..012, semua BR-01..BR-12 spec lama cocok dengan kode), 0 `[GAP]`, 0 `[NO-SPEC]` murni — tapi 8 di antaranya (BSL-005, 008, 009, 013..017 — lihat §8) adalah **bug/quirk yang harus DIPERTAHANKAN**, bukan diperbaiki.

1. **[BSL-005]** `[MATCH]` (ref: BR-05, F-02) — `onchange_partner_id` di `purchase.order` menimpa TOTAL method core Odoo bernama sama (dikonfirmasi via MRO live database: kelas modul ini muncul lebih dulu dari `purchase.models.purchase_order.PurchaseOrder` di `__mro__`). Efek samping core (payment term/fiscal position/incoterm saat partner berubah) kemungkinan besar tidak jalan sama sekali. **Risiko tertinggi di seluruh baseline ini** — mohon konfirmasi eksplisit: pertahankan apa adanya (bug-for-bug parity, default migrasi) atau perbaiki sekalian di 18.0?
2. **[BSL-006]** `[MATCH]` (ref: BR-04, F-03) — cabang `else` di method yang sama adalah `self.currency_id = self.currency_id` (no-op literal). Pada kondisi paling umum (partner ada, currency partner berbeda dari currency PO), currency PO **tidak pernah** benar-benar ikut berubah — berlawanan dengan docstring method itu sendiri ("Update currency based on the partner's purchase currency").
3. **[BSL-013]** `[MATCH]` (ref: F-04) — currency konversi harga bergantung pada `ir.config_parameter` GLOBAL (bukan per-user/per-request) → race condition kalau >1 user membuka form PO dengan currency berbeda bersamaan.
4. **[BSL-009]** `[MATCH]` (ref: BR-08, F-01) — field `product_add_mode` yang seharusnya jadi field `related` mandiri di `purchase.order.line` tertelan jadi kwarg asing di dalam constructor `fields.Many2many(...)` (paren pembuka belum ditutup) — field ini **tidak pernah terdaftar** sebagai field ORM (dikonfirmasi warning registry Odoo saat load module).
5. **[BSL-015]** `[MATCH]` (ref: F-06) — state vendor (`id_vendor`) dibaca JS langsung dari DOM (`document.getElementById('id_vendor_0')`), bukan lewat props resmi Owl — fragile terhadap perubahan layout view, berpotensi crash `.value` kalau elemen tidak ditemukan.
6. Sisanya (BSL-001..004, 007, 008, 010..012, 014, 016, 017) adalah business rule inti (dialog konfigurator, harga per-vendor, exclusions, dst.) — semua `[MATCH]`, risiko rendah untuk didokumentasikan salah, tapi wajib jadi dasar acceptance criteria satu-per-satu di Step 5.

---

## 1. Tujuan Modul

Modul ini menambahkan **Product Configurator** (pola sama seperti `sale_product_configurator`) ke form Purchase Order — memungkinkan produk dengan atribut varian/optional products dikonfigurasi langsung dari baris PO lewat dialog, bukan lewat dropdown produk sederhana. Modul juga menambahkan logic **harga per-vendor** (harga mengikuti `product.supplierinfo` vendor yang dipilih di PO) dan **konversi multi-currency** pada harga yang ditampilkan di dialog.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `purchase.order` (`_inherit`) | Field `id_vendor` (bridge partner id ke JS) + onchange currency-dari-partner (BSL-005/006) |
| `purchase.order.line` (`_inherit`) | Field custom/no-variant attribute values (pola `sale.order.line`), field `product_add_mode` (tidak aktif — BSL-009), onchange sync `id_vendor` |
| `product.template` (`_inherit`) | Method `convert_price()` — konversi currency harga dialog |
| `product.attribute.custom.value` (`_inherit`) | Relasi balik ke `purchase.order.line` (`purchase_order_line_id`) |

## 3. Field dengan Makna Bisnis

### `purchase.order`
- `id_vendor` (Char) — hidden visual (CSS `visibility:hidden`), membawa id partner ke JS lewat DOM. Label default "ID" (bentrok dengan field `id` bawaan — BSL-017).

### `purchase.order.line`
- `product_custom_attribute_value_ids` (One2many → `product.attribute.custom.value`, compute+store+precompute) — custom value atribut per baris PO.
- `product_no_variant_attribute_value_ids` (Many2many → `product.template.attribute.value`, compute) — extra value atribut `no_variant`.
- `product_add_mode` — **tidak aktif secara ORM** (BSL-009), tertelan sebagai kwarg `Many2many`.

## 4. Business Workflow / State Transition

### Konfigurasi produk di baris PO

- `[BSL-001]` `[MATCH]` (ref: BR-01) Saat `product_template_id` pada baris PO berubah dan `get_single_product_variant()` mengembalikan `has_optional_products=True` (atau tidak ada `product_id` unik), dialog `ProductConfiguratorDialogPurchase` dibuka otomatis. Kalau ada `purchase_warning` bertipe `block`, dialog TIDAK dibuka dan `product_template_id` di-reset ke `false`. Lokasi: `static/src/js/purchase_product_field.js:55-95`.
- `[BSL-002]` `[MATCH]` (ref: BR-02) Harga produk utama & optional dicari dari `product.supplierinfo` yang `partner_id`-nya cocok `id_vendor`; fallback ke supplier pertama; fallback ke `standard_price`. Lokasi: `static/src/js/product_configurator_dialog/product_configurator_dialog.js:97-208`.
- `[BSL-003]` `[MATCH]` (ref: BR-03) Harga hasil BSL-002 dikonversi lewat RPC `product.template.convert_price(price, from_currency)` — `to_currency` diambil dari `ir.config_parameter` global (lihat BSL-013 soal risikonya). Lokasi: `models/product_template.py:11-30`.
- `[BSL-004]` `[MATCH]` (ref: US-04) Dialog bisa dibuka ulang untuk baris PO yang sudah dikonfigurasi (`is_configurable_product`) untuk mengubah atribut/optional products.
- `[BSL-014]` `[MATCH]` (ref: BR-09) Saat user klik "Confirm", untuk tiap produk (utama/optional) yang belum punya `product_id` DAN atribut line-nya ada yang `create_variant == 'dynamic'`, variant baru dibuat via RPC `/purchase_product_optional/create_product` sebelum baris PO ditambahkan/diupdate. Lokasi: `product_configurator_dialog.js:537-557`.
- `[BSL-016]` `[MATCH]` (ref: BR-10) Kombinasi atribut yang termasuk `exclusions`/`parent_exclusions`/`archived_combinations` ditandai `excluded=true`; tombol "Confirm" disabled selama ada produk dengan kombinasi tidak valid. Lokasi: `product_configurator_dialog.js:405-535`, `product.xml`.

## 5. Server-Side Logic dengan Side Effect

### `purchase.order`
- `[BSL-005]` `[MATCH]` (ref: BR-05, F-02) `onchange('currency_id', 'partner_id') onchange_partner_id` — **menimpa TOTAL** method core `purchase.order.onchange_partner_id` (nama identik, kelas modul ini di depan di MRO). Dikonfirmasi lewat inspeksi `__mro__` live database (bukan dugaan). Lokasi: `models/purchase_order.py:9-22`.
- `[BSL-006]` `[MATCH]` (ref: BR-04, F-03) Isi method BSL-005: kalau partner kosong → simpan `currency_id` form saat ini ke config parameter. Kalau partner ada & currency partner == currency PO saat ini → set (no-op, sudah sama) + simpan ke config parameter. Kalau partner ada & currency BERBEDA (kasus paling umum) → `self.currency_id = self.currency_id` (no-op literal) + tetap simpan currency (yang **tidak berubah**) ke config parameter.
- `[BSL-007]` `[MATCH]` (ref: BR-06) `id_vendor` disinkronkan dari `partner_id` via `onchange_id_vendor` (`purchase_order_line.py:9-11`) — dipanggil saat `partner_id` berubah.

### `purchase.order.line`
- `[BSL-008]` `[MATCH]` (ref: BR-07) `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values`: saat `product_id` berubah, kedua compute membersihkan value atribut yang tidak lagi valid untuk template produk saat ini (`valid_product_template_attribute_line_ids`).
- `[BSL-009]` `[MATCH]` (ref: BR-08, F-01) `product_add_mode = fields.Selection(related=...)` didefinisikan SEBAGAI KWARG di dalam `fields.Many2many(...)` (paren `Many2many(` baru ditutup setelah baris ini) — bukan field declaration terpisah. Efeknya: `product_add_mode` **tidak pernah terdaftar** sebagai field ORM di `purchase.order.line` (dikonfirmasi warning registry Odoo: `unknown parameter 'product_add_mode'`). Modul tetap berhasil ter-install (warning, bukan error fatal).

### `product.template`
- `[BSL-013]` `[MATCH]` (ref: F-04) `convert_price(price, from_currency)`: `to_currency` diambil dari `ir.config_parameter` GLOBAL `"currency_id"` (di-set terakhir kali oleh BSL-005/006, lintas SEMUA user/request pada database yang sama) — bukan per-user/per-request. Berisiko race condition kalau >1 user membuka form PO dengan currency berbeda bersamaan.
- `[BSL-018]` `[MATCH]` (ref: F-05) Kalau `ir.config_parameter` key `"currency_id"` belum pernah di-set: `get_param()` mengembalikan `False` → `int(False)` = `0` → `to_currency = browse(0)` (currency kosong) → `_convert()` core Odoo **gagal senyap**, mengembalikan harga PERSIS SAMA dengan input tanpa exception dan tanpa warning ke user (dikonfirmasi eksekusi nyata: `convert_price(100.0, ...)` dengan param unset mengembalikan `100.0` apa adanya). User tidak tahu harga yang ditampilkan sebenarnya belum terkonversi.

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend
- Form view `purchase.order` (`views/purchase_order_views.xml`) — inherit `purchase.purchase_order_form`, xpath ke `//tree/field[@name='product_template_id']` (2×) dan `//tree/field[@name='product_id']`, plus 1× `<tree>` inline untuk sub-view `product_custom_attribute_value_ids`. **Ketiganya pakai tag `<tree>`** — kandidat migration blocker, dicek presisi di Step 2.
- `[BSL-017]` `[MATCH]` (ref: F-08) Field `id_vendor` (Char) tidak diberi `string=` eksplisit — label default bentrok dengan label field `id` bawaan Odoo ("ID"), terdeteksi via warning registry Odoo saat load module. Dampak rendah (field disembunyikan visual via CSS), tapi berpotensi membingungkan di konteks lain (mis. "optional fields" column selector).
- Komponen Owl (5 file, semua ES6 `class extends Component`, Owl 2 modern):
  - `Product` (`static/src/js/product/product.js`)
  - `ProductList` (`static/src/js/product_list/product_list.js`)
  - `ProductTemplateAttributeLine` (`static/src/js/product_template_attribute_line/product_template_attribute_line.js`)
  - `BadgeExtraPrice` (`static/src/js/badge_extra_price/badge_extra_price.js`)
  - `ProductConfiguratorDialogPurchase` (`static/src/js/product_configurator_dialog/product_configurator_dialog.js`, 568 baris — komponen paling kompleks)
- `[BSL-011]` `[MATCH]` (ref: BR-11) Kolom tree PO line: `product_template_id` selalu terlihat (`column_invisible=0`), `product_id` jadi optional/hidden dengan label "Product Variant".
- `[BSL-012]` `[MATCH]` (ref: BR-12) `auto_install: True` — modul terinstall otomatis begitu `purchase`, `purchase_product_matrix`, DAN `sale_product_configurator` sama-sama ter-install.
- RPC/route (`controllers/main.py`): `get_values_purchase`, `create_product`, `update_combination`, `get_optional_products` — semua mem-porting logic `sale_product_configurator` ke konteks purchase (`standard_price`/harga beli, bukan `list_price`).

### Public/Frontend
- Tidak ada — modul ini backend-only (form Purchase Order).

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['purchase', 'purchase_product_matrix', 'sale_product_configurator']`

### Implisit/Inferred
- Tidak ditemukan dependency implisit lain (tidak ada runtime-check `'x' in self.env` atau import silang ke modul yang tidak dideklarasikan).

## 8. Quirk / Behavior Non-Obvious

> Lanjutan penomoran dari §4/§5 — semua sudah ditandai `[BSL-005]`, `[BSL-006]`, `[BSL-009]`, `[BSL-013]`, `[BSL-017]`, `[BSL-018]` di atas karena levelnya server-side/field-level. Dua quirk tambahan murni client-side:

- `[BSL-010]` `[MATCH]` (ref: BR-09, F-07) `get_supplierinfo_id()`/`get_optional_product_prices()` (JS) tidak filter `seller_ids` berdasarkan company — di multi-company, seller info company lain ikut terhitung. Dampak rendah kalau instance single-company.

---

## Cara Pakai

ID `BSL-NNN` di dokumen ini dirujuk langsung oleh `03_MIGRATION_SPEC.md` (Step 3) dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (Step 5) — jangan diubah/dipakai ulang untuk klaim lain.
