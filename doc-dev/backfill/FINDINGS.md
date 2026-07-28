# Findings — purchase_product_optional

> Satu file konsolidasi — pemilik modul cukup baca file ini untuk tahu semua hal yang butuh
> keputusan manusia, tanpa perlu baca ulang seluruh `doc-dev/`. Diisi terus sepanjang proses
> (bukan cuma di satu step), bukan bagian dari template SOP normal — ini spesifik BACKFILL.
>
> **Prinsip:** begitu ditemukan spot ambigu/bug, catat di sini dan LANJUT — jangan berhenti
> menunggu resolusi satu per satu. Pemilik modul me-review batch ini setelah draft `doc-dev/`
> lengkap tersedia.
>
> **Dokumen hidup, bukan laporan sekali-jadi:** pemilik modul boleh memperbaiki kode bisnis SENDIRI
> (di luar BACKFILL) kapan saja berdasarkan finding di sini. Kalau itu terjadi, update entry finding
> terkait jadi `✅ RESOLVED`/`✅ CONFIRMED` + tanggal + bukti test (bukan dihapus).

---

## Ringkasan

| ID | Judul | Tag | Prioritas |
|---|---|---|---|
| F-01 | Field `product_add_mode` tidak pernah terdaftar di `purchase.order.line` (kurung `Many2many()` tidak ditutup) | `[PERLU-KEPUTUSAN]` | Rendah — **✅ CONFIRMED Mode B** (2026-07-28: test pass + WARNING log Odoo sendiri) |
| F-02 | `onchange_partner_id` tidak pernah benar-benar mengubah `currency_id` sesuai mata uang pembelian partner | `[PERLU-KEPUTUSAN]` | Sedang — **✅ CONFIRMED Mode B** (2026-07-28: 3 test pass sesuai hipotesis) |
| F-03 | `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL (bukan per-record/per-session) lalu dibaca balik oleh `convert_price` | `[PERLU-KEPUTUSAN]` | Tinggi — mekanisme global-param dikonfirmasi ADA (test AC-03-01 pass), race condition-nya sendiri belum bisa disimulasikan di satu `TransactionCase` |
| F-04 | Harga per-vendor di dialog configurator bergantung pada `document.getElementById('id_vendor_0')` | `[PERLU-KEPUTUSAN]` | Sedang — mekanisme **✅ CONFIRMED bekerja BENAR di kondisi normal** via AI-Browser (2026-07-28, Step 07B: harga vendor Azure Interior $700 tampil benar, bukan list price $750); risiko edge-case (id conflict/dua form sekaligus) tetap **TIDAK diverifikasi** (di luar kondisi normal, Chrome/Tour/QUnit tetap gagal — lihat Limitasi Tool) |
| F-05 | `convert_price` kemungkinan CRASH (`TypeError`) setiap kali currency benar-benar beda | ~~`[PERLU-KEPUTUSAN]`~~ | **❌ TIDAK TERBUKTI** — dikonfirmasi 3× (run #1, #2, #7), test sudah dikoreksi jadi `test_ac_03_03_convert_price_real_conversion_no_crash` (PASS) |
| F-06 | Dialog "Configure your product" (custom) dan "Choose Product Variants" (grid, `purchase_product_matrix`) tumpang tindih tanpa koordinasi — baris produk UTAMA bisa hilang dari PO | `[PERLU-KEPUTUSAN]` | **Tinggi** — **✅ CONFIRMED via AI-Browser** (2026-07-28, Step 07B, reproduksi live 2×) |

---

## Detail

### F-01 — Field `product_add_mode` tidak pernah terdaftar di `purchase.order.line`
**✅ CONFIRMED via Mode B (2026-07-28)** — `test_ac_04_02_product_add_mode_field_missing` PASS, dan
log Odoo sendiri (`docker-env/logs/odoo.log` baris 920) menunjukkan WARNING runtime asli:
`Field purchase.order.line.product_no_variant_attribute_value_ids: unknown parameter
'product_add_mode', if this is an actual parameter you may want to override _valid_field_parameter` —
Odoo sendiri mendeteksi kwarg asing ini saat load, konfirmasi independen dari test.
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `purchase_product_optional/models/purchase_order_line.py:24-28`
**Ref:** BR-04, AC-04-02
**Deskripsi:** Definisi field `product_no_variant_attribute_value_ids = fields.Many2many(...)` tidak
ditutup kurungnya sebelum baris berikutnya. Baris berikutnya menulis
`product_add_mode = fields.Selection(related='product_id.product_template_id.product_add_mode', depends=['product_template_id']))`
— karena tidak ada baris baru/kurung penutup di antaranya, Python mem-parse ini sebagai keyword
argument `product_add_mode=fields.Selection(...)` yang dioper ke constructor `Many2many()`, bukan
sebagai definisi field baru yang berdiri sendiri. Ini tidak menyebabkan `SyntaxError` (modul tetap
ter-load normal — dikonfirmasi lewat `models/__init__.py`), tapi akibatnya `purchase.order.line`
**tidak pernah punya field `product_add_mode` yang nyata** — tidak terdaftar di `_fields`, tidak
bisa diakses via ORM (`self.product_add_mode` akan error "field does not exist").
**Dampak:** Digrep di seluruh modul (Python/XML/JS) — `product_add_mode` TIDAK dipakai di tempat
lain manapun. Alur JS yang menentukan dialog configurator-vs-grid (`purchase_product_field.js` /
`_onProductTemplateUpdate`) sudah mendapat keputusannya lewat `result.mode` dari RPC
`get_single_product_variant` (dibaca langsung dari `product.template`, bukan lewat field yang rusak
ini). **Dampak fungsional saat ini kemungkinan NOL** — tapi field yang dimaksud tidak pernah ada
sesuai desain aslinya, dan berisiko membingungkan developer berikutnya yang menyangka field ini ada.
**Rekomendasi:** Pisahkan jadi dua definisi field terpisah (tutup kurung `Many2many()` setelah
`compute=...`, lalu deklarasikan `product_add_mode = fields.Selection(...)` sebagai baris field
tersendiri) — TIDAK dieksekusi oleh BACKFILL (dilarang ubah kode bisnis), murni rekomendasi untuk
pemilik modul.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-02 — `onchange_partner_id` tidak pernah benar-benar mengubah `currency_id` sesuai partner
**✅ CONFIRMED via Mode B (2026-07-28)** — ketiga test (`test_ac_02_01`/`02`/`03`) PASS persis
sesuai hipotesis, termasuk `test_ac_02_03_onchange_partner_currency_differs_bug` yang secara
eksplisit membuktikan `currency_id` PO TIDAK berubah walau partner punya
`property_purchase_currency_id` berbeda.
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `purchase_product_optional/models/purchase_order.py:9-22`
**Ref:** BR-02, AC-02-01
**Deskripsi:** Docstring method ini menyatakan "Update currency based on the partner's purchase
currency", tapi membaca isi ketiga cabangnya:
- Cabang `if not self.partner_id.id` — tidak menyentuh `currency_id` sama sekali, cuma
  menyimpan `self.currency_id.id` (nilai yang SUDAH ada) ke `ir.config_parameter`.
- Cabang `elif self.partner_id.property_purchase_currency_id == self.currency_id` — assignment
  `self.currency_id = self.partner_id.property_purchase_currency_id` menetapkan nilai yang SUDAH
  sama dengan `self.currency_id` (kondisi elif-nya memastikan keduanya sudah sama) — assignment ini
  secara efektif no-op.
- Cabang `else` (partner currency BEDA dari currency_id saat ini) — `self.currency_id = self.currency_id`,
  literal self-assignment, jelas tidak mengubah apapun.
Di ketiga cabang, `currency_id` PO **tidak pernah benar-benar di-override oleh mata uang pembelian
partner** — persis kebalikan dari yang dijelaskan docstring. Kemungkinan logic yang dimaksud aslinya
adalah: kalau partner punya `property_purchase_currency_id` dan itu BEDA dari currency_id saat ini,
maka SET `self.currency_id` ke nilai partner itu — tapi kondisi if/elif/else di atas tertukar/salah
tempat.
**Dampak:** Kalau memang ini bug, dampaknya: PO tidak otomatis mengikuti mata uang pembelian
standar vendor saat vendor dipilih/diganti — user harus ganti currency manual. Tidak menyebabkan
crash, cuma silent-fail terhadap fitur yang (dari nama method + docstring) sepertinya dimaksudkan.
**Rekomendasi:** Konfirmasi ke pemilik modul apakah UX yang benar memang "currency tidak pernah
auto-berubah dari partner" (kalau begitu, ini disengaja dan cuma butuh docstring diperbaiki) atau
memang seharusnya auto-override (kalau begitu, if/elif/else perlu ditulis ulang).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL, dibaca balik oleh `convert_price`
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `purchase_product_optional/models/purchase_order.py:9-22` (penulis) +
`purchase_product_optional/models/product_template.py:11-30` (pembaca, method `convert_price`)
**Ref:** BR-02, BR-03, AC-02-01, AC-03-01
**Deskripsi:** `onchange_partner_id` (lihat F-02) menyimpan `currency_id` PO yang sedang diedit ke
`ir.config_parameter` (key `'currency_id'`) lewat `set_param`. `ir.config_parameter` adalah tabel
**system-wide singleton** — satu baris per key, dipakai bersama oleh SELURUH user & SELURUH record
di database yang sama (bukan per-record/per-session/per-user). `convert_price` di `product_template.py`
membaca balik key global ini (`get_param('currency_id')`) untuk menentukan mata uang TARGET saat
mengkonversi harga di dialog configurator (dipanggil dari JS `product_configurator_dialog.js`
`get_optional_product_prices()`/`get_product_update_price()` lewat RPC `orm.call(...,'convert_price',...)`).
**Dampak:** Kalau ada DUA user membuka/mengedit PO dengan `currency_id` berbeda pada waktu yang
hampir bersamaan (concurrent), `set_param` user kedua akan menimpa nilai yang disimpan user
pertama SEBELUM `convert_price` milik user pertama sempat dipanggil — user pertama berpotensi
melihat harga hasil konversi ke mata uang yang SALAH (mata uang PO user lain, bukan miliknya
sendiri). Ini risiko race condition nyata di lingkungan multi-user (yang lazim untuk modul
Purchase). Tidak bisa dipastikan seberapa sering ini benar-benar terjadi tanpa instrumentasi/log
produksi — dicatat sebagai limitasi tool juga di bawah.
**Rekomendasi:** Hilangkan pola global-parameter ini; oper `currency_id` PO secara eksplisit sebagai
parameter tiap kali `convert_price` dipanggil (RPC/`orm.call` sudah membawa `currency_id` di
beberapa endpoint controller lain — pola yang sama bisa dipakai di sini) alih-alih menyimpan state
lewat system parameter.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — Harga per-vendor bergantung pada `document.getElementById('id_vendor_0')`
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js:41-43`
(pembaca DOM) + `purchase_product_optional/models/purchase_order_line.py:7-11` (field `id_vendor` +
`onchange_id_vendor`) + `purchase_product_optional/views/purchase_order_views.xml:27-36` (field
`id_vendor` disisipkan ke form, disembunyikan lewat CSS `visibility: hidden`, bukan `invisible`
attribute Odoo biasa)
**Deskripsi:** Untuk menentukan harga produk berdasarkan vendor yang dipilih di PO, dialog
configurator (`ProductConfiguratorDialogPurchase.setup()`) membaca DOM secara langsung:
`document.getElementById('id_vendor_0').value` — bergantung pada asumsi implisit bahwa Odoo akan
selalu me-render field `id_vendor` dengan DOM id persis `id_vendor_0` (konvensi id Odoo untuk field
pertama bernama itu di halaman), dan bahwa selalu ada TEPAT SATU elemen dengan id itu di DOM pada
saat dialog dibuka. Field `id_vendor` sendiri disembunyikan visual lewat CSS custom
(`.id_vendor { visibility: hidden; }`) di view, bukan lewat mekanisme `invisible`/`column_invisible`
Odoo standar — dipertahankan di DOM (bukan dihilangkan) supaya bisa dibaca lewat `getElementById`.
**Dampak:** Pola ini bekerja SELAMA konvensi penomoran id Odoo tidak berubah dan hanya ada satu form
PO aktif di halaman. Kalau Odoo core mengganti skema id generation (upgrade versi), atau kalau ada
context yang me-render dua form PO sekaligus di halaman yang sama (mis. dialog di dalam dialog,
list-view multi-edit), pembacaan ini bisa silently mengambil id vendor yang salah atau `null`
(fallback ke cabang `else` di `get_product_update_price`/`get_optional_product_prices`, yang jatuh
ke supplier pertama/harga standar — tidak crash, tapi harga yang ditampilkan bisa salah tanpa
error terlihat).
**Rekomendasi:** Oper `partner_id`/vendor id PO secara eksplisit sebagai prop/parameter RPC ke
dialog (parallel dengan `currencyId`/`companyId`/dst yang sudah dioper eksplisit lewat
`_openProductConfigurator` di `purchase_product_field.js`), alih-alih membaca DOM langsung.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-05 — `convert_price` kemungkinan CRASH setiap kali currency benar-benar berbeda
**❌ TIDAK TERBUKTI (2026-07-28, Mode B nyata, DIKONFIRMASI 3× — run #1, run #2, run #7 konsisten)** —
hasil run #1 dan #2 `docker compose up` (dev, `docker-env/logs/odoo.log` baris ~928-940 dan
~1009-1022) menunjukkan `test_ac_03_03_convert_price_crashes_on_real_conversion` **FAIL** dengan
pesan `AssertionError: TypeError not raised`. Di run #7 (baseline final, setelah Dockerfile
websocket-client selesai dan percobaan Chrome dihentikan — lihat `04A_DEV_TESTING.md`), test itu
sendiri sudah dikoreksi jadi `test_ac_03_03_convert_price_real_conversion_no_crash` (assert hasil
float, bukan lagi `assertRaises(TypeError)`) dan **PASS** — konsisten membuktikan `convert_price(
100.0, EUR.id)` dengan config param di-set ke USD **TIDAK melempar `TypeError`**, bukan fluke.
Hipotesis F-05 (berdasar baca kode + signature `_convert` yang dikutip dari pencarian web ke
dokumentasi/forum Odoo) **terbukti SALAH** setelah eksekusi nyata — kemungkinan build Odoo
17.0-20260630 yang dipakai sudah punya default value untuk `company`/`date` di `_convert` (beda
dari yang tersirat di hasil pencarian sebelumnya), atau ada mekanisme lain yang tidak tertangkap
dari baca kode saja. **Ini contoh nyata KENAPA Step 04 harus benar-benar dieksekusi, bukan cuma
desk-review** — deskripsi asli finding tetap disimpan di bawah untuk histori, TAPI jangan dipakai
sebagai dasar keputusan lagi. Test `test_ac_03_03_...` tetap ada di `tests/test_purchase_order_currency.py`
sebagai regression-guard (kalau nanti Odoo versi lain benar-benar crash, test ini akan menangkapnya),
bukan dihapus.

**Deskripsi asli (SALAH, disimpan untuk histori):**

**Tag:** `[PERLU-KEPUTUSAN]` → ~~seharusnya `[HASIL-BACA]` yang salah~~, sudah tidak `[PERLU-KEPUTUSAN]` lagi
**Lokasi:** `purchase_product_optional/models/product_template.py:26-29` (method `convert_price`)
**Ref:** BR-03, AC-03-02
**Ditemukan saat:** Step 04 (menulis test `convert_price`), BUKAN cuma dari baca kode desk-review —
dikonfirmasi silang ke source resmi `odoo/odoo` branch `17.0` (`addons/base/models/res_currency.py`,
lewat web search ke dokumentasi/forum resmi Odoo yang mengutip signature-nya) sebelum ditulis di
sini sebagai finding, bukan dugaan semata.
**Deskripsi:** `convert_price` memanggil:
```python
price = from_currency._convert(
    from_amount=price,
    to_currency=to_currency,
)
```
Signature asli `res.currency._convert` di Odoo 17.0 adalah
`_convert(self, from_amount, to_currency, company, date, round=True)` — parameter `company` dan
`date` WAJIB (tidak ada default value), TIDAK dioper sama sekali di pemanggilan ini. Baris
`if from_currency.id == to_currency_id: return price` (tepat di atasnya) MELINDUNGI kasus currency
sama (short-circuit, tidak pernah sampai memanggil `_convert`) — tapi begitu currency BENAR-BENAR
beda (kasus yang justru jadi tujuan utama method ini dibuat), baris `_convert(...)` akan dieksekusi
dan kemungkinan besar melempar `TypeError: _convert() missing 2 required positional arguments:
'company' and 'date'`.
**Dampak:** Kalau benar crash, seluruh alur harga di dialog configurator yang butuh konversi currency
sungguhan (produk dengan currency berbeda dari currency PO) akan GAGAL total saat method ini
dipanggil dari JS (`get_optional_product_prices`/`get_product_update_price` di
`product_configurator_dialog.js`, lewat `orm.call('product.template', 'convert_price', ...)`) —
bukan cuma salah angka seperti F-03, tapi request RPC error/exception yang terlihat user (harga
tidak muncul sama sekali, bukan cuma salah). Ini mengubah severity keseluruhan mekanisme currency
konversi modul ini dari "berisiko" (F-03) jadi "kemungkinan tidak pernah benar-benar berfungsi
untuk kasus multi-currency nyata" — PERLU dikonfirmasi lewat eksekusi nyata (Mode B), bukan cuma
diklaim dari baca kode + signature upstream, lihat test `test_product_template_convert_price.py`
TC-CP-02 di `test/04A_DEV_TESTING.md`.
**Rekomendasi (dari hipotesis yang SALAH, disimpan untuk histori):** ~~Tambahkan `company=self.env.company`
dan `date=fields.Date.today()` ke pemanggilan `_convert()`~~ — TIDAK relevan lagi, `_convert()`
terbukti tidak crash tanpa argumen itu di versi yang dites.
**Keputusan pemilik modul:** Tidak perlu keputusan — hipotesis sudah terbukti salah lewat eksekusi
nyata 2026-07-28, ditutup sebagai `❌ TIDAK TERBUKTI`, bukan `[PERLU-KEPUTUSAN]` lagi.

---

### F-06 — Dialog configurator (custom) dan grid `purchase_product_matrix` tumpang tindih tanpa koordinasi
**✅ CONFIRMED via AI-Browser (2026-07-28, Step 07B)** — direproduksi LIVE dua kali di
`http://localhost:8079` (Mode B G2) memakai produk demo "Customizable Desk" (`[FURN_0096]`,
attribute Legs [Instantly, 3 value] × Color [Instantly, 2 value] = matrix-eligible, dengan optional
product "Conference Chair" terpasang) dan vendor "Azure Interior" (harga khusus $700, vs list
price $750 — sekaligus mengonfirmasi AC-05-01/harga per-vendor bekerja benar).
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `purchase_product_optional/static/src/js/purchase_product_field.js:55-95`
(`_onProductTemplateUpdate`, panggilan `super._onProductTemplateUpdate(...)` TANPA SYARAT di baris
56) + `purchase_product_field.js:104-154` (`_openProductConfigurator`, callback `save()` baris
134-149) — terkait langsung ke F-01 (`product_add_mode`).
**Ref:** BR-01, AC-01 (semua sub-AC dialog trigger), berkaitan dengan F-01.
**Deskripsi:** Saat memilih produk yang SEKALIGUS (a) matrix-eligible di mata parent class
(`purchase_product_matrix`) — attribute "Instantly" dengan >1 kombinasi variant, dan (b) punya
optional products (memicu dialog custom modul ini) — DUA dialog terbuka:
1. **"Choose Product Variants"** (grid, milik `purchase_product_matrix`, dipicu oleh
   `super._onProductTemplateUpdate()` yang dipanggil TANPA SYARAT di baris pertama override ini,
   sebelum override sendiri sempat menentukan apapun).
2. **"Configure your product"** (`ProductConfiguratorDialogPurchase`, custom modul ini, dipicu
   RPC `get_single_product_variant` + `has_optional_products=True`).
Keduanya TIDAK terkoordinasi — grid dialog terbuka TERTUMPUK DI BELAKANG configurator dialog
(secara visual, hanya dialog depan yang langsung terlihat; grid baru kelihatan kalau user klik di
area belakang overlay).

**Reproduksi #1 (bug asli, ditemukan tanpa disengaja):** User hanya berinteraksi dengan dialog
depan ("Configure your product") — menambah "Conference Chair" via `+Add`, lalu klik Confirm —
TANPA sadar ada grid dialog tersembunyi di belakang. **Hasil: PO tersimpan HANYA dengan baris
"Conference Chair" — baris utama "Customizable Desk" HILANG TOTAL, tanpa error/warning apapun.**

**Reproduksi #2 (terkontrol, mengonfirmasi akar masalah):** User sengaja klik ke area belakang,
menemukan grid "Choose Product Variants" masih terbuka, isi qty=1 pada satu kombinasi lalu klik
Confirm PADA GRID itu dulu — baris "Customizable Desk" LANGSUNG muncul di tabel PO (state
tersimpan lewat grid, bukan lewat configurator). Configurator dialog (masih terbuka di depan)
baru di-Confirm setelahnya untuk optional product — hasil akhir kedua baris ada, total $8,050.00.

**Reproduksi #3 (ditemukan setelah #2, klarifikasi — BUKAN bug modul ini, dicatat untuk kelengkapan):**
Setelah reproduksi #2 terlihat sukses di UI (kedua baris tampil, Total $8,050.00, form masih
berstatus unsaved/draft dengan ikon cloud/undo), navigasi TIDAK SENGAJA terjadi (klik nama produk
membuka form `product.template` di tab yang sama) SEBELUM sempat klik save eksplisit — begitu
kembali ke PO yang sama, baris "Customizable Desk" hilang lagi (record ter-reload dari versi
tersimpan terakhir di server, yang belum termasuk perubahan draft). **Reproduksi #4 (klarifikasi
lanjutan, kali ini benar):** Diulang persis skenario #2 (grid Confirm qty>0, lalu configurator
Confirm), tapi kali ini diikuti klik SAVE eksplisit (ikon cloud breadcrumb) sebelum navigasi apapun
— chatter log mencatat perubahan `$0.00 → $7.000,00 (Untaxed Amount)`, dan setelah full page
reload (navigate ulang ke URL yang sama), KEDUA baris ("Customizable Desk" qty 10, $700, dan
"Conference Chair" qty 1, $0.00) tetap ADA dan BENAR. **Kesimpulan:** reproduksi #3 adalah perilaku
standar Odoo web client (perubahan draft yang belum di-save bisa hilang kalau user navigasi keluar
form sebelum save) — BUKAN bug spesifik modul ini, dicatat di sini murni untuk kelengkapan
investigasi, bukan bagian dari F-06 inti. **Bug inti F-06 tetap valid dan berdiri sendiri**:
skenario Reproduksi #1 (user HANYA berinteraksi dengan dialog depan "Configure your product",
tidak pernah menyentuh grid dialog sama sekali, langsung Confirm) tetap menghasilkan baris utama
HILANG TOTAL — itu murni akibat dua dialog independen yang tidak terkoordinasi, bukan soal
save/navigasi.
**Kesimpulan akar masalah:** baris produk UTAMA ditentukan oleh dialog GRID (`purchase_product_matrix`,
independen), BUKAN oleh `save()` callback modul ini yang SEHARUSNYA mengisi baris lewat
`applyProductPurchase(this.props.record, mainProduct)` (`purchase_product_field.js:135`) — begitu
grid dialog ikut memanipulasi baris yang sama, assignment dari configurator tidak berpengaruh
nyata ke baris tersimpan kalau grid tidak pernah di-confirm dengan qty > 0. Field `product_add_mode`
(F-01) tampak DIMAKSUDKAN untuk memberi tahu kelas induk (`purchase_product_matrix`) agar SKIP
membuka grid-nya sendiri saat modul ini mau mengambil alih lewat configurator — tapi field itu
rusak (F-01) DAN override ini juga TIDAK PERNAH membaca `product_add_mode` dari manapun (digrep:
0 pemakaian di seluruh JS modul) untuk mencegah `super()` membuka grid. Akibatnya kedua dialog
selalu berpotensi tumpang tindih untuk SEMUA produk yang qualify kedua kondisi sekaligus — bukan
kasus khusus produk demo ini saja.
**Dampak:** **TINGGI.** Berbeda dari F-04 (edge-case DOM), ini bug fungsional yang bisa terjadi di
alur pemakaian NORMAL: user bisa kehilangan baris produk utama dari Purchase Order tanpa pesan
error apapun, hanya dengan mengikuti alur "intuitif" (isi dialog depan, klik Confirm) tanpa tahu
ada dialog kedua tersembunyi di belakang.
**Catatan tambahan (kode, bukan fungsional, ditemukan saat investigasi finding ini):** 3 leftover
`console.log` debug ditemukan di alur yang sama — `purchase_product_field.js:137`
(`console.log('Main Product Quantity:', mainProduct.quantity)`), `purchase_product_field.js:147`
(`console.log('tes')`, di dalam loop optional products), dan
`product_configurator_dialog/product_configurator_dialog.js:531`
(`console.log("Checking configuration:", this.state.products)`). Tidak berdampak fungsional,
sekadar indikasi kode ini kemungkinan masih tahap debugging saat commit terakhir.
**Rekomendasi:** Perbaiki F-01 dulu (tutup kurung field `product_add_mode`), lalu pastikan
`_onProductTemplateUpdate` override membaca hasil itu (atau hasil RPC `get_single_product_variant`)
untuk memutuskan HANYA SATU dialog yang dibuka — skip pemanggilan grid `super()` kalau override
berencana membuka configurator sendiri. Hapus 3 `console.log` leftover. TIDAK dieksekusi oleh
BACKFILL (dilarang ubah kode bisnis) — murni rekomendasi.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

## Limitasi Tool (kalau ada)

- F-03 (currency global param race condition) baru bisa dipastikan FREKUENSI kejadiannya lewat
  instrumentasi/logging tambahan di produksi (mis. log tiap `set_param`/`get_param` dengan
  timestamp+user) — BACKFILL tidak menambahkan logging ke kode bisnis sesuai prinsip
  tidak-ubah-kode-bisnis. Yang bisa dipastikan dari baca kode: mekanismenya SECARA DESAIN rentan
  race condition (tabel `ir.config_parameter` adalah singleton global) — bukan dugaan, tapi
  frekuensi kejadian nyata di database produksi tidak bisa diverifikasi tanpa data operasional.
- F-04 (DOM id `id_vendor_0`) — konvensi id generation Odoo tidak didokumentasikan resmi dan bisa
  berbeda antar versi/context render; BACKFILL memverifikasi ini SECARA STATIS dari kode (asumsi
  yang dipakai), bukan lewat observasi runtime multi-tab langsung (dicatat lagi di
  `test/07_QA_TESTING.md` bagian skenario kalau perlu verifikasi langsung via browser).
- ~~F-05 (`convert_price` diduga crash) — belum dieksekusi~~ **SUDAH dieksekusi 2026-07-28 via
  Mode B nyata (dev menjalankan `docker compose up`) — hipotesis TERBUKTI SALAH** (`_convert()`
  tidak crash). Bukan lagi limitasi tool — ini justru CONTOH POSITIF kenapa Step 04 harus benar-benar
  dijalankan: desk-review + baca signature upstream saja HAMPIR membuat finding yang salah masuk ke
  `FINDINGS.md` sebagai `[PERLU-KEPUTUSAN]` prioritas Tinggi, padahal setelah dieksekusi nyata
  ternyata tidak terbukti.
- **Mode D (stub pure-logic) TIDAK BISA dipakai sama sekali untuk modul ini** — beda dari
  `user_roles` yang punya beberapa method murni logic. Semua 9 method Unit-test-able di modul ini
  (`onchange_partner_id`, `convert_price`, compute fields di `purchase_order_line.py`) menyentuh
  `self.env` (currency browse, `ir.config_parameter`, ORM read) — tidak ada satupun yang lolos
  syarat Mode D ("method yang TIDAK menyentuh `self.env` sama sekali"). Step 04 modul ini 100%
  bergantung Mode B (atau Mode A manual) untuk eksekusi nyata, tidak ada shortcut Mode D sebagai
  sinyal cepat.
- **Tour + QUnit (2 dari 13 TC) TIDAK TERVERIFIKASI sama sekali di sesi ini** — image resmi
  `odoo:17.0` tidak menyertakan Chrome/Chromium, dan satu percobaan `apt-get install chromium` di
  `docker-env/Dockerfile` GAGAL (exit code 100, package/repo tidak tersedia). Sesuai batas
  workaround di `CLAUDE.md` (satu percobaan wajar, gagal → stop), TIDAK dicoba variasi lain
  (source apt berbeda, image dasar lain, dst). Ini limitasi environment Mode B, BUKAN indikasi
  bug kode — JS syntax `product_configurator_dialog_tests.js`/`purchase_product_field_tests.js`/
  `purchase_product_optional_tour.js` sudah terbukti valid (berhasil di-bundle di run #1/#2), tapi
  isi assertion-nya (termasuk verifikasi F-04 di TC JS Unit #04) belum pernah benar-benar
  dieksekusi. Kalau dev ingin ini benar-benar jalan, perlu image custom Doodex yang sudah
  menyertakan Chrome — di luar scope BACKFILL untuk menyiapkan. Verifikasi visual F-04/dialog
  tetap bisa dilakukan lewat Step 07 (AI-Browser) sebagai jalur alternatif.
