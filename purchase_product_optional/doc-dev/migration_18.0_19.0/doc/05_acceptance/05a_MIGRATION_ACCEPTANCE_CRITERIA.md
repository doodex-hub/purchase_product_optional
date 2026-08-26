# Migration Acceptance Criteria — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan — **bukan** `03_spec/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-26

> Format Given/When/Then, diturunkan dari `01b_BASELINE_SPEC.md`. Kesetaraan diukur terhadap 18.0.

---

## AC-01 — Instalasi Modul

**AC-01-01** (verifies §Critical Migration Blockers `03_MIGRATION_SPEC.md`)
Given database 19.0 bersih dengan `purchase`, `purchase_product_matrix`, `sale` sudah ter-install
When modul `purchase_product_optional` di-install (`-i purchase_product_optional --stop-after-init`)
Then instalasi selesai tanpa `ParseError`/`AttributeError`/exception fatal apapun; modul ter-install dengan `auto_install: True` begitu ketiga dependency itu ada (BSL-012); manifest version `19.0.1.0.0`

## AC-02 — Dialog Konfigurator Terbuka Otomatis (AREA RISIKO TERTINGGI — DIFF-01/DIFF-02)

**AC-02-01** (verifies BSL-001, DIFF-01 — kritis, hanya lolos kalau rewrite format many2one benar)
Given form Purchase Order baru dengan vendor terisi
When user memilih `product_template_id` yang punya optional products/atribut varian di baris PO
Then dialog `ProductConfiguratorDialogPurchase` terbuka otomatis — identik 18.0; TIDAK ADA error JS di
console akibat baca `record.data.product_template_id[0]` (harus `.id`, format objek 19.0)

**AC-02-02** (verifies DIFF-02 — kritis, jalur fallback non-configurator)
Given `get_single_product_variant()` mengembalikan `result.mode` selain `'configurator'` (jalur jarang
tereksekusi produksi per CAND-07, tapi tetap wajib benar)
When `_onProductTemplateUpdate` mengeksekusi fallback `this._openGridConfigurator()`
Then TIDAK throw `TypeError` — method sudah diganti `this.matrixConfigurator.open(record, false)`
mengikuti pola native 19.0

**AC-02-03** (verifies BSL-001, dialog RPC)
Given dialog konfigurator baru dipicu terbuka (AC-02-01)
When dialog me-render dan memanggil RPC internal (`get_values_purchase`, dst.)
Then TIDAK ADA error RPC di console browser — dialog berhasil menampilkan data produk (fungsi ini
sudah sehat sejak migrasi 17→18, verifikasi ulang murni regresi check)

## AC-03 — Harga Per-Vendor & Currency

**AC-03-01** (verifies BSL-002)
Given produk punya `product.supplierinfo` untuk vendor yang dipilih di PO
When dialog konfigurator menghitung harga
Then harga mengikuti `product.supplierinfo` vendor tsb; fallback ke supplier pertama kalau tidak match; fallback ke `standard_price` kalau tidak ada supplierinfo — identik 18.0

**AC-03-02** (verifies BSL-003, BSL-013, BSL-018 — bug dipertahankan, BUKAN regresi baru, dikonfirmasi dev)
Given `ir.config_parameter` "currency_id" belum pernah di-set di database
When harga dikonversi lewat `convert_price()`
Then harga dikembalikan APA ADANYA tanpa error (silent no-op) — identik 18.0, TIDAK diperbaiki (keputusan dev, lihat "Ringkasan untuk Review" `01a_MIGRATION_INTAKE.md`)

## AC-04 — Edit Baris Terkonfigurasi

**AC-04-01** (verifies BSL-004)
Given baris PO yang sudah dikonfigurasi (`is_configurable_product=True`)
When user klik untuk mengedit baris tersebut
Then dialog `ProductConfiguratorDialogPurchase` terbuka kembali dengan data existing (custom values, no-variant values) — identik 18.0, BUKAN jatuh ke grid configurator default `purchase_product_matrix`

## AC-05 — Variant Dinamis & Konfirmasi

**AC-05-01** (verifies BSL-014, DIFF-01 — write field `product_id` format objek)
Given produk (utama/optional) di dialog belum punya `product_id` dan atribut line-nya `create_variant == 'dynamic'`
When user klik "Confirm"
Then variant baru dibuat via RPC `create_product` sebelum baris PO ditambahkan/diupdate; `record.update({product_id: {id, display_name}})` — bukan tuple `[id, name]` — identik behavior 18.0, beda format data

**AC-05-02** (verifies BSL-016)
Given kombinasi atribut termasuk `exclusions`/`parent_exclusions`/`archived_combinations`
When kombinasi itu dipilih di dialog
Then badge "not available" muncul dan tombol "Confirm" disabled — identik 18.0

## AC-06 — Server-Side Onchange (Bug Dipertahankan, dikonfirmasi dev)

**AC-06-01** (verifies BSL-005, BSL-006, DIFF-05 — keputusan dev: dipertahankan)
Given form PO dengan partner yang currency purchase-nya berbeda dari currency PO saat ini
When `onchange_partner_id` terpicu (ganti `currency_id`/`partner_id`)
Then `self.currency_id` TIDAK berubah (no-op literal) — identik 18.0; efek samping core Odoo (payment term/fiscal position/incoterm) TETAP tertimpa total (core method masih ada nama sama di 19.0, DIFF-05), TIDAK diperbaiki

**AC-06-02** (verifies BSL-007)
Given `partner_id` di PO berubah
Then `id_vendor` (hidden field) ikut ter-update ke id partner baru — identik 18.0

**AC-06-03** (verifies CAND-08 `SUMMARY.md` 17_18 — pola dua dialog, keputusan dev: dipertahankan)
Given modul men-patch `_onProductTemplateUpdate`/`onEditConfiguration` dan memanggil `super()` tanpa syarat kondisional koordinasi
When kondisi memicu baik dialog matrix (`purchase_product_matrix`) maupun dialog Product Configurator custom
Then perilaku "berpotensi dua dialog terbuka tanpa koordinasi" TETAP ada — identik 18.0, TIDAK diperbaiki (keputusan dev eksplisit)

## AC-07 — View & Tampilan

**AC-07-01** (verifies BSL-011)
Given form Purchase Order dibuka
Then kolom `product_template_id` di list baris PO selalu terlihat; kolom `product_id` optional/hidden berlabel "Product Variant" — identik 18.0

## AC-08 — Custom & No-Variant Attribute Values

**AC-08-01** (verifies BSL-008)
Given baris PO dengan `product_id` yang berubah
When compute `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values` jalan
Then value atribut yang tidak valid untuk template produk saat ini dibersihkan otomatis — identik 18.0

## AC-09 — `product_add_mode` (Bug Dipertahankan)

**AC-09-01** (verifies BSL-009)
Given modul ter-install
Then field `product_add_mode` TETAP TIDAK terdaftar sebagai field ORM di `purchase.order.line` (warning registry boleh muncul, bukan error fatal) — identik 18.0, TIDAK diperbaiki

## AC-10 — Multi-Company (Bug Dipertahankan)

**AC-10-01** (verifies BSL-010)
Given environment multi-company dengan seller info company lain
When harga optional product dihitung
Then seller dari company lain tetap ikut terhitung (tidak difilter company) — identik 18.0, TIDAK diperbaiki

## AC-11 — Label Field (Bug Dipertahankan)

**AC-11-01** (verifies BSL-017)
Given modul ter-install
Then field `id_vendor` tetap punya `string='ID'` eksplisit, label "ID" berpotensi bentrok dengan field `id` bawaan (visual tetap hidden via CSS) — identik 18.0, TIDAK diperbaiki
