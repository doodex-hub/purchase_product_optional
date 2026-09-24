# Migration Acceptance Criteria — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 19.0 (`migration/19.0`) — **bukan** `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-24

> Given/When/Then; kesetaraan diukur terhadap 19.0. Tanda ⚠️ = area risiko tinggi `03_MIGRATION_SPEC.md` §2b.

---

## AC-01 — Instalasi

**AC-01-01** ⚠️ (verifies BSL-012, BSL-009, BSL-023)
Given DB 20.0 bersih tanpa demo dengan `purchase`, `purchase_product_matrix`, `sale`
When `-i purchase_product_optional`
Then install tanpa ParseError/exception; satu-satunya warning milik modul = `unknown parameter
'product_add_mode'` (identik 19.0); manifest `20.0.1.0.0`.

## AC-02 — Dialog Configurator (buka otomatis)

**AC-02-01** ⚠️ (verifies BSL-001, BSL-024)
Given form PO baru dengan vendor
When user memilih `product_template_id` yang punya optional products
Then dialog berjudul "Configure your product" terbuka, menampilkan produk utama dan section "Add
optional products"; tanpa error JS.

**AC-02-02** (verifies BSL-001, BSL-021)
Given produk sederhana TANPA optional products
When dipilih di baris PO
Then tidak ada dialog modul; `product_id` terisi variant tunggal.

**AC-02-03** ⚠️ (verifies BSL-026, BSL-016, BSL-020)
Given template dengan/ tanpa atribut dan optional products (termasuk optional yang punya atribut)
When route `get_values_purchase`, `get_optional_products`, `update_combination`, `create_product` dipanggil
Then tidak ada error RPC; payload berisi `exclusions`, `archived_combinations`, `parent_exclusions`
(di 20.0 selalu `{}` — MF-03), `attribute_lines`, `price = standard_price`.

## AC-03 — Harga per-vendor & currency

**AC-03-01** (verifies BSL-002, BSL-003, BSL-010)
Given supplierinfo untuk vendor PO
Then harga dialog = harga supplierinfo vendor itu (fallback supplier pertama, lalu `standard_price`),
dikonversi `convert_price` — identik 19.0.

**AC-03-02** ⚠️ (verifies BSL-013, BSL-018, BSL-019)
Given param `currency_id` = currency company / currency lain / tidak di-set
When `convert_price(price, from)`
Then sama: harga apa adanya / dikonversi / tidak raise.

## AC-04 — Edit ulang baris

**AC-04-01** (verifies BSL-004)
Given baris PO configurable tersimpan
When tombol edit konfigurasi diklik
Then dialog modul terbuka `edit=true` dengan nilai existing; Cancel hanya menutup (baris tidak dihapus).

## AC-05 — Konfirmasi, variant dinamis, eksklusi

**AC-05-01** ⚠️ (verifies BSL-014, BSL-026)
Given template `create_variant='dynamic'` tanpa variant
When Confirm / route `create_product`
Then variant dibuat; baris PO memakai variant itu.

**AC-05-02** (verifies BSL-016)
Given nilai atribut yang saling mengecualikan dalam satu template (`excluded_value_ids` di 20.0)
Then nilai ditandai tidak tersedia, Confirm disabled — identik 19.0 (untuk eksklusi dalam template).

**AC-05-03** ⚠️ (verifies BSL-024, BSL-027, BSL-028)
Given dialog terbuka, optional product ditambahkan
When Confirm
Then baris utama terisi produk & qty, optional product jadi baris baru di bawah (`readonly`); PO bisa
disimpan.

## AC-06 — Onchange server-side (quirk dipertahankan)

**AC-06-01** ⚠️ (verifies BSL-005, BSL-006, BSL-019)
Given partner dengan purchase currency berbeda dari currency PO
When `onchange_partner_id`
Then currency PO TIDAK berubah; param `currency_id` = currency PO; efek core (fiscal position dll)
tetap tertimpa (MRO: class modul yang mendefinisikan method paling depan, tanpa `super()`).

**AC-06-02** (verifies BSL-007) `id_vendor` = id partner setelah onchange.

## AC-07 — View

**AC-07-01** ⚠️ (verifies BSL-011, BSL-023)
Given form PO
Then `product_template_id` terlihat (`column_invisible=0`), `product_id` `optional=hide` berlabel
"Product Variant"; field tersembunyi modul ada di arch tapi tidak terlihat; `id_vendor` ada dengan class
`id_vendor`.

## AC-08 — Compute atribut

**AC-08-01** (verifies BSL-008) Nilai custom/no-variant tidak valid dibersihkan saat produk berubah;
kosong saat tanpa produk.

## AC-09 — Quirk lain dipertahankan

**AC-09-01** (verifies BSL-009) `product_add_mode` bukan field ORM.
**AC-09-02** (verifies BSL-017) `id_vendor.string == 'ID'`.
