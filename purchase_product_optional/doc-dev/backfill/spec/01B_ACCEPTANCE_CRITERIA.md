# Acceptance Criteria — purchase_product_optional

**Module:** `purchase_product_optional`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-29
**Status:** Backfill retroaktif

> Format Given/When/Then, diturunkan dari Business Rules (BR-*) di `01A_FUNCTIONAL_SPEC.md`.

---

## AC-01 — Dialog konfigurator otomatis (ref BR-01)

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given baris PO kosong dan produk template dipilih punya optional products
When `product_template_id` di-set pada baris PO
Then dialog `ProductConfiguratorDialogPurchase` terbuka otomatis (`_openProductConfigurator()`)

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given `get_single_product_variant` mengembalikan `purchase_warning` bertipe `block`
When `product_template_id` di-set pada baris PO
Then dialog TIDAK terbuka, `WarningDialog` ditampilkan, dan `product_template_id` di-reset ke `false`

**AC-01-03** — ref `BR-01` `[HASIL-BACA]`
Given produk template punya variant tunggal tanpa optional products
When `product_template_id` di-set pada baris PO
Then `product_id` langsung di-set ke variant tunggal tersebut tanpa membuka dialog

---

## AC-02 — Harga per-vendor (ref BR-02)

**AC-02-01** — ref `BR-02` `[HASIL-BACA]`
Given produk punya `product.supplierinfo` dengan `partner_id` yang cocok dengan vendor PO (`id_vendor`)
When dialog konfigurator memuat harga produk
Then harga yang ditampilkan = `price` dari supplierinfo yang cocok tersebut

**AC-02-02** — ref `BR-02` `[HASIL-BACA]`
Given produk punya supplierinfo tapi TIDAK ADA yang `partner_id`-nya cocok dengan vendor PO
When dialog konfigurator memuat harga produk
Then harga yang ditampilkan = `price` dari supplierinfo PERTAMA di daftar (bukan `standard_price`)

**AC-02-03** — ref `BR-02` `[HASIL-BACA]`
Given produk sama sekali tidak punya `product.supplierinfo`
When dialog konfigurator memuat harga produk
Then harga yang ditampilkan = `standard_price` produk

---

## AC-03 — Konversi currency (ref BR-03, BR-04)

**AC-03-01** — ref `BR-03` `[HASIL-BACA]`
Given `ir.config_parameter` `currency_id` sudah ter-set ke currency X, dan harga produk berasal dari
currency Y (Y != X)
When `convert_price(price, Y)` dipanggil
Then harga dikembalikan dalam currency X (hasil `res.currency._convert`)

**AC-03-02** — ref `BR-03` `[HASIL-BACA]`
Given currency asal (`from_currency`) sama dengan `ir.config_parameter` `currency_id`
When `convert_price()` dipanggil
Then harga dikembalikan tanpa konversi (early return, `price` asli)

**AC-03-03** — ref `BR-04`+`BR-03` `[PERLU-KEPUTUSAN]` (ref F-05 di `FINDINGS.md`)
Given `ir.config_parameter` `currency_id` BELUM PERNAH di-set (database baru/param dihapus)
When `convert_price()` dipanggil
Then **SEKARANG** melempar `TypeError` (`int(None)`) — bukan fallback ke currency perusahaan/PO,
lihat F-05

**AC-03-04** — ref `BR-04` `[PERLU-KEPUTUSAN]` (ref F-03 di `FINDINGS.md`)
Given partner PO di-set, dan `partner_id.property_purchase_currency_id` BERBEDA dari `currency_id`
form PO saat ini
When onchange `partner_id`/`currency_id` pada `purchase.order` dijalankan
Then **SEKARANG** `self.currency_id` TIDAK berubah (cabang `else` = self-assignment no-op) — hanya
`ir.config_parameter` yang di-set ke currency LAMA (bukan currency partner) — kemungkinan berlawanan
dari tujuan modul ("multi currency"), lihat F-03

**AC-03-05** — ref `BR-05` `[PERLU-KEPUTUSAN]` (ref F-02 di `FINDINGS.md`)
Given Odoo core `purchase.order` punya method `onchange_partner_id` bawaan
When modul ini ter-install (method di-override lewat `_inherit`)
Then perilaku onchange bawaan (kalau ada, mis. set payment term/fiscal position/incoterm dari
partner) **SEKARANG** kemungkinan tidak lagi jalan — perlu verifikasi langsung ke source Odoo 17.0,
lihat F-02

---

## AC-04 — Custom & no-variant attribute values (ref BR-07)

**AC-04-01** — ref `BR-07` `[HASIL-BACA]`
Given baris PO punya `product_custom_attribute_value_ids` untuk atribut custom template A, lalu
`product_id` baris diganti ke produk dari template B
When `_compute_custom_attribute_values` dijalankan
Then custom value yang bukan milik template B dihapus dari `product_custom_attribute_value_ids`

**AC-04-02** — ref `BR-07` `[HASIL-BACA]`
Given baris PO punya `product_no_variant_attribute_value_ids` untuk template A, lalu `product_id`
diganti ke produk dari template B
When `_compute_no_variant_attribute_values` dijalankan
Then value PTAV yang bukan milik template B dihapus dari `product_no_variant_attribute_value_ids`

**AC-04-03** — ref `BR-07` `[HASIL-BACA]`
Given baris PO tidak punya `product_id` sama sekali
When compute dijalankan
Then `product_custom_attribute_value_ids` dan `product_no_variant_attribute_value_ids` di-set `False`/kosong

---

## AC-05 — `product_add_mode` (ref BR-08)

**AC-05-01** — ref `BR-08` `[PERLU-KEPUTUSAN]` (ref F-01 di `FINDINGS.md`)
Given kode `models/purchase_order_line.py` saat ini
When registry Odoo memuat model `purchase.order.line`
Then field `product_add_mode` **TIDAK** terdaftar sebagai field ORM mandiri pada
`purchase.order.line` (hanya jadi kwarg tak-dikenal ke `Many2many`) — perlu verifikasi Step 04 apakah
ini memicu warning/error saat module load

---

## AC-06 — Variant dinamis saat konfirmasi (ref BR-09)

**AC-06-01** — ref `BR-09` `[HASIL-BACA]`
Given produk dipilih di dialog punya atribut dengan `create_variant == 'dynamic'` dan kombinasi belum
punya `product.product` id
When user klik "Confirm"
Then `create_product` RPC dipanggil, variant baru dibuat, `product.id` di-set sebelum baris PO disimpan

**AC-06-02** — ref `BR-09` `[HASIL-BACA]`
Given semua produk (utama+optional) sudah punya `product_id` (variant sudah ada / bukan dynamic)
When user klik "Confirm"
Then tidak ada RPC `create_product` dipanggil, langsung `save()` dengan data existing

---

## AC-07 — Validasi kombinasi (ref BR-10)

**AC-07-01** — ref `BR-10` `[HASIL-BACA]`
Given kombinasi atribut yang dipilih termasuk dalam `exclusions` produk
When `_checkExclusions` dijalankan
Then PTAV terkait ditandai `excluded=true`, badge peringatan tampil, dan tombol "Confirm" disabled
selama produk ini ada di `state.products`

**AC-07-02** — ref `BR-10` `[HASIL-BACA]`
Given semua produk di `state.products` memiliki kombinasi valid (tidak excluded)
When `isPossibleConfiguration()` dipanggil
Then mengembalikan `true`, tombol "Confirm" enabled

---

## AC-08 — Tampilan tree PO line (ref BR-11)

**AC-08-01** — ref `BR-11` `[HASIL-BACA]`
Given form Purchase Order dibuka
When baris PO tree dirender
Then kolom "Product Template" (`product_template_id`) selalu tampil, kolom "Product Variant"
(`product_id`) tersembunyi secara default (bisa dimunculkan manual via optional column toggle)

---

## AC-09 — Auto-install (ref BR-12)

**AC-09-01** — ref `BR-12` `[HASIL-BACA]`
Given database punya `purchase`, `purchase_product_matrix`, dan `sale_product_configurator`
ter-install
When modul lain ter-install/upgrade (trigger auto_install scan)
Then `purchase_product_optional` ikut ter-install otomatis tanpa aksi manual
