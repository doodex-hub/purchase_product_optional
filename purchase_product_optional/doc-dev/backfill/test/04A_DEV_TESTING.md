# Dev Testing — purchase_product_optional

**Step:** 04 — Developer Testing (backfill)
**Module:** `purchase_product_optional`
**Spec ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-29 (isi awal, tunggu hasil eksekusi docker — lihat §3)

> Modul sebelumnya TIDAK punya `tests/` sama sekali — semua test di bawah BARU ditulis sesi ini
> (`tests/test_purchase_product_optional.py`), tidak ada method existing untuk diklasifikasi
> Lengkap/Stub.

---

## 1. Smoke Test (happy path)

**Cara Eksekusi:** Mode C — AI (Claude Code CLI) menjalankan `docker compose up` langsung dari
`docker-env/` (background), membaca `docker-env/logs/odoo.log` untuk hasil nyata (bukan desk-review).

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Instalasi modul | `-i purchase_product_optional` sukses tanpa Traceback, "Modules loaded." muncul | Mode C | ☑ Pass |
| 2 | Currency conversion | `convert_price()` currency sama → tanpa konversi | Mode C | ☑ Pass |
| 3 | Attribute value compute | Custom/no-variant value ter-prune saat produk baris PO diganti | Mode C | ☑ Pass |

---

## 2. Unit & Integration Test Specification

**File test:** `tests/test_purchase_product_optional.py`

### 2a. Currency Conversion — `models/product_template.py::convert_price`

#### TC-F-01 — `convert_price` currency sama vs berbeda vs param kosong

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | `from_currency == to_currency` (dari `ir.config_parameter`) | Harga dikembalikan tanpa konversi (early return) | `[HASIL-BACA]` |
| 02 | Unit | `from_currency != to_currency`, rate 2.0 ter-set | Harga terkonversi (berbeda dari input) | `[HASIL-BACA]` |
| 03 | Unit | `ir.config_parameter` key `currency_id` tidak pernah di-set | `TypeError` (`int(None)`) — ref F-05 | `[PERLU-KEPUTUSAN]` |

### 2b. Onchange Partner/Currency — `models/purchase_order.py::onchange_partner_id`

#### TC-BR-04 — Sinkronisasi currency partner

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Partner di-set, `property_purchase_currency_id` beda dari `currency_id` PO saat ini | `currency_id` PO **TIDAK berubah** (self-assignment no-op) — ref F-03 | `[PERLU-KEPUTUSAN]` |
| 02 | Unit | Cek MRO `purchase.order` untuk semua class yang definisikan `onchange_partner_id` | Log daftar class (lihat §3 untuk hasil aktual) — ref F-02 | `[PERLU-KEPUTUSAN]` |

### 2c. Attribute Value Compute — `models/purchase_order_line.py`

#### TC-BR-07 — Prune custom/no-variant value saat produk diganti

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Baris punya custom attribute value utk template A, `product_id` diganti ke template B | `product_custom_attribute_value_ids` kosong setelah `_compute_custom_attribute_values()` | `[HASIL-BACA]` |
| 02 | Unit | Baris punya no-variant PTAV utk template A, `product_id` diganti ke template B | `product_no_variant_attribute_value_ids` kosong setelah `_compute_no_variant_attribute_values()` | `[HASIL-BACA]` |
| 03 | Unit | Baris tanpa `product_id` sama sekali | Kedua field kosong/`False` | `[HASIL-BACA]` |

### 2d. Field Registration — `models/purchase_order_line.py`

#### TC-BR-08 — `product_add_mode`

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Registry `purchase.order.line` dimuat | `'product_add_mode' not in _fields` — ref F-01 | `[PERLU-KEPUTUSAN]` |

### 2e. View Arch — `views/purchase_order_views.xml`

#### TC-BR-11 — Kolom tree PO line

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Merged form view `purchase.order` (`get_view`) | `product_template_id` punya `column_invisible="0"`, `product_id` punya `optional="hide"` | `[HASIL-BACA]` |

### 2f. Controller Routes — `controllers/main.py` (Integration, HttpCase)

#### TC-BR-01/09 — JSON-RPC routes

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | POST `/purchase_product_optional/get_values_purchase` utk template dgn 1 optional product | Response berisi `optional_products` (1 item, `product_tmpl_id` cocok) + `exclusions` di produk utama | `[HASIL-BACA]` |
| 02 | Integration | POST `/purchase_product_optional/create_product` utk template dgn atribut `create_variant='dynamic'` | Variant baru (`product.product`) benar-benar dibuat, id valid | `[HASIL-BACA]` |

### 2g. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| Currency conversion | ✓ | | `[HASIL-BACA]`/`[PERLU-KEPUTUSAN]` (F-05) |
| Onchange partner/currency | ✓ | | `[PERLU-KEPUTUSAN]` (F-02/F-03) |
| Attribute value compute | ✓ | | `[HASIL-BACA]` |
| `product_add_mode` field | ✓ | | `[PERLU-KEPUTUSAN]` (F-01) |
| View arch kolom | ✓ | | `[HASIL-BACA]` |
| Controller JSON-RPC routes | | ✓ | `[HASIL-BACA]` |

### 2h. Ringkasan

- Unit: 10 TC — dijalankan via `odoo -i purchase_product_optional --test-enable --test-tags=/purchase_product_optional --stop-after-init` (Mode C, docker).
- Integration: 2 TC (`HttpCase`) — server nyata hidup di container yang sama (`--test-enable` menjalankan semua test tag modul, termasuk `HttpCase`, dalam satu proses).

---

## 3. Hasil Eksekusi Nyata (Mode C — docker, dijalankan AI langsung)

> Command yang dijalankan AI:
> ```
> cd docker-env && docker compose up --build
> ```
> (background, log dibaca dari `docker-env/logs/odoo.log`, lalu `docker compose down -v` setelah
> hasil didapat)

**Run #1 (2026-07-29 08:22-08:24 UTC)** — hasil: `3 failed, 0 error(s) of 12 tests`. 3 kegagalan
diperiksa satu per satu:

| Test | Penyebab kegagalan | Kategori |
|---|---|---|
| `test_convert_price_different_currency_converts` | `res.currency().search(...)` tanpa `active_test=False` — di DB single-currency, semua currency lain (~170 record) inactive by default, search hanya melihat yang active → recordset kosong | **Bug di test BACKFILL sendiri**, bukan bug modul — diperbaiki |
| `test_currency_not_synced_to_partner_purchase_currency` | Sama seperti di atas | **Bug di test BACKFILL sendiri** — diperbaiki |
| `test_convert_price_param_not_set_raises_typeerror` | Asumsi awal (`int(None)` → `TypeError`) SALAH — `ir.config_parameter.get_param()` defaultnya `False`, bukan `None` | **Asumsi F-05 di FINDINGS.md salah**, direvisi berdasarkan perilaku nyata (lihat F-05) |

Test diperbaiki (`active_test=False` pada search currency, assertion F-05 direvisi jadi
"returns without raising" + log nilai aktual), docker di-rebuild dari volume bersih
(`docker compose down -v` lalu `up` ulang).

**Run #2 (2026-07-29 08:27 UTC, FINAL)** — hasil:
```
odoo.tests.stats: purchase_product_optional: 24 tests 1.51s 1311 queries
odoo.tests.result: 0 failed, 0 error(s) of 12 tests when loading database 'purchase_product_optional_test'
```
**0 failed, 0 error(s) dari 12 test method** (TransactionCase + HttpCase), semua tag `post_install`.
Log confirmations penting yang terekam:

- `Field purchase.order.line.product_no_variant_attribute_value_ids: unknown parameter
  'product_add_mode', if this is an actual parameter you may want to override the method
  _valid_field_parameter...` → **mengonfirmasi F-01** (registry Odoo sendiri menganggap
  `product_add_mode` sebagai parameter asing, bukan field). Modul tetap berhasil ter-install
  (warning, bukan error fatal).
- `BACKFILL F-02: classes defining purchase.order.onchange_partner_id:
  ['odoo.addons.purchase_product_optional.models.purchase_order.PurchaseOrder',
  'odoo.addons.purchase.models.purchase_order.PurchaseOrder']` → **mengonfirmasi F-02**: Odoo core
  `purchase` module BENAR punya `onchange_partner_id` sendiri, dan module ini menimpanya total.
- `BACKFILL F-05: convert_price(100.0, ...) with unset 'currency_id' param returned 100.0 without
  raising` → **merevisi F-05**: bukan `TypeError`, melainkan silent no-op (harga dikembalikan utuh
  tanpa konversi, tanpa warning).
- 2 `HttpCase` (route controller) sukses: `POST /purchase_product_optional/create_product
  HTTP/1.1" 200` dan `POST /purchase_product_optional/get_values_purchase HTTP/1.1" 200` —
  keduanya dipanggil via HTTP nyata terhadap server yang hidup di container, bukan mock.

**Verdict Step 04:** ✔️ Lulus gate — hasil test REAL (Mode C, bukan desk-review), 12/12 test pass,
3 finding (F-01, F-02, F-05) terkonfirmasi/direvisi berdasarkan bukti eksekusi nyata, bukan cuma
baca kode. Environment docker-env dibersihkan (`docker compose down -v`) setelah selesai.

---

## 4. Tambahan — Tour test headless (Step 07 Mode E), run terpisah 2026-07-29

Setelah Step 07 awal, ditambahkan `tests/test_purchase_product_optional_tour.py` (Tour test,
lihat `USAGE_GUIDE.md` §Mode E). Dua percobaan Dockerfile:

**Percobaan #1 — GAGAL:** `apt-get install chromium` polos → "no installation candidate" (paket
Ubuntu `chromium` di image ini cuma stub Snap). Run tanpa Chromium: `0 failed, 0 error(s) of 13
tests` — Tour test skip rapi (`websocket-client module is not installed`, ketahuan duluan sebelum
Chromium relevan).

**Percobaan #2 — BERHASIL:** ganti resep ke **Google Chrome resmi** (`google-chrome-stable` dari
repo Google, bukan paket Ubuntu) + `pip3 install websocket-client`. Chrome headless benar-benar
menyala:
```
Chrome pid: 20
Browser version: Chrome/150.0.7871.186
```
Tour berjalan 9/11 langkah sukses (buka app Purchase → buat PO → isi vendor → tambah baris → pilih
produk → dialog konfigurator terbuka otomatis), gagal di 2 langkah TERAKHIR karena 3 bug DI SCRIPT
TOUR SAYA SENDIRI (bukan di modul) — masing-masing ditemukan & diperbaiki lewat root-cause analysis
langsung ke source `web_tour`, bukan tebak-tebakan:

1. **Selector `.modal ...` redundan** — Odoo `tour_compilers.js::findTrigger()` SUDAH otomatis
   scope pencarian ke `$visibleModal` begitu ada modal terbuka. Menulis `.modal td:contains(...)`
   berarti minta modal BERSARANG di dalam modal (tidak pernah ada) → selalu 0 match. Fix: hapus
   prefix `.modal` dari 3 trigger yang sudah otomatis di-scope.
2. **Assertion baris "Main Product" gagal** — field `product_template_id` baris itu masih dalam
   mode edit (`<input>`) tepat setelah Confirm; `:contains()` cuma baca `textContent`, BUKAN
   `.value` sebuah `<input>`. Fix: assert ke baris "Optional Product" (yang di-set `mode:
   "readonly"` oleh kode modul sendiri via `addNewRecord`), bukan baris yang masih fokus.
3. **"Tour finished with an open form view in edition mode"** — Tour tidak pernah klik Simpan;
   klik Simpan pertama juga race condition (RPC `web_save` sukses tapi Chrome ditutup ~130ms
   sebelum UI sempat update). Fix: tambah step klik `.o_form_button_save` + step tunggu breadcrumb
   berubah dari "New" (tanda `web_save` benar-benar selesai).

**Hasil akhir setelah ketiga fix:**
```
odoo.addons.....TestPurchaseProductOptionalTour.browser: test successful
odoo.tests.result: 0 failed, 0 error(s) of 13 tests when loading database 'purchase_product_optional_test'
```
**Tour benar-benar PASS penuh** — bukan cuma "sebagian jalan" — mencakup: buka app → buat PO → isi
vendor → tambah baris → pilih produk utama → dialog konfigurator terbuka otomatis (BR-01) →
optional product tampil dengan tombol Add → klik Add → klik Confirm → baris optional product
benar-benar tersimpan di PO → PO benar-benar ter-save (`web_save` RPC + breadcrumb update).

**Kesimpulan:** Mode E TERBUKTI BISA dieksekusi nyata DAN PASS BERSIH di lingkungan ini — bukan
lagi limitasi permanen, dan bukan lagi "sebagian pass". BR-01/AC-01-01/BR-09 (dialog auto-open +
tambah optional product + confirm menyimpan baris baru) sekarang punya bukti end-to-end headless-
Chrome sungguhan yang PASS, melengkapi bukti HTTP (`HttpCase`) yang sudah ada di §2f/§3. Screenshot
dari percobaan sebelumnya (`test/07B_screenshot_dialog_confirmed.png`) tetap relevan sebagai bukti
visual dialog yang terbuka.
