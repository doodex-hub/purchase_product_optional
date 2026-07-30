# Migration Acceptance Criteria — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan — **bukan** `03_spec/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-07-29

> Format Given/When/Then, diturunkan dari `01b_BASELINE_SPEC.md` (BSL-001..BSL-028) — yang
> sendirinya direkonsiliasi dari `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md` (AC-01..AC-09,
> hasil eksekusi nyata BACKFILL). Dokumen ini **mewarisi** AC-01..AC-09 apa adanya (kesetaraan
> diukur terhadap 17.0, bukan terhadap rencana migrasi), lalu menambah **AC-10** untuk F-06 (bug
> dialog tumpang tindih, ditemukan Step 07 BACKFILL — belum pernah punya AC formal sebelumnya) dan
> menandai eksplisit AC mana yang overlap dengan risiko migrasi (`DIFF-NNN`) dari `03_MIGRATION_SPEC.md`.
>
> **Traceability:** tiap AC menyebut `BSL-NNN` yang diverifikasi. Semua AC di bawah traceable ke
> `01b_BASELINE_SPEC.md` — tidak ada yang dikarang baru di luar baseline.

---

## AC-01 — Trigger dialog configurator saat produk dipilih di baris PO

**AC-01-01** (verifies `BSL-001`, `BSL-002`)
Given baris PO kosong dan user memilih `product_template_id` yang punya optional products
When produk itu dipilih di kolom Product Template
Then dialog `ProductConfiguratorDialogPurchase` terbuka via `_openProductConfigurator()`, TANPA
langsung meng-update `product_id` baris PO — harus identik dengan 17.0.

**AC-01-02** (verifies `BSL-003`)
Given produk template punya tepat SATU varian dan TIDAK punya optional products
When produk dipilih
Then baris PO langsung ter-update ke varian tunggal itu, dialog TIDAK dibuka.

**AC-01-03** (verifies `BSL-004`) — **⚠ overlap `DIFF-03`, verifikasi eksplisit wajib**
Given `get_single_product_variant` mengembalikan `purchase_warning` bertipe `block`
When produk template dipilih
Then dialog peringatan ditampilkan, `product_template_id` di-reset ke `false`. **Di 18.0, method
yang dipanggil (`get_single_product_variant`, sekarang di `product.template` core) kemungkinan
besar TIDAK PERNAH mengembalikan `purchase_warning` sama sekali (DIFF-03) — AC ini harus dites
dengan skenario eksplisit (produk dengan `purchase_line_warn` diisi) untuk MEMBUKTIKAN cabang ini
unreachable, bukan diasumsikan.** Kalau terbukti unreachable di 17.0 DAN 18.0 sama-sama (bukan
regresi migrasi) — dicatat sebagai limitasi warisan, bukan gagal AC.

**AC-01-04** (verifies `BSL-005`) — **⚠ overlap `DIFF-03`**, sama seperti AC-01-03 tapi untuk tipe `warning` (non-blocking).

**AC-01-05** (verifies `BSL-006`)
Given tidak ada `result.product_id`/`purchase_warning`, `result.mode` kosong/`'configurator'`
When produk template dipilih
Then dialog Product Configurator dibuka (default) — harus identik dengan 17.0.

**AC-01-06** (verifies `BSL-007`) — **⚠ overlap `DIFF-05`, `DIFF-07`, verifikasi eksplisit wajib**
Given `result.mode` bernilai selain `'configurator'`
When produk template dipilih
Then `_openGridConfigurator()` dipanggil. **Di 18.0, `product_add_mode`/`result.mode` kemungkinan
besar TIDAK PERNAH terisi (DIFF-07, mekanisme deliberately Sale-only) — sama seperti AC-01-03/04,
harus dibuktikan lewat skenario eksplisit, bukan diasumsikan "tetap sama seperti 17.0" tanpa test.**
Juga verifikasi `_openGridConfigurator()` (dipanggil tanpa argumen, DIFF-05) tidak error di base
class 18.0 yang baru.

**AC-01-09** (verifies `BSL-009`) — **⚠ overlap `DIFF-04`, prioritas Tinggi**
Given baris PO yang produknya sudah dikonfigurasi sebelumnya dibuka kembali
When user klik untuk edit baris itu
Then dialog terbuka kembali dengan kombinasi atribut & custom value yang sudah tersimpan (`edit=true`).
**Ini AC yang PALING LANGSUNG kena dampak rename `_editProductConfiguration`→`onEditConfiguration`
(DIFF-04) — kalau rename salah/terlewat, AC ini regresi silent (dialog tidak terbuka ATAU terbuka
kosong tanpa data tersimpan) tanpa error yang jelas.**

---

## AC-02 — Update currency berdasarkan partner (bug warisan, BSL-010..012)

**AC-02-01** (verifies `BSL-010`)
Given PO baru tanpa `partner_id` terisi
When onchange trigger
Then `currency_id` TIDAK berubah — harus identik 17.0 (bug dipertahankan, TIDAK diperbaiki).

**AC-02-02** (verifies `BSL-011`)
Given `partner_id.property_purchase_currency_id` kebetulan sama dengan `currency_id` PO
When onchange trigger
Then no-op observable — harus identik 17.0.

**AC-02-03** (verifies `BSL-012`)
Given `partner_id.property_purchase_currency_id` berbeda dari `currency_id` PO
When onchange trigger
Then `currency_id` PO **TETAP TIDAK BERUBAH** (self-assign, bug logic terbalik) — harus identik
17.0, JANGAN diperbaiki meski sekarang dipahami sebagai bug jelas.

---

## AC-03 — Konversi harga produk ke currency PO (BSL-016..018)

**AC-03-01** (verifies `BSL-016`)
Given `from_currency.id` sama dengan currency di `ir.config_parameter['currency_id']`
When `convert_price` dipanggil
Then harga dikembalikan apa adanya (short-circuit) — identik 17.0.

**AC-03-02** (verifies `BSL-016`, `BSL-017`)
Given `from_currency` beda dari currency di parameter global
When `convert_price` dipanggil
Then konversi lewat `res.currency._convert()` ke currency PARAMETER GLOBAL (bukan currency PO
user pemanggil) — risiko race condition warisan, dipertahankan identik, TIDAK diperbaiki.

**AC-03-03** (verifies `BSL-018`) — **⚠ overlap `DIFF-01`, prioritas verifikasi**
Given `from_currency` beda dari parameter global (baris `_convert()` benar-benar tereksekusi)
When method dijalankan
Then **TIDAK melempar error** — dikonfirmasi aman di 17.0 (Mode B run #1/#2/#7) DAN dikonfirmasi
lewat pembacaan source 18.0 (`_convert()` masih `company=None, date=None`, DIFF-01) bahwa
signature tetap kompatibel. **Tetap WAJIB re-run test nyata di 18.0** (bukan diasumsikan otomatis
sama hanya karena baca kode) — persis alasan kenapa AC ini gagal diprediksi benar sebelumnya di
17.0 (F-05 sempat salah diduga crash, baru terbukti aman lewat eksekusi nyata).

---

## AC-04 — Field `product_add_mode` (dead code warisan, BSL-008)

**AC-04-01** (verifies `BSL-008`)
Given modul ter-install
When modul di-load
Then TIDAK ada `SyntaxError`/`ImportError` — field tetap "rusak" secara desain (keyword-argument ke
`Many2many()`), bukan `SyntaxError`. Harus identik 17.0 DAN 18.0.

**AC-04-02** (verifies `BSL-008`) — **⚠ overlap `DIFF-07`**
Given kode memanggil `line.product_add_mode`
When dipanggil (Python atau `read()`/JS)
Then error "field does not exist" — field ini tetap TIDAK terdaftar di `_fields`, TIDAK diperbaiki.
Sekarang dipahami lebih jelas (DIFF-07: `purchase_product_matrix` 18.0 punya comment eksplisit
"tidak perlu cek `product_add_mode`") kenapa field ini secara desain platform memang tidak pernah
akan dipakai — bukan alasan untuk memperbaikinya.

---

## AC-05 — Harga berdasarkan supplierinfo vendor (BSL-013..015)

**AC-05-01** (verifies `BSL-013`)
Given produk punya `supplierinfo` dengan `partner_id` cocok `id_vendor` PO
When harga dihitung
Then harga & currency dari `supplierinfo` itu dipakai, dikonversi via `convert_price` — identik 17.0.

**AC-05-02** (verifies `BSL-014`)
Given produk punya `supplierinfo` tapi tidak ada yang cocok
When harga dihitung
Then fallback ke `supplierinfo` pertama (`[0]`) — identik 17.0, TIDAK diperbaiki jadi
`standard_price`.

**AC-05-03** (verifies `BSL-015`)
Given produk tidak punya `supplierinfo` sama sekali
When harga dihitung
Then fallback ke `standard_price` — identik 17.0.

---

## AC-06 — Vendor ID dibaca dari DOM (BSL-024, rapuh terhadap perubahan skema DOM Odoo)

**AC-06-01** (verifies `BSL-024`)
Given dialog dibuka pada halaman dengan tepat satu elemen `id_vendor_0`
When `setup()` dialog dijalankan
Then `this.id_vendor` terisi dari elemen itu — identik 17.0. **Prioritas verifikasi Tinggi di 18.0**
karena ini bergantung pada skema `getElementById` yang bisa berubah antar versi Odoo (belum ada
DIFF spesifik ditemukan untuk ini di step 2, tapi juga belum ada bukti eksplisit skema TIDAK
berubah — treat sebagai unverified sampai dites nyata).

**AC-06-02** (verifies `BSL-024`)
Given elemen `id_vendor_0` tidak ditemukan di DOM
When `setup()` dijalankan
Then error runtime (`Cannot read properties of null`), dialog gagal terbuka — perilaku warisan,
belum pernah terjadi di pemakaian nyata 17.0 (tetap tidak diverifikasi eksekusi nyata di BACKFILL
juga), TIDAK perlu "diperbaiki" jadi lebih robust kalau memang tidak observed sebagai masalah nyata.

---

## AC-07 — Optional products rekursif (BSL-019)

**AC-07-01** (verifies `BSL-019`)
Given produk utama punya `optional_product_ids`, user tambah salah satu optional product (nested)
When ditambahkan
Then optional products lanjutan ikut diambil (tanpa duplikat, parent id ditambahkan ke produk yang
sudah ada) — identik 17.0. **Dikonfirmasi CONFIRMED live di 17.0 (Step 07 AI-Browser BACKFILL)** —
titik referensi kuat untuk perbandingan 18.0.

**AC-07-02** (verifies `BSL-019`)
Given optional product punya >1 parent, satu parent dihapus
When dihapus
Then optional product TIDAK ikut terhapus sampai semua parent hilang — identik 17.0, **dikonfirmasi
CONFIRMED live di 17.0**.

---

## AC-08 — Sinkronisasi custom/no-variant attribute value (BSL-021, 022)

**AC-08-01** (verifies `BSL-021`)
Given baris PO sudah punya `product_custom_attribute_value_ids`, `product_id` diganti
When compute dijalankan ulang
Then value yang tidak valid untuk produk baru dihapus — identik 17.0.

**AC-08-02** (verifies `BSL-022`)
Analog AC-08-01 untuk `product_no_variant_attribute_value_ids` — identik 17.0.

---

## AC-09 — Pembuatan varian dynamic saat konfirmasi (BSL-023)

**AC-09-01** (verifies `BSL-023`) — **⚠ overlap area Controller & Route (§2b `03_MIGRATION_SPEC.md`)**
Given produk di dialog belum punya `id`, kombinasi mengandung PTAL `create_variant == "dynamic"`
When user Confirm
Then endpoint `create_product` dipanggil, produk baru dipakai sebelum `props.save()` — identik
17.0. **Method core yang dipanggil (`_create_product_variant` dkk) sekarang tinggal di `product`
(pindah dari `sale_product_configurator`) — signature harus dikonfirmasi kompatibel lewat eksekusi
nyata, bukan cuma baca kode.**

**AC-09-02** (verifies `BSL-023`)
Given ada produk dengan kombinasi tidak valid (`isPossibleConfiguration()` false)
When user Confirm
Then `onConfirm()` langsung return, tidak ada yang disimpan, dialog tetap terbuka — identik 17.0.

---

## AC-10 — Dialog configurator vs grid configurator tumpang tindih (BARU — BSL-020, BSL-025; F-06)

> Ditambahkan di step 5 migrasi — F-06 ditemukan Step 07 BACKFILL (setelah `01B_ACCEPTANCE_CRITERIA.md`
> ditulis), belum pernah punya AC formal. Ini **temuan bernilai tertinggi** seluruh BACKFILL modul
> ini — bug fungsional nyata, bukan risiko teoretis. **Prioritas Tinggi untuk direproduksi ulang
> identik di 18.0** karena `purchase_product_matrix` (parent class dialog grid) berubah struktur
> besar (DIFF-04) — kemungkinan berubah (jadi hilang ATAU jadi lebih parah), TIDAK BOLEH diasumsikan
> otomatis sama tanpa direproduksi ulang.

**AC-10-01** (verifies `BSL-020`, `BSL-025`)
Given produk yang SEKALIGUS matrix-eligible (`purchase_product_matrix`) DAN punya optional products
(modul ini)
When `product_template_id` dipilih di baris PO
Then dialog custom "Configure your product" DAN dialog grid "Choose Product Variants" terbuka
BERTUMPUK tanpa koordinasi (grid di belakang, configurator di depan) — harus identik 17.0.

**AC-10-02** (verifies `BSL-020`)
Given kedua dialog terbuka bertumpuk (AC-10-01), user hanya berinteraksi dengan dialog depan
(Confirm) tanpa menyentuh dialog grid di belakang
When Confirm ditekan
Then baris produk UTAMA hilang total dari PO tanpa error/warning apapun (state ditentukan grid,
bukan callback `save()` configurator) — bug fungsional dipertahankan identik, **TIDAK diperbaiki**.

**AC-10-03** (verifies `BSL-020`)
Given kedua dialog terbuka bertumpuk, user Confirm grid dulu (qty>0) baru configurator
When kedua langkah dilakukan berurutan
Then kedua baris tersimpan benar — identik 17.0.
