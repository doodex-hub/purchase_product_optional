# Functional Spec — purchase_product_optional

**Module:** `purchase_product_optional`
**Odoo Version:** 17.0
**Depends:** `purchase`, `purchase_product_matrix`, `sale_product_configurator` (`auto_install: True`)
**Last Updated:** 2026-07-28
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `doc-dev-backfill/templates/CLAUDE_TEMPLATE.md` §Provenance Tag untuk arti `[HASIL-BACA]`/`[DIKONFIRMASI]`/`[PERLU-KEPUTUSAN]`

> Template ini identik strukturnya dengan `doc/spec/FUNCTIONAL_SPEC.md` versi SOP dev normal
> (`cicd/test_design/odoo-module-folder-structure.md`) — cuma cara mengisinya beda: retroaktif dari
> kode, bukan dari requirement baru. Setiap klaim di bawah WAJIB diberi satu provenance tag.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

> Maks. 5-8 poin — cuma yang genuinely ambigu/berisiko/butuh keputusan pemilik modul. Item di sini
> juga muncul di `FINDINGS.md`.

1. **F-03 (Tinggi)** — `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL (bukan per-record),
   lalu dibaca balik oleh `convert_price` untuk konversi harga di dialog configurator. Berisiko race
   condition antar user/PO yang dibuka bersamaan — lihat `FINDINGS.md` F-03.
2. **F-02 (Sedang)** — `onchange_partner_id` (docstring: "update currency based on partner") tidak
   pernah benar-benar mengubah `currency_id` di ketiga cabang if/elif/else-nya — kemungkinan bug
   logic terbalik. Lihat `FINDINGS.md` F-02.
3. **F-04 (Sedang)** — Harga per-vendor di dialog configurator dibaca dari DOM langsung
   (`document.getElementById('id_vendor_0')`), bukan dioper eksplisit sebagai parameter — rapuh
   terhadap perubahan konvensi id Odoo atau multi-form-di-satu-halaman. Lihat `FINDINGS.md` F-04.
4. **F-01 (Rendah)** — Field `product_add_mode` di `purchase.order.line` tidak pernah benar-benar
   terdaftar (bug syntax/parenthesis), tapi tidak dipakai di tempat lain — kemungkinan dampak nol
   saat ini. Lihat `FINDINGS.md` F-01.
5. ~~F-05 (Tinggi, ditemukan Step 04) — `convert_price` kemungkinan CRASH~~ — **❌ TIDAK TERBUKTI**,
   dikonfirmasi lewat eksekusi nyata Mode B 2026-07-28: `_convert()` TIDAK crash tanpa argumen
   `company`/`date` di versi Odoo yang dites. Hipotesis awal (dari baca kode + signature upstream)
   salah — lihat `FINDINGS.md` F-05 untuk detail lengkap kronologinya.

---

## Latar Belakang & Tujuan

Modul ini menambahkan **Product Configurator** (dialog pemilihan atribut produk + optional
products, dipinjam konsepnya dari `sale_product_configurator`/`purchase_product_matrix`) ke form
Purchase Order — memungkinkan pembeli memilih varian/atribut produk dan produk opsional terkait
langsung dari baris PO, alih-alih hanya memilih varian produk yang sudah jadi lewat dropdown biasa.
Modul juga menghitung harga produk berdasarkan vendor yang dipilih pada PO tersebut (bukan cuma
harga standar produk), dan mengurus konversi mata uang antara mata uang produk dan mata uang PO.
`[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Menampilkan dialog Product Configurator (`ProductConfiguratorDialogPurchase`) saat baris PO
  memilih produk yang punya atribut/optional products, dipicu dari patch terhadap
  `PurchaseOrderLineProductField` (`purchase_product_field.js`). `[HASIL-BACA]`
- Endpoint JSON RPC (`controllers/main.py`) yang menyediakan data produk+atribut+optional
  products+exclusion rules untuk dialog: `get_values_purchase`, `create_product`,
  `update_combination`, `get_optional_products`. `[HASIL-BACA]`
- Perhitungan harga produk (utama & optional) berdasarkan `product.supplierinfo` milik vendor yang
  tercatat di PO (via field custom `id_vendor` pada `purchase.order`), dengan fallback ke
  `standard_price` produk kalau vendor tidak match supplierinfo manapun. `[HASIL-BACA]`
- Konversi mata uang harga produk ke mata uang PO lewat `product.template.convert_price` — lihat
  catatan risiko di F-03. `[HASIL-BACA]`
- Field tambahan di `purchase.order.line`: `product_custom_attribute_value_ids` (custom attribute
  value per baris), `product_no_variant_attribute_value_ids` (atribut no-variant + extra price).
  `[HASIL-BACA]`
- Field tambahan di `purchase.order`: `id_vendor` (Char, disimpan dari `partner_id.id` lewat
  onchange, disembunyikan visual di form lewat CSS custom). `[HASIL-BACA]`
- Penyesuaian tampilan tree/list baris PO: kolom `product_template_id` dipaksa selalu terlihat
  (`column_invisible=0`), kolom `product_id` disembunyikan default dan diberi label ulang "Product
  Variant". `[HASIL-BACA]`

### Yang Tidak Termasuk

Tidak ada indikasi eksplisit dari kode soal batasan scope yang sengaja tidak dibuat (tidak ada
comment/TODO yang menyatakan "sengaja tidak menangani X"). `[HASIL-BACA]`

---

## User Stories (rekonstruksi)

> Ditulis dari sudut pandang kode, bukan wawancara user asli — beri label rekonstruksi.

### US-01 — Memilih produk dengan atribut/optional products di baris PO
Sebagai staff Purchasing, saat saya memilih produk template yang punya atribut varian atau produk
opsional terkait pada baris Purchase Order, sistem menampilkan dialog Product Configurator supaya
saya bisa memilih kombinasi atribut yang tepat dan menambahkan produk opsional sekaligus, tanpa
harus menambah baris PO satu per satu secara manual. `[HASIL-BACA]`

### US-02 — Melihat harga sesuai vendor yang dipilih
Sebagai staff Purchasing, saat saya membuka dialog configurator untuk sebuah PO yang vendornya
sudah dipilih, saya ingin melihat harga produk (utama maupun optional) mengikuti harga vendor
tersebut (dari `product.supplierinfo`) — bukan cuma harga standar produk — supaya estimasi biaya
PO lebih akurat. `[HASIL-BACA]`

### US-03 — Mengedit konfigurasi produk yang sudah tersimpan
Sebagai staff Purchasing, saat saya membuka kembali baris PO yang produknya sudah dikonfigurasi
sebelumnya, saya ingin dialog configurator terbuka kembali dengan kombinasi atribut & custom value
yang sudah tersimpan (lewat tombol edit, `_editProductConfiguration`), bukan mulai dari kosong.
`[HASIL-BACA]`

---

## Business Rules

### BR-01 — Trigger pembukaan dialog configurator berdasarkan `product.template.get_single_product_variant`
Saat `product_template_id` pada baris PO diubah (`_onProductTemplateUpdate`), sistem memanggil
method `get_single_product_variant` di `product.template` (bukan didefinisikan di modul ini —
berasal dari `sale_product_configurator`) untuk menentukan: (a) apakah produk punya varian tunggal
langsung terpakai, (b) apakah ada peringatan pembelian (`purchase_warning`, tipe `block`/`warning`),
dan (c) mode dialog yang harus dibuka — `configurator` (dialog atribut biasa) atau grid/matrix
(`_openGridConfigurator`, method warisan dari `purchase_product_matrix`, tidak didefinisikan di
modul ini). Default mode kalau `result.mode` kosong adalah `'configurator'`. `[HASIL-BACA]`
**Lokasi kode:** `purchase_product_optional/static/src/js/purchase_product_field.js:55-94`

### BR-02 — Update mata uang PO berdasarkan vendor (docstring), TIDAK benar-benar dieksekusi
Docstring `onchange_partner_id` menyatakan currency PO seharusnya mengikuti
`partner_id.property_purchase_currency_id`, tapi implementasi ketiga cabangnya tidak pernah benar-
benar mengubah `self.currency_id` ke nilai lain dari yang sudah ada (lihat detail di `FINDINGS.md`
F-02). Efek nyata SAAT INI: currency PO tidak pernah otomatis di-override oleh preferensi partner.
`[PERLU-KEPUTUSAN]` — lihat `FINDINGS.md` F-02.
**Lokasi kode:** `purchase_product_optional/models/purchase_order.py:9-22`

### BR-03 — Currency PO disimpan sementara ke `ir.config_parameter` sebagai jembatan ke `convert_price`
Efek samping dari BR-02: tiap kali `onchange_partner_id` jalan, `currency_id.id` PO yang sedang
diedit ditulis ke system parameter global `'currency_id'`. `product_template.convert_price`
kemudian membaca parameter global ini sebagai mata uang TARGET saat mengonversi harga vendor/produk
untuk ditampilkan di dialog configurator. Karena `ir.config_parameter` bersifat singleton
system-wide (bukan per-record), mekanisme ini rentan race condition di lingkungan multi-user.
`[PERLU-KEPUTUSAN]` — lihat `FINDINGS.md` F-03.
**Lokasi kode:** `purchase_product_optional/models/purchase_order.py:9-22`,
`purchase_product_optional/models/product_template.py:11-30`

**Update Step 04 (2026-07-28, ditulis saat test dibuat):** sempat diduga ada finding TERPISAH dan
LEBIH SEVERE — pemanggilan `from_currency._convert(from_amount=price, to_currency=to_currency)`
tanpa argumen `company`/`date` yang menurut signature upstream WAJIB. **Update lagi (2026-07-28,
setelah Mode B nyata dijalankan dev):** hipotesis ini **TIDAK TERBUKTI** — test
`test_ac_03_03_convert_price_crashes_on_real_conversion` FAIL karena `_convert()` ternyata TIDAK
crash. Mekanisme global-config-parameter (BR-03 di atas) tetap valid sebagai risiko race condition
— cuma dugaan "pasti crash" (F-05) yang salah. Lihat `FINDINGS.md` F-05 untuk kronologi lengkap.

### BR-04 — `product_add_mode` dimaksudkan sebagai related field, tapi tidak pernah terdaftar
Baris kode yang dimaksudkan mendefinisikan `product_add_mode` (related ke
`product_id.product_template_id.product_add_mode`) pada `purchase.order.line` gagal terdaftar
sebagai field karena kesalahan parenthesis — lihat `FINDINGS.md` F-01. Field ini tidak dipakai di
tempat lain manapun di modul, jadi efek fungsional langsung saat ini nol, tapi field yang
dimaksudkan desainnya (kemungkinan untuk membedakan mode "Optional Products" vs "matrix/grid" per
baris PO) tidak pernah benar-benar ada. `[PERLU-KEPUTUSAN]` — lihat `FINDINGS.md` F-01.
**Lokasi kode:** `purchase_product_optional/models/purchase_order_line.py:24-28`

### BR-05 — Harga produk mengikuti supplier info vendor yang tercatat di PO, fallback ke standard price
`get_optional_product_prices`/`get_product_update_price` (di JS dialog) mencari
`product.supplierinfo` milik produk yang `partner_id`-nya cocok dengan `id_vendor` PO (dibaca dari
DOM, lihat BR-06). Kalau vendor cocok ditemukan di daftar supplierinfo produk, harga & currency dari
supplierinfo itu dipakai. Kalau tidak cocok/`id_vendor` kosong, fallback ke supplierinfo PERTAMA
dalam daftar (`supplierinfo[0]`) kalau ada, atau ke `standard_price` produk kalau supplierinfo sama
sekali tidak ada. `[HASIL-BACA]`
**Lokasi kode:** `purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js:109-208`

### BR-06 — Vendor PO diketahui dialog lewat pembacaan DOM langsung, bukan parameter eksplisit
Dialog configurator membaca ID vendor bukan dari props/RPC seperti data lain (currency, company,
pricelist — yang semuanya dioper eksplisit lewat `_openProductConfigurator`), melainkan lewat
`document.getElementById('id_vendor_0').value` saat dialog di-setup. Field `id_vendor` sendiri
diisi via onchange partner (`onchange_id_vendor` di `purchase_order_line.py`) dan disembunyikan
visual di form lewat CSS custom (bukan mekanisme `invisible` Odoo). `[PERLU-KEPUTUSAN]` — lihat
`FINDINGS.md` F-04.
**Lokasi kode:** `purchase_product_optional/models/purchase_order_line.py:7-11`,
`purchase_product_optional/views/purchase_order_views.xml:27-36`,
`purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js:41-43`

### BR-07 — Optional products otomatis diambil rekursif berdasarkan kombinasi atribut yang dipilih
Saat produk utama ditambahkan ke state dialog, daftar `optional_product_ids`-nya (field bawaan
`product.template` dari `sale_product_configurator`) diambil lewat endpoint
`get_optional_products`, termasuk exclusion rules (`_get_attribute_exclusions`) berdasarkan
kombinasi atribut produk utama & parent-nya. Produk optional bisa dipindah antara daftar
`state.products` (dipilih, quantity>0) dan `state.optionalProducts` (tersedia tapi belum dipilih)
lewat `_addProduct`/`_removeProduct`, termasuk penghapusan berantai ke child optional products yang
kehilangan semua parent-nya. `[HASIL-BACA]`
**Lokasi kode:** `purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js:265-315`,
`purchase_product_optional/controllers/main.py:157-204`

### BR-08 — Attribute custom value & no-variant value disinkronkan lewat compute field yang membersihkan value tidak valid
`product_custom_attribute_value_ids` dan `product_no_variant_attribute_value_ids` di
`purchase.order.line` adalah compute field (`store=True, readonly=False, precompute=True`) yang
membersihkan value yang tidak lagi valid untuk `product_id` saat ini (mis. produk diganti) —
membandingkan terhadap `valid_product_template_attribute_line_ids` produk yang sedang aktif.
`[HASIL-BACA]`
**Lokasi kode:** `purchase_product_optional/models/purchase_order_line.py:17-56`

### BR-09 — Produk dynamic-attribute dibuat sebagai varian baru saat konfirmasi dialog
Kalau kombinasi atribut produk (utama atau optional) mengandung minimal satu attribute line dengan
`create_variant == "dynamic"` dan produk itu belum punya `id` (varian belum ada), sistem memanggil
endpoint `create_product` untuk membuat `product.product` baru dari kombinasi itu saat tombol
Confirm ditekan (`onConfirm`), SEBELUM data dikirim balik ke baris PO. `[HASIL-BACA]`
**Lokasi kode:** `purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js:537-557`,
`purchase_product_optional/controllers/main.py:94-108`
