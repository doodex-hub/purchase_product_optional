# Acceptance Criteria — purchase_product_optional

**Module:** `purchase_product_optional`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-28
**Status:** Backfill retroaktif

> Format: Given/When/Then, diturunkan dari Business Rules (BR-*) di `01A_FUNCTIONAL_SPEC.md` — bukan
> dari requirement baru. Setiap AC WAJIB traceable ke minimal satu BR. Setiap AC diberi provenance
> tag yang sama seperti BR asalnya (kalau BR-nya `[PERLU-KEPUTUSAN]`, AC turunannya juga).

---

## AC-01 — Trigger dialog configurator saat produk dipilih di baris PO

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given baris PO kosong dan user memilih `product_template_id` yang punya optional products
(`has_optional_products=true` dari `get_single_product_variant`)
When produk itu dipilih di kolom Product Template
Then dialog `ProductConfiguratorDialogPurchase` terbuka via `_openProductConfigurator()`, TANPA
langsung meng-update `product_id` baris PO.

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given user memilih produk template yang punya tepat SATU varian (`result.product_id` ada) dan
`product_id` saat ini di baris berbeda dari varian itu, serta produk TIDAK punya optional products
When produk dipilih
Then baris PO langsung ter-update ke `product_id`/`product_name` varian tunggal itu, dialog TIDAK
dibuka.

**AC-01-03** — ref `BR-01` `[HASIL-BACA]`
Given `get_single_product_variant` mengembalikan `purchase_warning` bertipe `block`
When produk template dipilih
Then dialog peringatan (`WarningDialog`) ditampilkan berisi title+message dari `purchase_warning`,
dan `product_template_id` baris PO di-reset ke `false` — proses pemilihan produk dibatalkan.

**AC-01-04** — ref `BR-01` `[HASIL-BACA]`
Given `get_single_product_variant` mengembalikan `purchase_warning` bertipe `warning` (bukan
`block`)
When produk template dipilih
Then notifikasi non-blocking ditampilkan (`notification.add`), TAPI alur pemilihan produk tetap
lanjut ke pengecekan `result.mode` untuk membuka dialog configurator atau grid configurator.

**AC-01-05** — ref `BR-01` `[HASIL-BACA]`
Given tidak ada `result.product_id` maupun `purchase_warning`, dan `result.mode` kosong/`'configurator'`
When produk template dipilih
Then dialog Product Configurator dibuka (bukan grid configurator) — ini perilaku DEFAULT.

**AC-01-06** — ref `BR-01` `[HASIL-BACA]`
Given `result.mode` bernilai selain `'configurator'` (mis. `'matrix'`)
When produk template dipilih
Then `_openGridConfigurator()` dipanggil (grid/matrix configurator dari
`purchase_product_matrix`), BUKAN dialog Product Configurator milik modul ini.

---

## AC-02 — Update currency berdasarkan partner (BR-02, kandidat bug)

**AC-02-01** — ref `BR-02` `[PERLU-KEPUTUSAN]`
Given PO baru tanpa `partner_id` terisi (`self.partner_id.id` falsy)
When field `currency_id` atau `partner_id` berubah (trigger onchange)
Then `currency_id` PO TIDAK berubah (tidak disentuh sama sekali di cabang ini) — hanya nilai
`currency_id` yang SUDAH ada yang ditulis ke `ir.config_parameter['currency_id']`. Lihat
`FINDINGS.md` F-02/F-03 untuk apakah ini perilaku yang dimaksud.

**AC-02-02** — ref `BR-02` `[PERLU-KEPUTUSAN]`
Given `partner_id` terisi dan `partner_id.property_purchase_currency_id` KEBETULAN SUDAH SAMA
dengan `currency_id` PO saat ini
When onchange trigger
Then `currency_id` di-assign ulang ke nilai yang sama (no-op secara observable), dan nilai itu
ditulis ke `ir.config_parameter['currency_id']`.

**AC-02-03** — ref `BR-02` `[PERLU-KEPUTUSAN]`
Given `partner_id` terisi dan `partner_id.property_purchase_currency_id` BERBEDA dari `currency_id`
PO saat ini (kasus yang menurut docstring seharusnya memicu auto-update)
When onchange trigger
Then `currency_id` PO **TETAP TIDAK BERUBAH** (assignment `self.currency_id = self.currency_id` —
literal self-assign), currency PARTNER tidak pernah diterapkan ke PO meskipun berbeda. Ini
BERTENTANGAN dengan docstring method ("Update currency based on the partner's purchase currency")
— kandidat bug utama, lihat `FINDINGS.md` F-02.

---

## AC-03 — Konversi harga produk ke currency PO (BR-03, risiko global state)

**AC-03-01** — ref `BR-03` `[PERLU-KEPUTUSAN]`
Given `convert_price` dipanggil dengan `from_currency` yang ID-nya SAMA dengan currency yang
tersimpan di `ir.config_parameter['currency_id']`
When method dijalankan
Then harga dikembalikan APA ADANYA tanpa konversi (`if from_currency.id == to_currency_id: return
price`).

**AC-03-02** — ref `BR-03` `[PERLU-KEPUTUSAN]`
Given `convert_price` dipanggil dengan `from_currency` yang BEDA dari currency di
`ir.config_parameter['currency_id']`
When method dijalankan
Then harga dikonversi lewat `res.currency._convert()` ke currency yang tersimpan di parameter
global — BUKAN ke currency PO milik user yang memanggil, kalau parameter global itu SEMPAT ditimpa
oleh onchange PO user LAIN di antara waktu `onchange_partner_id` user ini terakhir jalan dan
`convert_price` ini dipanggil. Skenario race condition ini perlu diverifikasi lewat Step 07 (kalau
memungkinkan disimulasikan) — lihat `FINDINGS.md` F-03.

**AC-03-03** — ref `BR-03` `[HASIL-BACA]` — **❌ hipotesis awal TIDAK TERBUKTI, dikonfirmasi Mode B 2026-07-28**
Given `from_currency` BEDA dari currency di `ir.config_parameter['currency_id']` (baris
`_convert()` benar-benar tereksekusi, bukan short-circuit AC-03-01)
When method dijalankan
Then **TIDAK melempar error** — `_convert()` berjalan normal tanpa argumen `company`/`date` di versi
Odoo yang dites (kontras dengan dugaan awal berdasar signature upstream). Lihat `FINDINGS.md` F-05
untuk kronologi lengkap kenapa hipotesis awal ini salah, dan test
`test_ac_03_03_convert_price_crashes_on_real_conversion` di `tests/test_purchase_order_currency.py`
(sekarang berfungsi sebagai regression-guard, bukan bukti bug).

---

## AC-04 — Field `product_add_mode` (BR-04, dead code)

**AC-04-01** — ref `BR-04` `[HASIL-BACA]`
Given modul ter-install dan `models/__init__.py` mengimpor `purchase_order_line.py`
When modul di-load
Then TIDAK ada `SyntaxError`/`ImportError` — file tetap valid Python (kesalahan parenthesis-nya
menghasilkan keyword-argument yang secara sintaks sah, bukan error saat load).

**AC-04-02** — ref `BR-04` `[PERLU-KEPUTUSAN]`
Given modul ter-install dan record `purchase.order.line` dibaca lewat ORM
When kode memanggil `line.product_add_mode` (baik lewat Python maupun via `read()`/`search_read()`
dari JS)
Then dipanggil akan menghasilkan error "field does not exist" / `KeyError` — field ini TIDAK
terdaftar di `_fields` model. Verifikasi: digrep di seluruh modul, tidak ada kode lain (Python/XML/
JS) yang benar-benar memanggil `product_add_mode` pada `purchase.order.line`, jadi AC ini
kemungkinan besar tidak pernah ter-trigger dalam pemakaian normal saat ini.

---

## AC-05 — Harga berdasarkan supplierinfo vendor (BR-05)

**AC-05-01** — ref `BR-05` `[HASIL-BACA]`
Given produk (utama/optional) punya `product.supplierinfo` dengan `partner_id` yang cocok dengan
`id_vendor` PO
When harga produk dihitung di dialog (`get_product_update_price`/`get_optional_product_prices`)
Then harga & currency yang dipakai adalah milik `supplierinfo` vendor tersebut, dikonversi ke
currency PO lewat `convert_price` (lihat AC-03).

**AC-05-02** — ref `BR-05` `[HASIL-BACA]`
Given produk punya `product.supplierinfo` tapi TIDAK ADA yang `partner_id`-nya cocok dengan
`id_vendor` PO, dan `supplierinfo` list tidak kosong
When harga dihitung
Then fallback ke harga & currency dari `supplierinfo` PERTAMA dalam list (index `[0]`) — BUKAN
`standard_price` produk, meskipun vendor yang dipilih di PO tidak match.

**AC-05-03** — ref `BR-05` `[HASIL-BACA]`
Given produk sama sekali tidak punya `product.supplierinfo` (list kosong)
When harga dihitung
Then fallback ke `standard_price` produk, dikonversi dari currency produk ke currency PO.

---

## AC-06 — Vendor ID dibaca dari DOM (BR-06, kandidat rapuh)

**AC-06-01** — ref `BR-06` `[PERLU-KEPUTUSAN]`
Given dialog configurator dibuka pada halaman yang punya TEPAT SATU elemen dengan DOM id
`id_vendor_0` (kondisi normal — satu form PO per halaman)
When `setup()` dialog dijalankan
Then `this.id_vendor` terisi dari `.value` elemen itu, dipakai sebagai key pencarian supplierinfo
di AC-05.

**AC-06-02** — ref `BR-06` `[PERLU-KEPUTUSAN]`
Given elemen dengan id `id_vendor_0` TIDAK DITEMUKAN di DOM (mis. konvensi id Odoo berubah, atau
dialog dipanggil dari context/rendering yang berbeda)
When `setup()` dialog dijalankan
Then `inputElementIdVendor.value` akan melempar error runtime (`Cannot read properties of null`)
karena `document.getElementById(...)` mengembalikan `null` — dialog GAGAL terbuka sama sekali.
Belum ada verifikasi apakah skenario ini pernah benar-benar terjadi di pemakaian nyata — perlu
dicek di Step 07 kalau memungkinkan (mis. buka dialog dari halaman/context yang tidak standar).

---

## AC-07 — Optional products rekursif (BR-07)

**AC-07-01** — ref `BR-07` `[HASIL-BACA]`
Given produk utama punya `optional_product_ids` dan user menambahkan salah satu optional product ke
daftar terpilih (`_addProduct`)
When produk optional itu punya optional products lanjutan sendiri (nested)
Then optional products lanjutan itu ikut diambil (`_getOptionalProducts`) dan ditambahkan ke
`state.optionalProducts` — kecuali kalau produk itu sudah ada di list (di-skip, parent id-nya
ditambahkan ke `parent_product_tmpl_ids` produk yang sudah ada, tidak duplikat).

**AC-07-02** — ref `BR-07` `[HASIL-BACA]`
Given sebuah optional product punya LEBIH dari satu parent product (`parent_product_tmpl_ids`
punya >1 entry)
When salah satu SATU parent-nya dihapus dari `state.products` (`_removeProduct`)
Then optional product itu TIDAK ikut terhapus selama masih ada parent lain yang tersisa di
`state.products` — baru dihapus kalau `parent_product_tmpl_ids` jadi kosong.

---

## AC-08 — Sinkronisasi custom/no-variant attribute value (BR-08)

**AC-08-01** — ref `BR-08` `[HASIL-BACA]`
Given baris PO sudah punya `product_custom_attribute_value_ids` tersimpan, lalu `product_id` baris
itu diganti ke produk lain
When compute `_compute_custom_attribute_values` dijalankan ulang
Then value custom attribute yang TIDAK termasuk `valid_product_template_attribute_line_ids` milik
produk BARU dihapus dari `product_custom_attribute_value_ids` — value lama untuk produk sebelumnya
tidak ikut terbawa.

**AC-08-02** — ref `BR-08` `[HASIL-BACA]`
Analog AC-08-01, tapi untuk `product_no_variant_attribute_value_ids` lewat
`_compute_no_variant_attribute_values` — membandingkan `ptav._origin` terhadap
`valid_product_template_attribute_line_ids.product_template_value_ids` produk baru.

---

## AC-09 — Pembuatan varian dynamic saat konfirmasi (BR-09)

**AC-09-01** — ref `BR-09` `[HASIL-BACA]`
Given produk (utama atau optional) yang dipilih di dialog belum punya `id` (`product.id` belum
di-set, artinya varian belum ada di database) dan kombinasi atributnya mengandung minimal satu PTAL
dengan `create_variant == "dynamic"`
When user menekan tombol Confirm (`onConfirm`)
Then endpoint `create_product` dipanggil untuk membuat `product.product` baru dari kombinasi itu
SEBELUM `props.save(...)` dipanggil untuk menulis balik ke baris PO — produk baru langsung dipakai
sebagai `product_id` baris PO/optional.

**AC-09-02** — ref `BR-09` `[HASIL-BACA]`
Given salah satu produk di `state.products` punya kombinasi atribut yang TIDAK valid
(`isPossibleConfiguration()` mengembalikan `false` — ada PTAV terpilih yang `excluded`)
When user menekan tombol Confirm
Then `onConfirm()` langsung `return` di awal — TIDAK ada produk yang disimpan/dibuat, dialog TETAP
terbuka (tidak close).
