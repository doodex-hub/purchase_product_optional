# Baseline Spec — purchase_product_optional

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 18.0.
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (baseline 17.0→18.0 lama, di `source-codebase`) + cross-check LANGSUNG ke kode 18.0 aktual (`source-codebase/purchase_product_optional/models/`, `controllers/`, `views/`) — bukan disalin mentah.

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance vs baseline 17.0→18.0 lama:** 17 dari 18 klaim `[MATCH]` — perilaku 18.0 identik dengan 17.0 untuk BSL-001..009, 011..018 (cross-check kode langsung, tidak ada perubahan). **1 klaim dikoreksi: BSL-017** (lihat di bawah — deskripsi lama sedikit tidak akurat, bukan behavior yang berubah).

1. **[BSL-005]** (masih `[MATCH]`, risiko tertinggi, dibawa dari 17.0) — `onchange_partner_id` di `purchase.order` MASIH menimpa total method core Odoo bernama sama di 18.0 (kode identik baris-per-baris dengan 17.0). **Sama seperti baseline lama: mohon konfirmasi eksplisit ke dev — pertahankan apa adanya (bug-for-bug parity, default migrasi 18→19 ini) atau perbaiki sekalian?** Sampai ada jawaban eksplisit, default `CLAUDE.md` berlaku: **dipertahankan**, tidak diperbaiki.
2. **[BSL-017] — KOREKSI dari baseline lama:** baseline 17.0→18.0 lama menulis "`id_vendor` field TIDAK diberi `string=` eksplisit" — **ini TIDAK akurat**, dicek langsung ke kode 18.0 (`models/purchase_order_line.py:5`): `id_vendor = fields.Char(string='ID')` — **eksplisit** diberi `string='ID'`. Behavior/dampaknya tetap SAMA (label "ID" bentrok dengan label default field `id` bawaan Odoo) — cuma mekanismenya beda (eksplisit, bukan default kosong). Tidak mengubah kesimpulan risiko (masih rendah, field disembunyikan visual via CSS).
3. **Third-party/source-actively-developed** — sama seperti dicatat di `01a_MIGRATION_INTAKE.md` §"Ringkasan untuk Review", belum ada jawaban final eksplisit dev — tidak menghalangi baseline spec ini (baseline murni mendokumentasikan behavior kode, tidak bergantung jawaban itu).
4. **Route/controller style sudah modern** (relevan step 2) — `controllers/main.py` sudah pakai `from odoo.http import Controller, request, route` + `@route(..., type='json', auth='user')` (gaya class-based `Controller` + fungsi `route` Odoo 18, BUKAN `http.Controller`/`http.route` lama). Menurut `knowledge/version-diffs/18-to-19.md` §1, `type='json'` di 19.0 jadi **alias deprecated** untuk `type='jsonrpc'` (backward-compat, TIDAK breaking) — aman diport apa adanya untuk migrasi cepat, cleanup opsional dicatat sebagai kandidat step 3.

---

## 1. Tujuan Modul

Modul ini menambahkan **Product Configurator** (pola sama seperti `sale_product_configurator`, tapi sudah di-port ke basis `sale`+`purchase_product_matrix` sejak migrasi 17→18 — lihat `01a_MIGRATION_INTAKE.md` §2) ke form Purchase Order — memungkinkan produk dengan atribut varian/optional products dikonfigurasi langsung dari baris PO lewat dialog, bukan lewat dropdown produk sederhana. Modul juga menambahkan logic **harga per-vendor** (harga mengikuti `product.supplierinfo` vendor yang dipilih di PO) dan **konversi multi-currency** pada harga yang ditampilkan di dialog.

**Tidak berubah dari 17.0** — verifikasi langsung ke kode 18.0 tidak menemukan perbedaan tujuan/scope fungsional.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `purchase.order` (`_inherit`) | Field `id_vendor` (bridge partner id ke JS) + onchange currency-dari-partner (BSL-005/006) |
| `purchase.order.line` (`_inherit`) | Field custom/no-variant attribute values (pola `sale.order.line`), field `product_add_mode` (tidak aktif — BSL-009), onchange sync `id_vendor` |
| `product.template` (`_inherit`) | Method `convert_price()` — konversi currency harga dialog |
| `product.attribute.custom.value` (`_inherit`) | Relasi balik ke `purchase.order.line` (`purchase_order_line_id`) |

Identik dengan 17.0 — dikonfirmasi cross-check `models/*.py` 18.0.

## 3. Field dengan Makna Bisnis

### `purchase.order`
- `id_vendor` (Char, `string='ID'` — eksplisit, lihat koreksi BSL-017 di atas) — hidden visual (CSS `visibility:hidden`), membawa id partner ke JS lewat DOM.

### `purchase.order.line`
- `product_custom_attribute_value_ids` (One2many → `product.attribute.custom.value`, compute+store+precompute) — custom value atribut per baris PO.
- `product_no_variant_attribute_value_ids` (Many2many → `product.template.attribute.value`, compute) — extra value atribut `no_variant`.
- `product_add_mode` — **tidak aktif secara ORM** (BSL-009), tertelan sebagai kwarg `Many2many` — dikonfirmasi masih identik di 18.0 (`models/purchase_order_line.py:19-24`, paren `Many2many(` belum ditutup sebelum baris `product_add_mode =`).

## 4. Business Workflow / State Transition

- `[BSL-001]` `[MATCH]` Saat `product_template_id` pada baris PO berubah dan `get_single_product_variant()` mengembalikan `has_optional_products=True` (atau tidak ada `product_id` unik), dialog `ProductConfiguratorDialogPurchase` dibuka otomatis. Kalau ada `purchase_warning` bertipe `block`, dialog TIDAK dibuka dan `product_template_id` di-reset ke `false`. Lokasi: `static/src/js/purchase_product_field.js`.
- `[BSL-002]` `[MATCH]` Harga produk utama & optional dicari dari `product.supplierinfo` yang `partner_id`-nya cocok `id_vendor`; fallback ke supplier pertama; fallback ke `standard_price`. Lokasi: `static/src/js/product_configurator_dialog/product_configurator_dialog.js`.
- `[BSL-003]` `[MATCH]` Harga hasil BSL-002 dikonversi lewat RPC `product.template.convert_price(price, from_currency)` — `to_currency` diambil dari `ir.config_parameter` global (lihat BSL-013 soal risikonya). Lokasi: `models/product_template.py` (dikonfirmasi identik baris-per-baris dengan 17.0).
- `[BSL-004]` `[MATCH]` Dialog bisa dibuka ulang untuk baris PO yang sudah dikonfigurasi (`is_configurable_product`) untuk mengubah atribut/optional products.
- `[BSL-014]` `[MATCH]` Saat user klik "Confirm", untuk tiap produk (utama/optional) yang belum punya `product_id` DAN atribut line-nya ada yang `create_variant == 'dynamic'`, variant baru dibuat via RPC `/purchase_product_optional/create_product` (dikonfirmasi masih ada & sama di `controllers/main.py` 18.0) sebelum baris PO ditambahkan/diupdate.
- `[BSL-016]` `[MATCH]` Kombinasi atribut yang termasuk `exclusions`/`parent_exclusions`/`archived_combinations` ditandai `excluded=true`; tombol "Confirm" disabled selama ada produk dengan kombinasi tidak valid. Lokasi: `controllers/main.py::_get_product_information_purchase` (dikonfirmasi `exclusions`/`archived_combinations`/`parent_exclusions` masih dikembalikan sama persis di 18.0), `product_configurator_dialog.js`.

## 5. Server-Side Logic dengan Side Effect

### `purchase.order`
- `[BSL-005]` `[MATCH]` — **RISIKO TERTINGGI** — `onchange('currency_id','partner_id') onchange_partner_id` di `models/purchase_order.py` MASIH menimpa TOTAL method core `purchase.order.onchange_partner_id` bernama sama (nama identik — Python override-by-name, bukan mekanisme extend Odoo). Kode 18.0 identik baris-per-baris dengan 17.0 (dikonfirmasi baca langsung). Efek samping core (payment term/fiscal position/incoterm saat partner berubah) kemungkinan besar tetap tidak jalan sama sekali di 18.0. Belum ada verifikasi live-database ulang di 18.0 (baseline 17.0 lama pernah verifikasi via `__mro__` live test) — kalau step 6/9 punya environment executable, ulangi test yang sama untuk 18.0.
- `[BSL-006]` `[MATCH]` Isi method BSL-005 identik dengan 17.0: partner kosong → simpan `currency_id` form ke config parameter. Partner ada & currency partner == currency PO → set (no-op) + simpan. Partner ada & currency BERBEDA (kasus paling umum) → `self.currency_id = self.currency_id` (no-op literal) + tetap simpan currency yang **tidak berubah**.
- `[BSL-007]` `[MATCH]` `id_vendor` disinkronkan dari `partner_id` via `onchange_id_vendor` — dikonfirmasi identik di `models/purchase_order_line.py:9-11` 18.0.

### `purchase.order.line`
- `[BSL-008]` `[MATCH]` `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values`: saat `product_id` berubah, kedua compute membersihkan value atribut yang tidak lagi valid untuk template produk saat ini — kode identik di 18.0.
- `[BSL-009]` `[MATCH]` `product_add_mode` masih tertelan sebagai kwarg `Many2many(...)`, tidak pernah terdaftar sebagai field ORM — identik dengan 17.0. **Belum diverifikasi ulang eksekusi live di 18.0** (baseline lama verifikasi dari log Odoo 17.0) — kandidat re-run di step 6/9 kalau environment executable tersedia.

### `product.template`
- `[BSL-013]` `[MATCH]` `convert_price(price, from_currency)`: `to_currency` diambil dari `ir.config_parameter` GLOBAL `"currency_id"` — bukan per-user/per-request. Kode identik dengan 17.0 di `models/product_template.py` 18.0. Risiko race condition multi-user tetap ada.
- `[BSL-018]` `[MATCH]` Kalau `ir.config_parameter` key `"currency_id"` belum pernah di-set: `get_param()` → `False` → `int(False)` = `0` → `to_currency` kosong → `_convert()` core Odoo diasumsikan tetap gagal senyap (perilaku core `_convert()` dikonfirmasi **tidak berubah** 17.0→18.0, lihat CAND-03 di `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`) — belum diverifikasi ulang eksekusi live di 18.0 secara spesifik untuk modul ini.

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend
- Form view `purchase.order` (`views/purchase_order_views.xml`) — inherit `purchase.purchase_order_form`. **Perubahan dari 17.0:** dikonfirmasi TIDAK ADA lagi tag `<tree>` di file ini (grep bersih, 0 match `attrs=`/`domain=`/`context=`/`<tree` — lihat `01a_MIGRATION_INTAKE.md` §2b) — migration blocker `<tree>`→`<list>` yang dicatat baseline 17.0 lama SUDAH diperbaiki tuntas selama migrasi 17→18, tidak perlu dikerjakan ulang di 18→19.
- `[BSL-017]` `[MATCH, dikoreksi]` — lihat "Ringkasan untuk Review" poin 2 di atas.
- Komponen Owl (5 file, semua ES6 `class extends Component`, Owl 2 modern — dikonfirmasi TIDAK berubah dari 17.0):
  - `Product` (`static/src/js/product/product.js`)
  - `ProductList` (`static/src/js/product_list/product_list.js`)
  - `ProductTemplateAttributeLine` (`static/src/js/product_template_attribute_line/product_template_attribute_line.js`)
  - `BadgeExtraPrice` (`static/src/js/badge_extra_price/badge_extra_price.js`)
  - `ProductConfiguratorDialogPurchase` (`static/src/js/product_configurator_dialog/product_configurator_dialog.js`, komponen paling kompleks)
  - **Catatan dari migrasi 17→18** (CAND-05, `SUMMARY.md` 17_18): pola `useService("rpc")` sempat jadi breaking change 17→18 (dihapus sebagai Owl service) — dikonfirmasi SUDAH diperbaiki selama migrasi itu (modul ter-install dan G1/G2 pass). Perlu dicek ulang di step 2 apakah idiom `rpc()` yang dipakai sekarang (`@web/core/network/rpc`) masih stabil di 19.0, atau ada perubahan lanjutan.
- `[BSL-011]` `[MATCH]` Kolom tree PO line: `product_template_id` selalu terlihat, `product_id` jadi optional/hidden dengan label "Product Variant".
- `[BSL-012]` `[MATCH, disesuaikan]` `auto_install: True` — baseline 17.0 lama menulis modul auto-install begitu `purchase`+`purchase_product_matrix`+`sale_product_configurator` ter-install; **di 18.0, dependency ketiga sudah jadi `sale`** (bukan `sale_product_configurator`, yang dihapus total di 18.0 — lihat CAND-01/09 `SUMMARY.md` 17_18) — jadi kondisi auto-install sekarang: `purchase`+`purchase_product_matrix`+`sale` ter-install. Behavior mekanismenya (`auto_install: True`) sendiri tidak berubah.
- RPC/route (`controllers/main.py`): `get_values_purchase`, `create_product`, `update_combination`, `get_optional_products` — semua masih ada, signature sama dengan 17.0. **Style controller sudah modern** — pakai `Controller`/`route` (fungsi) dari `odoo.http`, bukan `http.Controller`/`@http.route` class-based lama (sudah di-port selama migrasi 17→18). Route type `type='json'` — lihat "Ringkasan untuk Review" poin 4 soal status di 19.0.

### Public/Frontend
- Tidak ada — modul ini backend-only (form Purchase Order). Tidak berubah dari 17.0.

## 7. Dependency Eksternal

### Eksplisit (manifest, 18.0)
- `depends: ['purchase', 'purchase_product_matrix', 'sale']` — **berbeda dari baseline 17.0 lama** (`sale_product_configurator` sudah diganti `sale` selama migrasi 17→18, lihat CAND-01/09).

### Implisit/Inferred
- Tidak ditemukan dependency implisit lain (tidak ada runtime-check `'x' in self.env` atau `self.env[<variabel>]` dinamis) — dikonfirmasi ulang grep `models/*.py` 18.0, konsisten dengan `01a_MIGRATION_INTAKE.md` §2.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-010]` `[MATCH]` `get_supplierinfo_id()`/`get_optional_product_prices()` (JS) tidak filter `seller_ids` berdasarkan company — di multi-company, seller info company lain ikut terhitung. Dampak rendah kalau instance single-company. Tidak berubah dari 17.0.
- **[Baru, dari migrasi 17→18, CAND-07]** `get_single_product_variant()` (dipanggil `purchase_product_field.js` untuk BSL-001) HANYA mengisi `sale_warning`/`has_optional_products`/`is_combo` — TIDAK PERNAH mengisi `purchase_warning`/`mode` khusus konteks Purchase, karena `purchase`/`purchase_product_matrix` tidak override method ini. Bukan bug migrasi — keterbatasan desain platform yang sudah ada sejak 18.0 (kemungkinan mekanisme setara di 17.0, kalau ada, berasal dari `sale_product_configurator` Enterprise yang sudah dihapus). **Perlu dicek ulang apakah ini masih berlaku sama persis di 19.0** — kandidat step 2.
- **[Baru, dari migrasi 17→18, CAND-08]** Pola "dua dialog dibuka bersamaan tanpa koordinasi" — `purchase_product_matrix.PurchaseOrderLineProductField._onProductTemplateUpdate()` membuka dialog grid "Choose Product Variants" untuk produk matrix-eligible; modul ini men-patch method yang sama untuk dialog Product Configurator sendiri, memanggil `super()` tanpa syarat → berpotensi KEDUA dialog terbuka bersamaan tanpa koordinasi. Dikonfirmasi identik antara 17.0 dan 18.0 (bug/gotcha desain, bukan disebabkan versi) — **kemungkinan besar ini yang dimaksud "MF-01" di `MIGRATION_18_19_STATUS.md`** (lihat `01a_MIGRATION_INTAKE.md` §4a). **Default: dipertahankan apa adanya di 19.0** (bukan bug yang diperbaiki), sesuai larangan `CLAUDE.md` — kecuali dev eksplisit minta diperbaiki. Wajib dicek ulang di step 2 apakah struktur `_onProductTemplateUpdate` di `purchase_product_matrix` 19.0 masih sama (method ini sudah pernah berubah struktur besar 17→18, CAND-02).

---

## Cara Pakai

ID `BSL-NNN` di dokumen ini **dibawa dari baseline 17.0→18.0** untuk behavior yang tidak berubah (konsisten dengan prinsip "kode yang menang, dokumentasi cuma alat bantu") — dirujuk langsung oleh `03_MIGRATION_SPEC.md` (Step 3) dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (Step 5) untuk migrasi 18→19 ini. Jangan diubah/dipakai ulang untuk klaim lain.
