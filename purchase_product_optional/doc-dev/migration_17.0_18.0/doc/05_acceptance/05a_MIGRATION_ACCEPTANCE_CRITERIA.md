# Migration Acceptance Criteria — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan
**Tanggal:** 2026-08-24

---

## AC-01 — Instalasi Modul

**AC-01-01** (verifies DIFF-01, DIFF-02, DIFF-03 — install blockers)
Given database 18.0 bersih dengan `purchase`, `purchase_product_matrix`, `sale` sudah ter-install
When modul `purchase_product_optional` di-install (`-i purchase_product_optional --stop-after-init`)
Then instalasi selesai tanpa `ParseError`/`AttributeError`/exception fatal apapun; modul ter-install dengan `auto_install: True` begitu ketiga dependency itu ada (BSL-012)

## AC-02 — Dialog Konfigurator Terbuka Otomatis

**AC-02-01** (verifies BSL-001)
Given form Purchase Order baru dengan vendor terisi
When user memilih `product_template_id` yang punya optional products/atribut varian di baris PO
Then dialog `ProductConfiguratorDialogPurchase` terbuka otomatis (identik 17.0)

**AC-02-02** (verifies BSL-001, DIFF-07 — kritis, hanya lolos kalau fix `useService("rpc")` benar)
Given dialog konfigurator baru dipicu terbuka (AC-02-01)
When dialog me-render dan memanggil RPC internal (`get_values_purchase`, dst.)
Then TIDAK ADA error `Service rpc is not available` di console browser — dialog berhasil menampilkan data produk

## AC-03 — Harga Per-Vendor & Currency

**AC-03-01** (verifies BSL-002)
Given produk punya `product.supplierinfo` untuk vendor yang dipilih di PO
When dialog konfigurator menghitung harga
Then harga mengikuti `product.supplierinfo` vendor tsb; fallback ke supplier pertama kalau tidak match; fallback ke `standard_price` kalau tidak ada supplierinfo — identik 17.0

**AC-03-02** (verifies BSL-003, BSL-013, BSL-018 — bug dipertahankan, BUKAN regresi baru)
Given `ir.config_parameter` "currency_id" belum pernah di-set di database
When harga dikonversi lewat `convert_price()`
Then harga dikembalikan APA ADANYA tanpa error (silent no-op) — identik F-05 di 17.0, TIDAK diperbaiki

## AC-04 — Edit Baris Terkonfigurasi

**AC-04-01** (verifies BSL-004, DIFF-05 — kritis, hanya lolos kalau rename `onEditConfiguration` benar)
Given baris PO yang sudah dikonfigurasi (`is_configurable_product=True`)
When user klik untuk mengedit baris tersebut
Then dialog `ProductConfiguratorDialogPurchase` terbuka kembali dengan data existing (custom values, no-variant values) — identik 17.0, BUKAN jatuh ke grid configurator default `purchase_product_matrix`

## AC-05 — Variant Dinamis & Konfirmasi

**AC-05-01** (verifies BSL-014)
Given produk (utama/optional) di dialog belum punya `product_id` dan atribut line-nya `create_variant == 'dynamic'`
When user klik "Confirm"
Then variant baru dibuat via RPC `create_product` sebelum baris PO ditambahkan/diupdate — identik 17.0

**AC-05-02** (verifies BSL-016)
Given kombinasi atribut termasuk `exclusions`/`parent_exclusions`/`archived_combinations`
When kombinasi itu dipilih di dialog
Then badge "not available" muncul dan tombol "Confirm" disabled — identik 17.0

## AC-06 — Server-Side Onchange (Bug Dipertahankan)

**AC-06-01** (verifies BSL-005, BSL-006 — F-02/F-03, keputusan dev: dipertahankan)
Given form PO dengan partner yang currency purchase-nya berbeda dari currency PO saat ini
When `onchange_partner_id` terpicu (ganti `currency_id`/`partner_id`)
Then `self.currency_id` TIDAK berubah (no-op literal) — identik 17.0; efek samping core Odoo (payment term/fiscal position/incoterm) TETAP tertimpa total, TIDAK diperbaiki

**AC-06-02** (verifies BSL-007)
Given `partner_id` di PO berubah
Then `id_vendor` (hidden field) ikut ter-update ke id partner baru — identik 17.0

## AC-07 — View & Tampilan

**AC-07-01** (verifies BSL-011, DIFF-01)
Given form Purchase Order dibuka
Then kolom `product_template_id` di list baris PO selalu terlihat; kolom `product_id` optional/hidden berlabel "Product Variant" — identik 17.0, tag view sudah `<list>` bukan `<tree>`

## AC-08 — Custom & No-Variant Attribute Values

**AC-08-01** (verifies BSL-008)
Given baris PO dengan `product_id` yang berubah
When compute `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values` jalan
Then value atribut yang tidak valid untuk template produk saat ini dibersihkan otomatis — identik 17.0

## AC-09 — `product_add_mode` (Bug Dipertahankan)

**AC-09-01** (verifies BSL-009 — F-01, keputusan dev: dipertahankan)
Given modul ter-install
Then field `product_add_mode` TETAP TIDAK terdaftar sebagai field ORM di `purchase.order.line` (warning registry boleh muncul, bukan error fatal) — identik 17.0, TIDAK diperbaiki

## AC-10 — Multi-Company (Bug Dipertahankan)

**AC-10-01** (verifies BSL-010 — F-07)
Given environment multi-company dengan seller info company lain
When harga optional product dihitung
Then seller dari company lain tetap ikut terhitung (tidak difilter company) — identik 17.0, TIDAK diperbaiki

## AC-11 — Label Field (Bug Dipertahankan)

**AC-11-01** (verifies BSL-017 — F-08)
Given modul ter-install
Then field `id_vendor` tetap tidak punya `string=` eksplisit, label "ID" berpotensi bentrok dengan field `id` bawaan (visual tetap hidden via CSS) — identik 17.0, TIDAK diperbaiki
