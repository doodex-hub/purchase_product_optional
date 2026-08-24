# Findings — purchase_product_optional

> Satu file konsolidasi — pemilik modul cukup baca file ini untuk tahu semua hal yang butuh
> keputusan manusia, tanpa perlu baca ulang seluruh `doc-dev/backfill/`. Diisi terus sepanjang proses.
>
> **Dokumen hidup, bukan laporan sekali-jadi:** pemilik modul boleh memperbaiki kode bisnis SENDIRI
> (di luar BACKFILL) kapan saja berdasarkan finding di sini. Kalau itu terjadi, update entry finding
> terkait jadi `✅ RESOLVED`/`✅ CONFIRMED` + tanggal + bukti test, jangan dihapus.

---

## Ringkasan

| ID | Judul | Tag | Prioritas |
|---|---|---|---|
| F-01 | `product_add_mode` tertelan jadi kwarg di dalam `fields.Many2many(...)`, bukan field sendiri | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-02 | `onchange_partner_id` di `purchase_order.py` menggunakan nama method yang sama dengan onchange core Odoo pada `purchase.order` — berpotensi override total, bukan extend | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-03 | Logic `onchange_partner_id`: cabang `else` melakukan `self.currency_id = self.currency_id` (no-op) — currency partner tidak pernah benar-benar diterapkan pada kondisi paling umum | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-04 | `ir.config_parameter` key `currency_id` dipakai sebagai state global lintas-user/lintas-request untuk currency konversi harga — race condition multi-user | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-05 | `convert_price()` memanggil `int(get_param('currency_id'))` tanpa guard kalau param belum pernah di-set (None) | `[PERLU-KEPUTUSAN]` | Sedang |
| F-06 | `id_vendor` field + JS `document.getElementById('id_vendor_0')` — fragile DOM-based state passing, bukan lewat props/context resmi | `[PERLU-KEPUTUSAN]` | Sedang |
| F-07 | `get_supplierinfo_id()`/`get_optional_product_prices()` tidak filter `seller_ids` berdasarkan company — potensi salah company multi-company | `[PERLU-KEPUTUSAN]` | Rendah |
| F-08 | Field `id_vendor` (purchase.order) punya label "ID" yang sama persis dengan field `id` bawaan Odoo — ambigu di UI (mis. optional column selector) | `[PERLU-KEPUTUSAN]` | Rendah |

---

## Detail

### F-01 — `product_add_mode` tertelan jadi kwarg Many2many, bukan field mandiri
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order_line.py:24-28`
**Deskripsi:** Definisi `product_no_variant_attribute_value_ids = fields.Many2many(...)` tidak
ditutup sebelum baris berikutnya menulis `product_add_mode = fields.Selection(...)` — secara
sintaks Python ini valid (kwarg `product_add_mode=fields.Selection(...)` dikirim ke constructor
`Many2many`), tapi secara semantik `product_add_mode` **tidak pernah terdaftar sebagai field ORM
sendiri** pada `purchase.order.line`. `Grep` lintas modul mengonfirmasi `product_add_mode` tidak
dipakai di manapun lagi (tidak ada di views/JS) — field terkait (`related='product_id.product_template_id.product_add_mode'`)
tidak pernah bisa diakses.
**Dampak:** Kalau ada bagian lain (kode/view masa depan, atau modul lain yang depends ke ini)
mengasumsikan `purchase.order.line.product_add_mode` ada, akan `KeyError`/`AttributeError`. Saat ini
tidak terpakai jadi tidak crash langsung — tapi ini indikasi kuat merge/edit yang tidak selesai.
Perlu verifikasi ke Odoo real (Step 04) apakah field asing (`product_add_mode`) sebagai kwarg ke
`Many2many` menyebabkan warning/error saat load registry.
**Rekomendasi:** Pisahkan jadi dua field declaration terpisah (tutup paren Many2many sebelum baris
`product_add_mode`).
**Dikonfirmasi via eksekusi nyata (Step 04, 2026-07-29):** `docker-env/logs/odoo.log` menunjukkan
warning registry Odoo sendiri saat load module: `Field
purchase.order.line.product_no_variant_attribute_value_ids: unknown parameter 'product_add_mode',
if this is an actual parameter you may want to override the method _valid_field_parameter on the
relevant model in order to allow it` — mengonfirmasi `product_add_mode` benar-benar hanya kwarg
asing, bukan field. Modul tetap berhasil ter-install (warning, bukan error fatal).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-02 — `onchange_partner_id` menimpa nama method core Odoo
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order.py:9-22`
**Deskripsi:** Method didefinisikan dengan nama persis `onchange_partner_id` pada `_inherit =
'purchase.order'`. Karena Python override method by name (bukan Odoo API extension mechanism
seperti `_inherit` model), kalau Odoo core `purchase.order` sudah punya method dengan nama sama,
definisi ini MENIMPA TOTAL implementasi asli (bukan menambah di atasnya) — semua efek samping onchange
partner bawaan Odoo (payment terms, fiscal position, incoterm, dll., tergantung versi 17.0) berpotensi
hilang. Commit history repo ini (`git log`, tidak dijalankan langsung oleh BACKFILL tapi terlihat di
gitStatus awal sesi) menyebut "change onchange function name to prevent override onchange_partner_id
function" — mengindikasikan masalah ini SUDAH pernah disadari sebagian, tapi method dengan nama ini
masih ada di `purchase_order.py` saat ini.
**Dampak:** Berpotensi Tinggi — regresi silent pada field-field lain yang biasanya di-set otomatis
oleh Odoo core saat partner berubah di form pembelian.
**Rekomendasi:** Verifikasi langsung ke source Odoo 17.0 core (`addons/purchase/models/purchase.py`)
apakah `onchange_partner_id` ada di sana, dan kalau ada apa isi aslinya — dilakukan di Step 04 lewat
docker image resmi `odoo:17.0` (baca source di image, bukan re-implementasi).
**Dikonfirmasi via eksekusi nyata (Step 04, 2026-07-29):** Test `TestOnchangePartnerCurrency.
test_onchange_partner_id_mro_shadowing_candidates` membaca `type(self.env['purchase.order']).__mro__`
langsung di database live dan mencatat ke log:
```
BACKFILL F-02: classes defining purchase.order.onchange_partner_id:
['odoo.addons.purchase_product_optional.models.purchase_order.PurchaseOrder',
 'odoo.addons.purchase.models.purchase_order.PurchaseOrder']
```
**TERKONFIRMASI:** Odoo core (`addons/purchase/models/purchase_order.py`) BENAR punya method
`onchange_partner_id` sendiri. Karena kelas modul ini muncul LEBIH DULU di MRO (di-load setelah
`purchase` sehingga override menang), implementasi ASLI dari core **sepenuhnya tertimpa** —
bukan cuma dugaan lagi. Efek konkret (payment term/fiscal position/incoterm/dll. yang biasanya
di-set core saat partner berubah) kemungkinan tidak lagi jalan sama sekali pada `purchase.order`.
**Ini prioritas tertinggi untuk direview pemilik modul** — berpotensi regresi luas pada form PO.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — Cabang `else` di `onchange_partner_id` adalah no-op
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order.py:19-22`
**Deskripsi:** Struktur method:
```python
if not self.partner_id.id:
    ...set_param(currency_id, self.currency_id.id)
elif self.partner_id.property_purchase_currency_id == self.currency_id:
    self.currency_id = self.partner_id.property_purchase_currency_id  # currency sudah sama, no-op efektif
    ...set_param(...)
else:
    self.currency_id = self.currency_id  # literally self-assignment, tidak melakukan apa-apa
    ...set_param(...)
```
Docstring method mengklaim "Update currency based on the partner's purchase currency" — tapi kondisi
di mana partner ADA dan currency partner BERBEDA dari currency PO saat ini (kasus paling umum yang
justru butuh update) tidak pernah benar-benar mengubah `self.currency_id`. Hanya `ir.config_parameter`
yang di-`set_param` di ketiga cabang.
**Dampak:** Currency PO tidak pernah otomatis berubah mengikuti partner (kecuali kebetulan sudah
sama) — kemungkinan berlawanan dengan tujuan modul ("multi currency" dari nama commit terakhir).
**Rekomendasi:** Klarifikasi ke pemilik modul: apakah ini bug (harusnya `self.currency_id =
self.partner_id.property_purchase_currency_id` di cabang `else`), atau disengaja (currency PO
memang tidak pernah dipaksa berubah, hanya dicatat ke config parameter untuk dipakai `convert_price`).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — `ir.config_parameter` "currency_id" sebagai state global lintas-user
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order.py:13-22`, `models/product_template.py:19-23`
**Deskripsi:** `onchange_partner_id` menulis `ir.config_parameter` key `"currency_id"` via
`sudo().set_param(...)` setiap kali partner/currency form PO berubah. `product_template.convert_price()`
membaca parameter GLOBAL yang sama (`get_param('currency_id')`) untuk menentukan currency tujuan
konversi harga. `ir.config_parameter` adalah tabel singleton PER-DATABASE, bukan per-user/per-session/
per-request — dua user yang membuka form PO berbeda dengan currency berbeda pada saat bersamaan akan
saling menimpa parameter ini.
**Dampak:** Tinggi pada environment multi-user konkuren — harga hasil `convert_price()` bisa memakai
currency dari PO/user LAIN, bukan currency PO yang sedang dibuka. Race condition klasik, sulit
direproduksi manual single-user tapi nyata secara arsitektur.
**Rekomendasi:** Currency seharusnya dilewatkan eksplisit sebagai parameter (sudah ada param
`currency_id` di beberapa call chain controller — periksa apakah `ir.config_parameter` ini betul-betul
diperlukan sebagai fallback, atau bisa dihapus sepenuhnya).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-05 — `convert_price()` gagal senyap (bukan error keras) kalau `get_param` kosong
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/product_template.py:22`
**Deskripsi:** **Direvisi setelah eksekusi nyata Step 04** (asumsi awal `TypeError` TERBUKTI SALAH —
`TC-F-01-03` gagal dengan "TypeError not raised"). Perilaku sebenarnya: `ir.config_parameter.get_param()`
defaultnya mengembalikan `False` (bukan `None`) kalau key tidak ada — jadi `int(get_param('currency_id'))`
= `int(False)` = `0`, BUKAN melempar exception. Kode lanjut jalan dengan `to_currency =
currency_obj.browse(0)` (currency yang tidak ada), lalu memanggil `from_currency._convert(...)` —
hasil eksekusi nyata (`docker-env/logs/odoo.log`, 2026-07-29):
```
BACKFILL F-05: convert_price(100.0, ...) with unset 'currency_id' param returned 100.0 without raising
```
Nilai dikembalikan PERSIS SAMA dengan input (100.0) — tidak crash, dan bukan angka yang "salah
konversi", melainkan konversi SENYAP DIABAIKAN (kemungkinan `_convert` core Odoo punya guard
internal yang no-op kalau `to_currency` tidak valid/kosong).
**Dampak:** Sedang-Tinggi — perilaku senyap ini tetap salah secara fungsional: user tidak
mendapat pesan/warning apapun bahwa harga yang ditampilkan BELUM dikonversi ke currency target
(padahal parameter target currency belum pernah ter-set). Di UI dialog konfigurator ini akan
terlihat seperti harga "normal" padahal masih dalam currency asal produk/vendor — berpotensi salah
tafsir user kalau currency asal berbeda dari yang diharapkan.
**Rekomendasi:** Guard eksplisit: kalau `get_param('currency_id')` falsy, fallback ke
`self.env.company.currency_id` alih-alih `int()` langsung.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-06 — `id_vendor` + DOM `getElementById('id_vendor_0')` sebagai state passing
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order.py` (field `id_vendor`), `views/purchase_order_views.xml:28-36`,
`static/src/js/product_configurator_dialog/product_configurator_dialog.js:41-43`
**Deskripsi:** Field `id_vendor` (Char, hidden via CSS `visibility:hidden`, `nolabel`) di-set lewat
onchange `partner_id`, lalu dialog JS membaca nilainya langsung dari DOM
(`document.getElementById('id_vendor_0')`) alih-alih melalui props/record data resmi OWL. Ini rentan
terhadap perubahan struktur view (id `_0` berasumsi field pertama di form) dan tidak scalable ke
multi-record (list view/multiple PO line dengan dialog terbuka bersamaan).
**Dampak:** Sedang — berfungsi di happy path single-form saat ini, tapi fragile terhadap perubahan
layout/urutan field dan berpotensi `null` (crash `.value` di baris 42) kalau elemen tidak ditemukan.
**Rekomendasi:** Lewatkan `id_vendor`/partner id sebagai prop resmi ke `ProductConfiguratorDialogPurchase`.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-07 — Harga supplier tidak difilter company
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `static/src/js/product_configurator_dialog/product_configurator_dialog.js` (`get_supplierinfo_id`,
`get_optional_product_prices`, `get_product_update_price`)
**Deskripsi:** Pencarian `product.supplierinfo` hanya filter `id in supplierinfo_id` (semua seller
dari `product_or_template.seller_ids`), tanpa filter company — di lingkungan multi-company, seller
info company lain ikut terhitung.
**Dampak:** Rendah kalau instance single-company (kasus umum), berpotensi salah harga di
multi-company.
**Rekomendasi:** Verifikasi apakah `seller_ids` sendiri sudah company-scoped oleh Odoo core (kemungkinan
ya, via `_compute`/domain default) — kalau begitu ini bukan gap nyata, cukup catat sebagai limitasi
observasi.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-08 — Label field `id_vendor` bentrok dengan label `id` bawaan
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/purchase_order.py` (field `id_vendor`, tidak ada `string=` eksplisit)
**Deskripsi:** Ditemukan via registry Odoo saat load module (Step 07, `docker-env/logs/odoo_g2.log`):
```
WARNING odoo.addons.base.models.ir_model: Two fields (id_vendor, id) of purchase.order() have the
same label: ID. [Modules: purchase_product_optional and purchase]
```
Field `id_vendor` tidak diberi `string=` eksplisit sehingga Odoo men-derive label "ID" dari nama
field (mengambil kata terakhir `vendor` → tidak, lebih tepatnya default label generation Odoo
mengambil "Id Vendor" biasanya jadi "Id Vendor", tapi warning menunjukkan hasilnya sama-sama "ID" —
kemungkinan karena field ini didaftarkan dengan `string='ID'` implisit dari kapitalisasi tertentu.
**Dampak:** Rendah — field ini sudah disembunyikan visual (`visibility:hidden` CSS di
`views/purchase_order_views.xml`), jadi label yang bentrok kemungkinan besar tidak pernah terlihat
user. Tetap berpotensi membingungkan di context lain (mis. "optional fields" column selector, atau
error message referencing field label yang ambigu).
**Rekomendasi:** Beri `string=` eksplisit yang unik pada field `id_vendor` (mis. "Vendor ID
(internal)").
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### Catatan tambahan — Percobaan Tour test headless (Step 07 Mode E), 2026-07-29

Setelah Step 07 awal (browser MCP blocked, lihat `07B_QA_AI_BROWSER.md`), dicoba pendekatan lain:
Odoo Tour test (`static/tests/tours/purchase_product_optional_tour.js` +
`tests/test_purchase_product_optional_tour.py`, `HttpCase.start_tour()`), yang seharusnya
dieksekusi via Chrome headless MILIK ODOO SENDIRI (bukan tool browser eksternal) — lihat
`USAGE_GUIDE.md` §Mode E untuk rasional lengkap.

**Hasil:** DUA dependency terpisah ternyata tidak tersedia di image resmi `odoo:17.0`:
1. **Paket OS `chromium`** — `docker-env/Dockerfile` (`apt-get install chromium`) GAGAL: "Package
   chromium is not available... no installation candidate". Tidak dicoba nama paket/repo alternatif
   (sesuai batas-workaround), langsung revert `docker-compose.yml` ke `image: odoo:17.0` polos.
2. **Paket Python `websocket-client`** — bahkan TANPA menyentuh masalah Chromium, test langsung
   di-`skipTest` OTOMATIS oleh Odoo sendiri dengan pesan jelas: `websocket-client module is not
   installed` (`docker-env/logs/odoo.log`, run final, 2026-07-29 09:05). Ini SATU LAGI dependency
   yang perlu ditambahkan (`pip3 install websocket-client` di image custom) SEBELUM Chromium bahkan
   relevan.

**Bukti positif:** test di-`skipTest` DENGAN RAPI (bukan gagal/error) — total tetap `0 failed, 0
error(s) of 13 tests`. Odoo sendiri yang mendeteksi dependency hilang dan skip otomatis, jadi
menambahkan file Tour test ini AMAN dimasukkan ke repo walau lingkungan saat ini belum bisa
menjalankannya sungguhan.

**Update (percobaan #2, sesi yang sama, 2026-07-29):** root cause paket `chromium` ditemukan —
image `odoo:17.0` based Ubuntu 22.04 (jammy), dan paket `chromium` Ubuntu di versi ini cuma stub
Snap (bukan binary asli), makanya "no installation candidate". Solusi: install **Google Chrome**
dari repo resmi Google (`google-chrome-stable`, bukan Snap) + `pip3 install websocket-client` di
`docker-env/Dockerfile`. **INI BERHASIL** — Chrome headless benar-benar menyala (`Chrome pid: 20`,
`Browser version: Chrome/150.0.7871.186`) dan Tour berhasil mengeksekusi 9 dari 11 langkah:
membuka app Purchase, membuat PO baru, isi vendor, tambah baris, pilih produk utama — **DAN
dialog konfigurator BENAR-BENAR TERBUKA OTOMATIS**, tervalidasi via screenshot nyata
(`test/07B_screenshot_dialog_confirmed.png`) yang menunjukkan "BACKFILL QA Main Product" +
"Add optional products" + "BACKFILL QA Optional Product" + tombol "+ Add", persis sesuai BR-01.

Tour gagal di langkah assertion berikutnya (`.modal td:contains("BACKFILL QA Optional Product")`,
timeout 10 detik) — TAPI screenshot pada momen kegagalan justru MEMBUKTIKAN teks itu ADA di DOM
persis seperti diharapkan. Kemungkinan besar ini quirk selector-engine Tour (compound selector/
timing), bukan bug modul — tidak dikejar lebih lanjut (screenshot sudah jadi bukti visual yang
cukup kuat, sesuai prinsip "jangan berputar-putar mengejar kesempurnaan tooling test").

**Update (percobaan #3, sesi yang sama, 2026-07-29) — PASS PENUH:** setelah percobaan #2 (Chrome
menyala tapi 2 langkah terakhir gagal), root-cause 3 bug DI SCRIPT TOUR (bukan modul) ditemukan
lewat baca source `web_tour` langsung, bukan tebakan:
1. Selector `.modal ...` redundan — Odoo `tour_compilers.js::findTrigger()` sudah otomatis scope
   pencarian ke modal yang sedang terbuka; prefix `.modal` tambahan berarti minta modal bersarang
   (tidak pernah ada) → selalu gagal. Dihapus dari 3 trigger yang relevan.
2. Assertion ke baris "Main Product" gagal karena field itu masih `<input>` dalam mode edit;
   `:contains()` tidak baca `.value` input. Diganti assert ke baris "Optional Product" yang sudah
   `mode: "readonly"`.
3. "Tour finished with an open form view in edition mode" — kurang step Simpan + race condition
   (RPC `web_save` sukses tapi Chrome ditutup sebelum UI update). Ditambah step klik Simpan + step
   tunggu breadcrumb berubah dari "New".

**Hasil akhir: `0 failed, 0 error(s) of 13 tests`, Tour PASS PENUH** (bukan skip, bukan sebagian) —
mencakup seluruh alur BR-01/BR-09: buka app → PO baru → isi vendor → tambah baris → pilih produk →
dialog terbuka otomatis → tambah optional product → confirm → baris tersimpan → PO ter-save.

**Kesimpulan final:** Mode E (Tour headless) TERBUKTI BISA JALAN PENUH di image ini dengan resep
Google Chrome + websocket-client (bukan lagi limitasi permanen, dan bukan lagi "sebagian pass").
BR-01/AC-01-01/BR-09 sekarang punya bukti end-to-end headless-Chrome sungguhan yang PASS, bukan
cuma HTTP response JSON. `docker-env/Dockerfile` + `static/tests/tours/purchase_product_optional_tour.js`
di repo ini SUDAH memakai versi final yang terbukti PASS.

---

## Limitasi Tool (kalau ada)

- *(diisi setelah Step 04 dijalankan — tergantung apakah environment docker berhasil membuktikan/
  membantah F-01/F-02 secara nyata, atau berhenti di desk-review)*
