# Functional Spec — purchase_product_optional

**Module:** `purchase_product_optional`
**Odoo Version:** 17.0
**Depends:** `purchase`, `purchase_product_matrix`, `sale_product_configurator`
**Last Updated:** 2026-07-29
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `CLAUDE.md` §Provenance Tag untuk arti `[HASIL-BACA]`/`[DIKONFIRMASI]`/`[PERLU-KEPUTUSAN]`

---

## Ringkasan untuk Review — Perlu Konfirmasi User

> Maks. 5-8 poin — item juga muncul di `FINDINGS.md` dengan detail lengkap.

1. **F-02 (Tinggi):** `onchange_partner_id` di `purchase_order.py` memakai nama method yang sama
   dengan (kemungkinan) onchange bawaan Odoo core `purchase.order` — berpotensi override total
   perilaku currency/payment-term/fiscal-position bawaan, bukan sekadar menambah currency-sync.
2. **F-03 (Tinggi):** Cabang `else` di method yang sama adalah `self.currency_id = self.currency_id`
   (no-op) — pada kondisi paling umum (partner ada, currency partner berbeda dari currency PO saat
   ini), currency PO TIDAK PERNAH benar-benar berubah mengikuti partner, berlawanan dengan docstring-nya.
3. **F-04 (Tinggi):** Currency konversi harga (`convert_price`) bergantung pada `ir.config_parameter`
   global (`currency_id`) yang ditulis tiap onchange partner — bukan per-user/per-request, berisiko
   race condition kalau lebih dari satu user membuka form PO dengan currency berbeda bersamaan.
4. **F-01 (Tinggi):** Field `product_add_mode` yang seharusnya jadi field `related` mandiri di
   `purchase.order.line` tertelan jadi argumen `fields.Many2many(...)` lain (missing closing paren) —
   field ini efektif tidak pernah terdaftar sebagai field ORM.
5. **F-06 (Sedang):** State vendor (`id_vendor`) dilewatkan dari form ke dialog JS lewat
   `document.getElementById('id_vendor_0')`, bukan lewat props resmi OWL — fragile terhadap
   perubahan layout view.

---

## Latar Belakang & Tujuan

Modul ini menambahkan **Product Configurator** (pola yang sama dengan `sale_product_configurator`)
ke form Purchase Order — memungkinkan produk dengan atribut varian/optional products dikonfigurasi
langsung dari baris PO lewat dialog, bukan lewat dropdown produk sederhana. Modul juga menambahkan
logic **harga per-vendor** (harga ditampilkan berdasarkan `product.supplierinfo` vendor yang dipilih
di PO) dan **konversi multi-currency** pada harga yang ditampilkan di dialog. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Dialog konfigurasi produk (atribut varian, custom value, no-variant value, optional products)
  saat memilih `product_template_id` di baris Purchase Order. `[HASIL-BACA]`
- 4 endpoint JSON-RPC (`get_values_purchase`, `create_product`, `update_combination`,
  `get_optional_products`) yang mem-porting logic `sale_product_configurator` ke konteks purchase
  (memakai `standard_price`/harga beli, bukan `list_price`/harga jual). `[HASIL-BACA]`
- Perhitungan harga produk (utama & optional) berdasarkan vendor yang dipilih di PO
  (`product.supplierinfo` cocok `partner_id`), fallback ke supplier pertama, fallback ke
  `standard_price`. `[HASIL-BACA]`
- Konversi currency tampilan harga di dialog via `product.template.convert_price()`. `[HASIL-BACA]`
- Auto-update `purchase.order.currency_id` mengikuti partner (onchange) — lihat catatan bug F-02/F-03
  di atas soal implementasi. `[HASIL-BACA]`
- Field tambahan `id_vendor` (Char, hidden) di `purchase.order` untuk membawa partner id ke sisi JS.
  `[HASIL-BACA]`
- Perubahan tampilan tree PO line: kolom `product_template_id` selalu terlihat, kolom `product_id`
  jadi optional/tersembunyi dengan label "Product Variant". `[HASIL-BACA]`
- `auto_install: True` — modul terinstall otomatis begitu ketiga dependency-nya ter-install (tidak
  perlu instalasi manual). `[HASIL-BACA]`

### Yang Tidak Termasuk

Tidak ada indikasi eksplisit dari kode (comment/TODO) yang menyebut scope yang sengaja tidak dibuat.
`[HASIL-BACA]`

---

## User Stories (rekonstruksi)

> Ditulis dari sudut pandang kode, bukan wawancara user asli.

### US-01 — Konfigurasi produk saat membuat PO line
Sebagai buyer, saat saya memilih produk (template) yang punya optional products/atribut varian di
baris Purchase Order, saya ingin dialog konfigurasi terbuka otomatis supaya saya bisa memilih
atribut dan menambah produk optional sebelum baris PO tersimpan. `[HASIL-BACA]`

### US-02 — Harga sesuai vendor yang dipilih
Sebagai buyer, saya ingin harga yang ditampilkan di dialog konfigurator mengikuti harga vendor yang
sedang saya pilih di PO (bukan selalu `standard_price` global), supaya estimasi total PO lebih akurat
per vendor. `[HASIL-BACA]`

### US-03 — Harga dalam currency yang sesuai
Sebagai buyer yang bertransaksi dengan vendor luar negeri, saya ingin harga yang ditampilkan di
dialog dikonversi ke currency yang relevan. `[HASIL-BACA]`

### US-04 — Edit konfigurasi produk yang sudah ada di baris PO
Sebagai buyer, saya ingin bisa membuka kembali dialog konfigurator untuk baris PO yang sudah
dikonfigurasi (`is_configurable_product`) untuk mengubah atribut/optional products-nya. `[HASIL-BACA]`

---

## Business Rules

### BR-01 — Dialog konfigurator terbuka otomatis
Saat `product_template_id` pada baris PO berubah dan `product.template.get_single_product_variant()`
mengembalikan `has_optional_products=True` (atau tidak ada `product_id` unik), dialog
`ProductConfiguratorDialogPurchase` dibuka otomatis. Kalau ada `purchase_warning` bertipe `block`,
dialog TIDAK dibuka dan `product_template_id` di-reset ke `false`. `[HASIL-BACA]`
**Lokasi kode:** `static/src/js/purchase_product_field.js:55-95`

### BR-02 — Harga berdasarkan vendor (`id_vendor`)
Harga produk utama & optional di dialog dicari dari `product.supplierinfo` yang `partner_id`-nya
cocok dengan `id_vendor` (id partner PO). Kalau tidak ada match, pakai supplier pertama di daftar
(`supplierinfo[0]`). Kalau tidak ada supplierinfo sama sekali, pakai `standard_price` produk.
`[HASIL-BACA]`
**Lokasi kode:** `static/src/js/product_configurator_dialog/product_configurator_dialog.js:97-208`

### BR-03 — Currency konversi harga dialog
Harga hasil BR-02 dikonversi lewat RPC `product.template.convert_price(price, from_currency)` —
`from_currency` diambil dari `currency_id` produk/supplierinfo, `to_currency` diambil dari
`ir.config_parameter` global `currency_id` (di-set terakhir kali oleh onchange BR-04). `[HASIL-BACA]`
**Lokasi kode:** `models/product_template.py:11-30`

### BR-04 — Auto-update currency PO dari partner
`onchange('currency_id', 'partner_id')` pada `purchase.order`: kalau partner kosong, simpan
currency_id form saat ini ke config parameter. Kalau partner ada DAN
`partner_id.property_purchase_currency_id == currency_id` saat ini, set currency_id (no-op karena
sudah sama) lalu simpan ke config parameter. Kalau partner ada dan currency BERBEDA (kasus paling
umum), cabang `else` melakukan `self.currency_id = self.currency_id` (no-op literal) lalu tetap
menyimpan currency_id (yang TIDAK berubah) ke config parameter. `[PERLU-KEPUTUSAN]` — lihat F-03,
kemungkinan bug: currency PO tidak pernah benar-benar disinkronkan ke `property_purchase_currency_id`
partner pada kasus yang justru paling relevan.
**Lokasi kode:** `models/purchase_order.py:9-22`

### BR-05 — Method onchange menimpa nama core Odoo
`onchange_partner_id` pada `_inherit purchase.order` didefinisikan dengan nama yang identik dengan
kemungkinan method onchange bawaan Odoo core untuk `purchase.order`. `[PERLU-KEPUTUSAN]` — lihat F-02,
perlu verifikasi langsung ke source Odoo 17.0 (Step 04) apakah ini menimpa logic asli (payment term/
fiscal position/incoterm dari partner).
**Lokasi kode:** `models/purchase_order.py:9`

### BR-06 — `id_vendor` disinkronkan dari partner
`purchase.order.id_vendor` (Char) di-set ke `self.partner_id.id` via `onchange('partner_id')`
terpisah (`onchange_id_vendor`, di `purchase_order_line.py`) — field ini hidden secara visual di form
(`visibility: hidden` CSS) tapi tetap ada di DOM untuk dibaca JS. `[HASIL-BACA]`
**Lokasi kode:** `models/purchase_order_line.py:7-11`, `views/purchase_order_views.xml:27-36`

### BR-07 — Custom & no-variant attribute values tersimpan di baris PO
`purchase.order.line` menambah `product_custom_attribute_value_ids` (One2many ke
`product.attribute.custom.value`, computed+store+precompute) dan
`product_no_variant_attribute_value_ids` (Many2many ke `product.template.attribute.value`,
computed) — pola identik dengan `sale.order.line` di `sale_product_configurator`. Kedua compute
membersihkan value yang tidak lagi valid untuk template produk saat ini (`product_id` berubah).
`[HASIL-BACA]`
**Lokasi kode:** `models/purchase_order_line.py:14-56`

### BR-08 — `product_add_mode` tidak benar-benar terdaftar
Field `product_add_mode` (`related='product_id.product_template_id.product_add_mode'`) yang tampaknya
dimaksudkan sebagai field mandiri di `purchase.order.line`, secara sintaks Python malah menjadi kwarg
tak terpakai di dalam constructor `fields.Many2many(...)` milik `product_no_variant_attribute_value_ids`
(paren pembuka `Many2many(` baru ditutup setelah baris `product_add_mode=...`). `[PERLU-KEPUTUSAN]` —
lihat F-01.
**Lokasi kode:** `models/purchase_order_line.py:24-28`

### BR-09 — Variant dinamis dibuat saat konfirmasi
Saat user klik "Confirm" di dialog, untuk tiap produk (utama/optional) yang belum punya `product_id`
DAN atribut line-nya ada yang `create_variant == 'dynamic'`, variant baru dibuat via RPC
`/purchase_product_optional/create_product` sebelum baris PO ditambahkan/diupdate. `[HASIL-BACA]`
**Lokasi kode:** `static/src/js/product_configurator_dialog/product_configurator_dialog.js:537-557`

### BR-10 — Kombinasi tidak valid ditandai & tidak bisa dikonfirmasi
Kombinasi atribut yang termasuk `exclusions`/`parent_exclusions`/`archived_combinations` (dari
`product.template._get_attribute_exclusions()`) ditandai `excluded=true` di state JS — badge warning
"This option or combination of options is not available" muncul, dan tombol "Confirm" disabled
selama ada produk dengan kombinasi tidak valid (`isPossibleConfiguration()`). `[HASIL-BACA]`
**Lokasi kode:** `static/src/js/product_configurator_dialog/product_configurator_dialog.js:405-535`,
`static/src/js/product/product.xml:23`, `product.xml:14`

### BR-11 — Kolom tree PO line
View `purchase.order` form: kolom `product_template_id` di tree baris PO selalu ditampilkan
(`column_invisible=0`), kolom `product_id` jadi optional/hidden dengan label "Product Variant".
`[HASIL-BACA]`
**Lokasi kode:** `views/purchase_order_views.xml:9-26`

### BR-12 — Auto-install
Modul `auto_install: True` — akan terinstall otomatis begitu `purchase`, `purchase_product_matrix`,
DAN `sale_product_configurator` sama-sama ter-install di database, tanpa aksi manual. `[HASIL-BACA]`
**Lokasi kode:** `__manifest__.py:29`
