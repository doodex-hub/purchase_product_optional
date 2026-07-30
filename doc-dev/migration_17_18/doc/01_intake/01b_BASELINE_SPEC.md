# Baseline Spec — purchase_product_optional

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 17.0 — bukan bagaimana diimplementasikan.
**Tanggal:** 2026-07-29
**Sumber:** Direkonsiliasi dari `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` +
`doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md` + `doc-dev/backfill/FINDINGS.md` (hasil project
BACKFILL retroaktif 2026-07-28, sudah divalidasi eksekusi nyata) + cross-check langsung ke kode
17.0 di `source-codebase` (`models/`, `controllers/main.py`, 6 file JS + template, `views/purchase_order_views.xml`).

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) —
> BUKAN `03_MIGRATION_SPEC.md`.

---

## Provenance Tag (WAJIB per klaim)

Format: `[BSL-NNN] [TAG] (ref: BR-XX, AC-XX-XX)`. Lihat `templates/01b_BASELINE_SPEC.md` untuk arti
`[MATCH]`/`[GAP]`/`[NO-SPEC]`. **Hasil cross-check untuk modul ini: seluruh klaim di
`01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md` COCOK dengan kode aktual** (dibaca langsung,
baris per baris, semua file Python/JS/XML modul) — tidak ditemukan satupun penyimpangan. Karena itu
seluruh `BSL-NNN` di bawah bertag `[MATCH]`, kecuali disebutkan lain.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

> Tally provenance: **32 klaim, semua `[MATCH]`, 0 `[GAP]`, 0 `[NO-SPEC]`.**

1. **`[BSL-020]` F-06 (Tinggi)** — dialog "Configure your product" (custom) dan grid "Choose Product
   Variants" (`purchase_product_matrix`) bisa terbuka BERTUMPUK tanpa koordinasi. Kalau user hanya
   berinteraksi dengan dialog depan, baris produk UTAMA hilang total dari PO tanpa error. Ini bug
   fungsional nyata (dikonfirmasi live 2×), WAJIB dipertahankan identik di 18.0 (bukan diperbaiki).
2. **`[BSL-016]` F-03 (Tinggi)** — `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL (bukan
   per-record), dibaca balik oleh `convert_price` — rawan race condition di lingkungan multi-user.
3. **`[BSL-010]` F-02 (Sedang)** — `onchange_partner_id` (docstring: "update currency based on
   partner") tidak pernah benar-benar mengubah `currency_id` di ketiga cabang if/elif/else — kandidat
   bug logic terbalik. Dipertahankan sesuai source of truth.
4. **`[BSL-024]` F-04 (Sedang)** — harga per-vendor dialog membaca DOM langsung
   (`document.getElementById('id_vendor_0')`), bukan parameter eksplisit — rapuh terhadap perubahan
   konvensi id Odoo. **Perlu perhatian ekstra di step 6/9** — kalau 18.0 mengubah skema id generation
   DOM, pola ini bisa silently break (fallback ke supplier pertama, bukan crash).
5. **`[BSL-008]` F-01 (Rendah)** — field `product_add_mode` di `purchase.order.line` tidak pernah
   benar-benar terdaftar (bug parenthesis) — dampak fungsional saat ini nol (tidak dipakai di manapun),
   tapi dipertahankan (TIDAK diperbaiki "sekalian" saat migrasi).
6. **`[BSL-018]` F-05 sudah TERBUKTI TIDAK crash** (`_convert()` tanpa `company`/`date` jalan normal di
   versi Odoo 17.0 yang dites) — **perlu diverifikasi ulang di 18.0** karena signature `_convert()` core
   Odoo bisa saja berubah antar versi (ini bagian dari scope step 2/9, bukan diasumsikan otomatis sama).
7. Semua 6 finding di atas TIDAK butuh keputusan baru sekarang — sudah dikonfirmasi via eksekusi nyata
   di project BACKFILL, murni diwariskan sebagai baseline yang harus identik pasca migrasi.

---

## 1. Tujuan Modul

Modul ini menambahkan **Product Configurator** (dialog pemilihan atribut produk + optional products,
konsepnya dipinjam dari `sale_product_configurator`/`purchase_product_matrix`) ke form Purchase Order
— memungkinkan staff purchasing memilih varian/atribut produk dan produk opsional terkait langsung
dari baris PO, alih-alih hanya memilih varian produk jadi lewat dropdown biasa. Modul juga menghitung
harga produk berdasarkan vendor yang dipilih pada PO (bukan cuma harga standar), dan mengurus konversi
mata uang antara mata uang produk dan mata uang PO. `[MATCH]` (ref: Latar Belakang & Tujuan,
`01A_FUNCTIONAL_SPEC.md`)

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `purchase.order` (`_inherit`) | + field `id_vendor` (Char, disimpan dari `partner_id.id`); onchange currency (BR-02, tidak benar-benar berfungsi — lihat §8) |
| `purchase.order.line` (`_inherit`) | + `product_custom_attribute_value_ids` (One2many, compute, sync ke produk aktif); + `product_no_variant_attribute_value_ids` (Many2many, compute — definisi rusak, lihat §8 F-01); onchange currency dari partner (kelas `PurchaseOrder` kedua di file yang sama, method `onchange_id_vendor`) |
| `product.template` (`_inherit`) | + method `convert_price(price, from_currency)` — konversi currency berdasar `ir.config_parameter['currency_id']` |
| `product.attribute.custom.value` (`_inherit`) | + field `purchase_order_line_id` (Many2one, `ondelete='cascade'`) — link custom attribute value ke baris PO asalnya |

## 3. Field dengan Makna Bisnis

### `purchase.order`
- **Identitas:** `id_vendor` (Char) — menyimpan `partner_id.id` sebagai string, diupdate via onchange `partner_id`. Dipakai HANYA sebagai jembatan ke JS lewat DOM (lihat §8 F-04), bukan dipakai langsung di Python manapun selain assignment-nya sendiri.

### `purchase.order.line`
- **Struktur:** `product_custom_attribute_value_ids` (One2many ke `product.attribute.custom.value`, `store=True, readonly=False, precompute=True, copy=True`) — custom value per baris PO, dibersihkan otomatis kalau tidak valid untuk produk saat ini.
- **Struktur:** `product_no_variant_attribute_value_ids` (Many2many ke `product.template.attribute.value`) — extra-price attribute (no-variant) untuk baris ini. **Catatan desain:** definisi field ini secara sintaks menyertakan `product_add_mode=...` sebagai keyword-argument ke constructor `Many2many()` — lihat §8 `[BSL-008]`.

### `product.attribute.custom.value`
- **Struktur:** `purchase_order_line_id` (Many2one ke `purchase.order.line`, `ondelete='cascade'`) — link balik ke baris PO pemilik custom value ini.

## 4. Business Workflow / State Transition

### Trigger Dialog Configurator (BR-01)

- `[BSL-001]` `[MATCH]` (ref: BR-01, AC-01-01) Saat `product_template_id` pada baris PO diubah
  (`_onProductTemplateUpdate` di `purchase_product_field.js`), sistem memanggil
  `product.template.get_single_product_variant` (method dari `sale_product_configurator`, tidak
  didefinisikan di modul ini) untuk menentukan langkah selanjutnya.
- `[BSL-002]` `[MATCH]` (ref: BR-01, AC-01-01) Given produk punya optional products
  (`has_optional_products=true`) dan belum ada `result.product_id` — dialog
  `ProductConfiguratorDialogPurchase` terbuka via `_openProductConfigurator()`, TANPA langsung
  meng-update `product_id` baris PO.
- `[BSL-003]` `[MATCH]` (ref: BR-01, AC-01-02) Given produk punya tepat SATU varian
  (`result.product_id` ada), `product_id` saat ini berbeda dari varian itu, DAN produk TIDAK punya
  optional products — baris PO langsung di-update ke varian tunggal itu, dialog TIDAK dibuka.
- `[BSL-004]` `[MATCH]` (ref: BR-01, AC-01-03) Given `purchase_warning` bertipe `block` —
  `WarningDialog` ditampilkan (title+message dari warning), `product_template_id` baris di-reset ke
  `false`, proses pemilihan produk dibatalkan.
- `[BSL-005]` `[MATCH]` (ref: BR-01, AC-01-04) Given `purchase_warning` bertipe `warning` (bukan
  `block`) — notifikasi non-blocking ditampilkan, TAPI alur tetap lanjut ke pengecekan `result.mode`.
- `[BSL-006]` `[MATCH]` (ref: BR-01, AC-01-05) Given tidak ada `product_id`/`purchase_warning`, dan
  `result.mode` kosong atau `'configurator'` — dialog Product Configurator dibuka (default).
- `[BSL-007]` `[MATCH]` (ref: BR-01, AC-01-06) Given `result.mode` bernilai selain `'configurator'`
  (mis. `'matrix'`) — `_openGridConfigurator()` dipanggil (grid/matrix dari `purchase_product_matrix`),
  BUKAN dialog Product Configurator modul ini.
- `[BSL-008]` `[MATCH]` (ref: BR-04, AC-04-01/02) Field `product_add_mode` yang DIMAKSUDKAN sebagai
  related field di `purchase.order.line` **tidak pernah benar-benar terdaftar** (kurung `Many2many()`
  tidak ditutup sebelum baris berikutnya) — secara sintaks Python valid (tidak ada `SyntaxError` saat
  load), tapi field ini tidak ada di `_fields`, memanggilnya (`line.product_add_mode`) akan
  menghasilkan error "field does not exist". Tidak dipakai di tempat lain manapun di modul (digrep
  Python/XML/JS: 0 pemakaian). **Bug ini terkait langsung ke `[BSL-020]` (F-06)** — field ini
  kemungkinan dimaksudkan untuk memberi tahu `purchase_product_matrix` agar skip grid dialog-nya
  sendiri, tapi karena rusak (dan tidak pernah dibaca dari manapun oleh JS modul ini), kedua dialog
  selalu berpotensi tumpang tindih.
- `[BSL-009]` `[MATCH]` (ref: US-03) Membuka kembali baris PO yang produknya sudah dikonfigurasi
  memicu `_editProductConfiguration()` — dialog terbuka kembali dengan kombinasi atribut & custom
  value yang sudah tersimpan (`edit=true`), bukan mulai dari kosong.

### Update Currency Berdasarkan Partner (BR-02, kandidat bug — TIDAK berfungsi seperti docstring)

- `[BSL-010]` `[MATCH]` (ref: BR-02, AC-02-01) Given PO baru tanpa `partner_id` terisi — `currency_id`
  TIDAK disentuh sama sekali; hanya nilai `currency_id` yang SUDAH ada yang ditulis ke
  `ir.config_parameter['currency_id']`.
- `[BSL-011]` `[MATCH]` (ref: BR-02, AC-02-02) Given `partner_id.property_purchase_currency_id`
  KEBETULAN SUDAH SAMA dengan `currency_id` PO — assignment terjadi tapi ke nilai yang sama (no-op
  secara observable), lalu ditulis ke config parameter.
- `[BSL-012]` `[MATCH]` (ref: BR-02, AC-02-03) Given `partner_id.property_purchase_currency_id`
  BERBEDA dari `currency_id` PO (kasus yang menurut docstring seharusnya memicu auto-update) —
  `currency_id` PO **TETAP TIDAK BERUBAH** (`self.currency_id = self.currency_id`, literal
  self-assignment). Ini bertentangan dengan docstring method ("Update currency based on the partner's
  purchase currency") — kandidat bug logic if/elif/else tertukar. **Dipertahankan identik di 18.0,
  TIDAK diperbaiki.**

## 5. Server-Side Logic dengan Side Effect

### Harga Berdasarkan Supplier Info Vendor (BR-05)

- `[BSL-013]` `[MATCH]` (ref: BR-05, AC-05-01) Given produk punya `product.supplierinfo` dengan
  `partner_id` cocok dengan `id_vendor` PO — harga & currency dari supplierinfo itu dipakai, dikonversi
  ke currency PO lewat `convert_price`.
- `[BSL-014]` `[MATCH]` (ref: BR-05, AC-05-02) Given produk punya supplierinfo tapi TIDAK ADA yang
  cocok dengan `id_vendor` — fallback ke supplierinfo PERTAMA dalam list (`[0]`), BUKAN
  `standard_price`, meskipun vendor tidak match.
- `[BSL-015]` `[MATCH]` (ref: BR-05, AC-05-03) Given produk sama sekali tidak punya supplierinfo —
  fallback ke `standard_price` produk, dikonversi dari currency produk ke currency PO.

### Konversi Currency via Global Config Parameter (BR-03, risiko race condition)

- `[BSL-016]` `[MATCH]` (ref: BR-03, AC-03-01/02) `convert_price(price, from_currency)`: kalau
  `from_currency.id` == currency yang tersimpan di `ir.config_parameter['currency_id']` — return harga
  apa adanya (short-circuit, tanpa konversi). Kalau beda — konversi lewat `res.currency._convert()` ke
  currency yang tersimpan di parameter GLOBAL itu, **bukan ke currency PO milik user yang memanggil**
  kalau parameter itu sempat ditimpa onchange PO user LAIN di antara waktu `onchange_partner_id`
  terakhir jalan dan `convert_price` dipanggil. `ir.config_parameter` adalah singleton system-wide
  (satu baris per key, dipakai bersama SELURUH user/record) — mekanisme ini SECARA DESAIN rentan race
  condition di lingkungan multi-user (frekuensi kejadian nyata butuh instrumentasi produksi untuk
  dipastikan, tidak bisa dipastikan dari baca kode/test transaksi tunggal saja).
- `[BSL-017]` `[MATCH]` (ref: BR-03) `onchange_partner_id` (§4 `[BSL-010]`..`[BSL-012]`) adalah SATU-
  SATUNYA penulis parameter global `'currency_id'` ini — jadi bug BR-02 dan risiko BR-03 saling
  terkait: parameter global itu HAMPIR SELALU berisi currency PO yang sedang aktif (karena
  `onchange_partner_id` selalu menulis `self.currency_id.id` di ketiga cabangnya, meski tidak pernah
  benar-benar mengubahnya), tapi tetap rentan ditimpa proses concurrent lain.
- `[BSL-018]` `[MATCH]` (ref: BR-03, AC-03-03) `_convert()` dipanggil TANPA argumen `company`/`date`
  (`from_currency._convert(from_amount=price, to_currency=to_currency)`) — signature upstream Odoo
  17.0 resmi punya parameter `company`/`date` sebagai wajib tanpa default. **Dikonfirmasi via eksekusi
  nyata (Mode B, run #1/#2/#7, 2026-07-28): method ini TIDAK crash** pada versi Odoo 17.0 yang dites
  (build `17.0-20260630`) — kemungkinan versi tersebut punya default value untuk kedua argumen itu.
  **Perlu diverifikasi ulang khusus di 18.0** (step 9) — signature `_convert()` core Odoo bisa berbeda
  antar versi, tidak boleh diasumsikan otomatis identik hanya karena 17.0 terbukti aman.

### Optional Products Rekursif (BR-07)

- `[BSL-019]` `[MATCH]` (ref: BR-07, AC-07-01, AC-07-02) Saat produk optional ditambahkan
  (`_addProduct`), optional products lanjutannya (nested) diambil via `_getOptionalProducts`, termasuk
  exclusion rules (`_get_attribute_exclusions`) berdasarkan kombinasi atribut produk utama & parent.
  Produk optional dengan >1 parent HANYA dihapus dari state kalau SEMUA parent-nya sudah dihapus
  (`parent_product_tmpl_ids` jadi kosong) — bukan langsung ikut terhapus begitu satu parent dihapus.

### Dialog Configurator vs Grid Configurator — Tumpang Tindih Tanpa Koordinasi (terkait BR-01, F-06)

- `[BSL-020]` `[MATCH]` (ref: BR-01, terkait `[BSL-008]`) `_onProductTemplateUpdate` di
  `purchase_product_field.js` memanggil `super._onProductTemplateUpdate(...)` TANPA SYARAT di baris
  pertama override (baris 56) — method induk ini (dari `purchase_product_matrix`) berpotensi membuka
  grid dialog "Choose Product Variants" SENDIRI, independen dari keputusan override modul ini untuk
  membuka dialog custom "Configure your product". **Dikonfirmasi live (AI-Browser, 2026-07-28,
  direproduksi 2×)**: untuk produk yang SEKALIGUS matrix-eligible (`purchase_product_matrix`) DAN
  punya optional products (modul ini), KEDUA dialog terbuka bertumpuk (grid di belakang, configurator
  di depan). Kalau user hanya berinteraksi dengan dialog depan (Confirm tanpa sadar ada grid di
  belakang) — **baris produk UTAMA hilang total dari PO, tanpa error/warning apapun** (state
  tersimpan ditentukan oleh grid, bukan oleh `save()` callback configurator). Kalau user
  men-Confirm grid dulu (qty>0) baru configurator — kedua baris tersimpan benar. **Bug fungsional
  bernilai TINGGI — WAJIB dipertahankan identik (direproduksi, bukan diperbaiki) di 18.0.** Field
  `product_add_mode` (`[BSL-008]`) tampak dimaksudkan untuk mencegah ini (memberi tahu parent class
  untuk skip grid), tapi rusak DAN tidak pernah dibaca oleh JS manapun di modul ini.

### Sinkronisasi Custom/No-Variant Attribute Value (BR-08)

- `[BSL-021]` `[MATCH]` (ref: BR-08, AC-08-01) `_compute_custom_attribute_values`: saat `product_id`
  baris diganti, value custom attribute yang TIDAK termasuk
  `valid_product_template_attribute_line_ids` produk BARU dihapus dari
  `product_custom_attribute_value_ids` — value lama tidak ikut terbawa ke produk baru.
- `[BSL-022]` `[MATCH]` (ref: BR-08, AC-08-02) Analog untuk `product_no_variant_attribute_value_ids`
  lewat `_compute_no_variant_attribute_values`, membandingkan `ptav._origin` terhadap
  `valid_product_template_attribute_line_ids.product_template_value_ids` produk baru.

### Pembuatan Varian Dynamic Saat Konfirmasi (BR-09)

- `[BSL-023]` `[MATCH]` (ref: BR-09, AC-09-01, AC-09-02) Kalau produk (utama/optional) di dialog belum
  punya `id` DAN kombinasi atributnya mengandung minimal satu PTAL dengan `create_variant ==
  "dynamic"` — endpoint `create_product` dipanggil untuk membuat `product.product` baru SEBELUM
  `props.save(...)` dipanggil. Kalau ada produk dengan kombinasi TIDAK valid (`isPossibleConfiguration()`
  false) — `onConfirm()` langsung `return` di awal, TIDAK ada yang disimpan/dibuat, dialog TETAP
  terbuka (tidak close).

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend — Komponen Owl (5, semua ES6 `class extends Component`, `@odoo-module`, sudah gaya Owl 2 — lihat catatan Owl/JS di `migration-records/`)

- **`ProductConfiguratorDialogPurchase`** (`product_configurator_dialog/product_configurator_dialog.js`,
  567 baris) — komponen dialog utama. State: `products`/`optionalProducts`. Env: `addProduct`,
  `removeProduct`, `setQuantity`, `updateProductTemplateSelectedPTAV`, `updatePTAVCustomValue`,
  `isPossibleCombination`. Membaca harga per-vendor via `get_supplierinfo_id()`/
  `get_product_update_price()`/`get_optional_product_prices()` (lihat `[BSL-013]`..`[BSL-015]`, F-04
  `[BSL-024]`).
- **`ProductList`** (`product_list/product_list.js`) — tabel daftar produk (utama atau optional),
  hitung total harga.
- **`Product`** (`product/product.js`) — baris satu produk: quantity +/-, harga terformat, tombol
  remove (non-optional) / add (optional).
- **`ProductTemplateAttributeLine`** (`product_template_attribute_line/product_template_attribute_line.js`)
  — render 5 varian tampilan attribute line (`color`/`multi`/`pills`/`radio`/`select`), custom value
  input.
- **`BadgeExtraPrice`** (`badge_extra_price/badge_extra_price.js`) — badge kecil `+`/`-` harga extra
  attribute value.

### Patch — `PurchaseOrderLineProductField` (`purchase_product_field.js`, 154 baris)
Patch (bukan inherit/extend Owl) terhadap komponen `purchase_product_matrix`. Override
`_onProductTemplateUpdate`, `_editProductConfiguration`, tambah `_openProductConfigurator` (lihat
`[BSL-001]`..`[BSL-009]`, `[BSL-020]`).

### RPC Route (`controllers/main.py`, 342 baris, semua `type='json', auth='user'`, internal-only —
dikonsumsi HANYA JS modul sendiri, dikonfirmasi tidak ada konsumen eksternal)
- `/purchase_product_optional/get_values_purchase` — data produk utama + optional products lengkap
  (attribute lines, exclusions, harga).
- `/purchase_product_optional/create_product` — buat `product.product` baru dari kombinasi dynamic.
- `/purchase_product_optional/update_combination` — info produk ter-update setelah ganti kombinasi.
- `/purchase_product_optional/get_optional_products` — optional products untuk kombinasi tertentu.

### View (`views/purchase_order_views.xml`, 40 baris)
Extend form PO (`purchase.purchase_order_form`): kolom `product_template_id` dipaksa selalu terlihat
(`column_invisible="0"`), tambah field tersembunyi (`product_template_attribute_value_ids`,
`product_custom_attribute_value_ids` dengan inner `<tree>`, `product_no_variant_attribute_value_ids`,
`is_configurable_product`), kolom `product_id` disembunyikan default + label ulang "Product Variant",
field `id_vendor` disisipkan setelah `currency_id` dengan CSS `visibility: hidden` (lihat F-04
`[BSL-024]`). **Catatan migrasi (bukan behavior, murni tipe view):** pakai `<tree>` — install-breaking
di 18.0, wajib `<tree>`→`<list>` di step 6 Fase A2 (perubahan mekanis, tidak mengubah field/atribut
apapun di dalamnya).

## 7. Dependency Eksternal

### Eksplisit (manifest)
`depends: ['purchase', 'purchase_product_matrix', 'sale_product_configurator']`, `auto_install: True`.

### Implisit/Inferred
Tidak ditemukan — digrep seluruh modul untuk pola `'x' in self.env`/import model lain di luar
manifest: nihil. Semua model yang dipakai (`product.template`, `product.supplierinfo`,
`res.currency`, `ir.config_parameter`, `uom.uom`, `product.pricelist`,
`product.template.attribute.value`, dll) berasal dari `purchase`/`product`/`base` (core, sudah
implisit lewat `purchase`) atau dari `purchase_product_matrix`/`sale_product_configurator` (dideklarasikan).

## 8. Quirk / Behavior Non-Obvious

> Lanjutan `[BSL-024]`..`[BSL-025]` — 6 finding F-01..F-06 dari `doc-dev/backfill/FINDINGS.md`,
> semuanya `[MATCH]` (spec BACKFILL cocok kode aktual), SEMUA WAJIB dipertahankan identik di 18.0.

- `[BSL-024]` `[MATCH]` (ref: F-04, AC-06-01, AC-06-02) **Harga per-vendor bergantung pada
  `document.getElementById('id_vendor_0')`.** Dialog membaca DOM langsung untuk tahu vendor PO,
  bukan lewat props/RPC eksplisit seperti data lain (currency, company, pricelist). Field `id_vendor`
  disembunyikan lewat CSS `visibility: hidden` (bukan mekanisme `invisible` Odoo), dipertahankan di
  DOM supaya bisa dibaca `getElementById`. **Risiko migrasi konkret:** kalau 18.0 mengubah skema id
  generation DOM Odoo, `getElementById('id_vendor_0')` bisa return `null` →
  `Cannot read properties of null` saat `.value` diakses — dialog gagal terbuka sama sekali (AC-06-02,
  belum pernah diverifikasi terjadi di 17.0, TAPI wajib dicek ulang di 18.0 step 9 karena ini
  persis jenis perubahan yang bisa dipicu upgrade versi).
- `[BSL-025]` `[MATCH]` (ref: F-06 — sudah didetailkan penuh di `[BSL-020]` §5, direferensikan ulang di
  sini karena termasuk quirk paling berisiko) Dua dialog independen tanpa koordinasi — lihat `[BSL-020]`.
- `[BSL-026]` `[MATCH]` (ref: F-01 — sudah didetailkan penuh di `[BSL-008]` §4, direferensikan ulang di
  sini) Field `product_add_mode` tidak pernah terdaftar.
- `[BSL-027]` `[MATCH]` (ref: F-02/F-03 — sudah didetailkan penuh di `[BSL-010]`..`[BSL-012]`,
  `[BSL-016]`..`[BSL-017]` §4/§5) Bug currency onchange + risiko race condition config parameter global.
- `[BSL-028]` `[MATCH]` (ref: 3 leftover `console.log` debug, dicatat `FINDINGS.md` F-06 "Catatan
  tambahan") `purchase_product_field.js:137` (`console.log('Main Product Quantity:', ...)`),
  `purchase_product_field.js:147` (`console.log('tes')`),
  `product_configurator_dialog.js:531` (`console.log("Checking configuration:", ...)`) — tidak
  berdampak fungsional, indikasi kode belum dibersihkan dari debugging. **Dipertahankan apa adanya**
  (bukan cleanup — prinsip "tidak ada cleanup dini" `06a_CODE_MIGRATION_PHASES.md` P3), kecuali user
  eksplisit minta dihapus sebagai perubahan disengaja.

---

## Cara Pakai (ringkasan, detail lengkap di `templates/01b_BASELINE_SPEC.md`)

ID `BSL-NNN` di atas dipakai sebagai rujukan wajib oleh `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (step
5) dan `03_MIGRATION_SPEC.md` (step 3, untuk item risiko yang terkait behavior spesifik). Total 28
klaim diskrit (`BSL-001`..`BSL-028`), semua `[MATCH]` terhadap `doc-dev/backfill/spec/`. Jangan
mengubah/memakai ulang ID yang sudah ada untuk klaim lain.
