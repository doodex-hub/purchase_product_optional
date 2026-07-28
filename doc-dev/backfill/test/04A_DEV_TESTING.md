# Dev Testing — purchase_product_optional

**Step:** 04 — Developer Testing (backfill)
**Module:** `purchase_product_optional`
**Spec ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-28

> Gabungan Smoke Test + Unit & Integration Spec. Tidak ada `04B_API_TEST.md` — diputuskan di Step
> 03B (4 route controller internal-only, lihat `test/03B_TEST_PLAN.md`).
>
> Modul ini TIDAK punya `tests/` sebelumnya — semua file test di bawah BARU ditulis BACKFILL
> (`purchase_product_optional/tests/__init__.py`, `test_purchase_order_currency.py`,
> `test_purchase_order_line_fields.py`, `test_controllers.py`, `test_tours.py`) plus test JS baru
> di `static/tests/` (`product_configurator_dialog_tests.js`, `purchase_product_field_tests.js`,
> `tours/purchase_product_optional_tour.js`) — **revisi 2026-07-28** setelah `odoo-testing-taxonomy.md`
> diperbaiki menambahkan JS Unit (QUnit)/Tour, lihat `03B_TEST_PLAN.md` §"Revisi 2".

---

## Status Eksekusi — PENTING, baca sebelum percaya tabel di bawah sebagai "Pass"

**Update 2026-07-28 (run #1, REAL, dijalankan dev via Mode B):** 11 TC Python (Unit+Integration)
SUDAH benar-benar dieksekusi — `docker-env/logs/odoo.log` dibaca langsung oleh BACKFILL. Hasil:
**9 pass, 1 fail, 1 error** dari 11 test.

| TC | Hasil nyata | Catatan |
|---|---|---|
| AC-02-01/02/03 (onchange currency) | ✅ Pass (3/3) | Mengonfirmasi F-02 sebagai bug nyata |
| AC-03-01 (convert_price short-circuit) | ✅ Pass | |
| AC-03-03 / F-05 (convert_price diduga crash) | ❌ **FAIL** — `_convert()` TIDAK crash | Hipotesis F-05 **TERBUKTI SALAH**, lihat `FINDINGS.md` F-05 |
| AC-04-01/02 (product_add_mode) | ✅ Pass (2/2) | F-01 dikonfirmasi GANDA — test pass + WARNING log Odoo sendiri (baris 920) |
| AC-08-01/02 (compute fields) | ✅ Pass (2/2) | |
| AC-07-01 (get_optional_products route) | ✅ Pass | HTTP 200 di log baris 906 |
| AC-09-01 (create_product route) | ⚠️ **ERROR** — bug di TEST SETUP, bukan kode modul | `create_variant` diubah SETELAH product memakainya → `UserError` asli Odoo. Sudah diperbaiki di `test_controllers.py` (set `create_variant='dynamic'` dari awal) |

**Instalasi modul bersih** — `sale_product_configurator`+`purchase_product_matrix` berhasil load
("Modules loaded." di log), jadi prasyarat Enterprise yang diduga di `docker-compose.yml` TERNYATA
tersedia di environment dev — tidak jadi masalah.

**Update 2026-07-28 (run #2, REAL)** — dev jalankan ulang setelah file JS+Tour+perbaikan
ditambahkan. Hasil: **2 failed, 0 error(s) of 12 tests** (naik dari 11 jadi 12 — `test_tours.py`
baru ikut kehitung). Detail:

| TC | Hasil run #2 | Catatan |
|---|---|---|
| AC-03-03 / F-05 | ❌ FAIL (sama seperti run #1) | Konsisten — F-05 tetap TIDAK TERBUKTI, bukan fluke run #1 |
| AC-09-01 (create_product route) | ❌ FAIL (beda dari run #1 yang ERROR) | Bug BARU ketemu: kombinasi test-nya sendiri salah — mengoper 2 ptav sekaligus untuk 1 attribute line non-multi (bukan kombinasi valid), `_create_product_variant` balik `False`. **Sudah diperbaiki** — ambil 1 ptav saja |
| Tour (`test_purchase_product_optional_happy_path_tour`) | ⚠️ **SKIPPED** (bukan pass/fail) — `"websocket-client module is not installed"` | Gap environment (paket Python untuk Chrome DevTools Protocol), BUKAN soal kode/selector tour. Ditambahkan instruksi instalasi di `docker-compose.yml` |
| QUnit (`product_configurator_dialog_tests.js`, `purchase_product_field_tests.js`) | ⚠️ **TIDAK ADA HASIL SAMA SEKALI** — bundle `web.qunit_suite_tests` berhasil di-generate (baris ~983 log, artinya JS-nya valid syntax, tidak ada error saat bundling) TAPI tidak ada runner Python yang benar-benar MENJALANKAN suite-nya dan melaporkan pass/fail | **Gap ditemukan**: asumsi awal "QUnit otomatis ikut `--test-tags`" TERNYATA SALAH — perlu wrapper eksplisit. **Sudah ditambahkan:** `tests/test_qunit.py` (`HttpCase.browser_js` ke `/web/tests?module=purchase_product_optional`), pola umum yang dipakai addon Odoo yang punya QUnit sendiri |
| 9 TC lain (AC-02, AC-03-01, AC-04, AC-07-01, AC-08) | ✅ Pass (konsisten run #1) | |

**Update 2026-07-28 (run #3, GAGAL TOTAL — bukan gagal test, container tidak pernah start)** —
percobaan `docker compose exec odoo pip3 install ...` gagal karena container sudah exit
(`--stop-after-init`). Fix pertama: override `entrypoint: []` + `command: bash -c "pip3 install
... && odoo ..."`. INI SALAH — entrypoint resmi image `odoo:17.0` yang menerjemahkan env var
`HOST/USER/PASSWORD` jadi koneksi db (`db:5432`) ikut terbuang, container gagal start SEBELUM
sempat menulis satu baris log pun (dikonfirmasi: mtime `odoo.log` tidak berubah sama sekali
setelah run ini). Di-revert.

**Update 2026-07-28 (run #4, REAL, berhasil)** — fix benar: `websocket-client` di-install di
layer image lewat `docker-env/Dockerfile` baru (`build: .` menggantikan `image: odoo:17.0` di
compose), command dikembalikan persis seperti run #1/#2. Hasil: **1 failed, 0 error(s) of 13
tests**. Tour tidak lagi skip karena websocket-client (fix berhasil), tapi sekarang skip dengan
pesan BARU **"Chrome executable not found"** (begitu juga `test_qunit.py`) — gap terpisah: image
`odoo:17.0` tidak menyertakan Chrome/Chromium. Satu-satunya FAIL tersisa: `test_ac_03_03_...`
(F-05) — tetap gagal SESUAI HARAPAN karena test itu masih menuntut crash yang sudah terbukti
tidak terjadi (belum dikoreksi di titik ini). Run #5 (dev re-run manual, khawatir proses
"ke-kill") menghasilkan angka identik — bukan run baru yang signifikan, cuma re-konfirmasi run #4.

**Update 2026-07-28 (run #6, GAGAL saat build, tidak sampai jalan test)** — percobaan menambah
`apt-get install chromium` ke `Dockerfile` supaya Tour/QUnit tidak skip GAGAL: `exit code: 100`
(package/repo tidak tersedia di base image ini). Sesuai batas workaround di `CLAUDE.md` (satu
percobaan wajar, gagal → stop, jangan coba variasi lain), **TIDAK dikejar lebih lanjut** — di-
revert ke `Dockerfile` versi run #4 (websocket-client saja). Tour + QUnit tetap SKIP karena Chrome
untuk SISA sesi ini — dicatat sebagai limitasi lingkungan permanen di `FINDINGS.md`, bukan gate
blocker (lihat run #7).

**Update 2026-07-28 (run #7, REAL, BASELINE FINAL — dijadikan dasar penutupan gate Step 04)** —
setelah `Dockerfile` di-revert dan test F-05 dikoreksi jadi
`test_ac_03_03_convert_price_real_conversion_no_crash` (assert hasil float, bukan lagi
`assertRaises(TypeError)`, sesuai temuan nyata run #1/#2). Hasil: **0 failed, 0 error(s) of 13
tests** — SEMUA 11 test Python (9 Unit + 2 Integration) PASS bersih; Tour + QUnit (2 dari 13)
tetap SKIP karena "Chrome executable not found" (limitasi lingkungan, dicatat, tidak dikejar lagi).
Ini baseline final Step 04 — lihat `CLAUDE.md` §Status untuk keputusan penutupan gate.

**Mode D (stub pure-logic) TIDAK BISA dipakai untuk modul ini** — semua method Python yang diuji
menyentuh `self.env` (lihat `FINDINGS.md` §Limitasi Tool). Satu-satunya jalan konfirmasi nyata:
**Mode B** (docker-compose, dijalankan dev).

**Tambahan (2026-07-28): test JS (QUnit) & Tour punya prasyarat TERPISAH dari test Python** — butuh
Chrome/Chromium headless tersedia di container (lihat komentar baru di `docker-env/docker-compose.yml`).
Kalau container tidak punya Chrome, test Python (Unit/Integration) tetap bisa jalan normal, tapi
QUnit/Tour akan gagal karena browser tidak ditemukan — bukan berarti logic-nya salah, itu gap
environment yang terpisah dari gap kode.

### Serah-terima ke dev — command persis

`docker-env/docker-compose.yml` sudah diinstansiasi di root repo (sibling `doc-dev/`). **Baca
komentar prasyarat di baris atas file itu dulu** — modul ini depends `sale_product_configurator`
yang setahu BACKFILL Enterprise-only, image `odoo:17.0` polos mungkin perlu diganti ke image
Enterprise Doodex.

1. Buka terminal di `docker-env/`:
   ```
   cd docker-env
   ```
2. Jalankan (pakai `--build` karena service `odoo` sekarang `build: .` dari `Dockerfile` lokal,
   bukan `image:` langsung — lihat komentar di `Dockerfile`/`docker-compose.yml` untuk histori):
   ```
   docker compose up --build
   ```
3. Tunggu sampai `Modules loaded.` muncul di log, lalu proses akan berhenti sendiri
   (`--stop-after-init`). Kalau ada `Traceback` SEBELUM `Modules loaded.` = instalasi modul
   sendiri gagal (bukan soal test — cek pesan error, kemungkinan besar terkait prasyarat
   Enterprise di atas).
4. Beri tahu BACKFILL setelah selesai ("sudah") — AI akan baca `docker-env/logs/odoo.log`
   langsung (ter-mount, tidak perlu copy-paste manual).
5. Setelah AI baca hasil, matikan container:
   ```
   docker compose down
   ```

---

## 1. Smoke Test (happy path)

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Product Configurator dialog | Buka PO, pilih vendor, pilih produk configurable → dialog terbuka, pilih atribut+optional product, confirm → baris PO tersimpan dengan harga sesuai vendor | Mode B (G2, server hidup) / AI-in-the-loop (07B) | ☐ Pass / ☐ Fail — **belum dijalankan** |
| 2 | Edit konfigurasi tersimpan | Buka kembali baris yang sudah dikonfigurasi → dialog terbuka dengan kombinasi lama | Mode B (G2) / AI-in-the-loop (07B) | ☐ Pass / ☐ Fail — **belum dijalankan** |

---

## 2. Unit & Integration Test Specification

### 2a. `models/purchase_order.py` + `models/product_template.py` — Currency (BR-02/BR-03)

**File test:** `tests/test_purchase_order_currency.py`

#### TC-CUR-01 — `onchange_partner_id`

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Tanpa `partner_id` | `currency_id` tidak berubah, config param global ditulis dari nilai yang sudah ada (AC-02-01) | `[HASIL-BACA]` |
| 02 | Unit | Partner currency == currency PO | Assignment no-op observable (AC-02-02) | `[HASIL-BACA]` |
| 03 | Unit | Partner currency != currency PO | `currency_id` PO **TETAP TIDAK BERUBAH** — mendokumentasikan F-02 (AC-02-03) | `[PERLU-KEPUTUSAN]` |

#### TC-CP-01/02 — `convert_price`

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | `from_currency` == config param global | Harga dikembalikan tanpa konversi (AC-03-01) | `[HASIL-BACA]` |
| 02 | Unit | `from_currency` != config param global (konversi sungguhan) | **REVISI (F-05 tidak terbukti, 3× run nyata):** `convert_price` mengembalikan float hasil konversi TANPA crash (AC-03-03). Test `test_ac_03_03_convert_price_real_conversion_no_crash` — PASS di run #7 | `[HASIL-BACA]` (sebelumnya `[PERLU-KEPUTUSAN]`, sudah ditutup) |

### 2b. `models/purchase_order_line.py` — Field & Compute (BR-04/BR-08)

**File test:** `tests/test_purchase_order_line_fields.py`

#### TC-F-01 — `product_add_mode` (F-01)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Modul ter-load | Tidak ada `SyntaxError` (AC-04-01) | `[HASIL-BACA]` |
| 02 | Unit | Cek `_fields` dict `purchase.order.line` | `'product_add_mode'` TIDAK ADA di `_fields` (AC-04-02, F-01) | `[PERLU-KEPUTUSAN]` |

#### TC-F-02 — Compute attribute values (BR-08)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Unit | Line punya `product_custom_attribute_value_ids`, lalu `product_id` diganti | Value lama dibersihkan (AC-08-01) | `[HASIL-BACA]` |
| 02 | Unit | Line punya `product_no_variant_attribute_value_ids`, lalu `product_id` diganti | Value lama dibersihkan (AC-08-02) | `[HASIL-BACA]` |

### 2c. `controllers/main.py` — Route JSON (BR-07/BR-09)

**File test:** `tests/test_controllers.py`

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | `get_optional_products` dipanggil dengan produk yang punya `optional_product_ids` | Response 200, `optional_product_ids` ikut dikembalikan (AC-07-01) | `[HASIL-BACA]` |
| 02 | Integration | `create_product` dipanggil dengan kombinasi dynamic attribute | Response 200, `product.product` baru dibuat, id dikembalikan (AC-09-01) | `[HASIL-BACA]` |

> Catatan: `test_ac_09_01_create_product_route` mengubah `create_variant` attribute jadi
> `'dynamic'` SETELAH attribute_line dibuat di `setUpClass` — kalau ternyata Odoo tidak
> merefleksikan perubahan ini otomatis ke `product_template_value_ids.create_variant` (perlu
> re-fetch/invalidate cache), test ini bisa perlu penyesuaian setelah run pertama. Ini bagian
> normal dari "belum dieksekusi" — dicatat di sini supaya tidak mengejutkan saat Mode B jalan.

### 2d. JS Unit (QUnit) & Tour — BARU 2026-07-28 (BR-01/BR-05/BR-06/BR-07/BR-09)

**File test:** `static/tests/product_configurator_dialog_tests.js`,
`static/tests/purchase_product_field_tests.js`, `static/tests/tours/purchase_product_optional_tour.js`
+ wrapper `tests/test_tours.py`.

> Ditambahkan setelah `odoo-testing-taxonomy.md` diperbaiki (lihat `03B_TEST_PLAN.md` §"Revisi 2")
> — sebelumnya 13 AC berikut dianggap "tidak bisa ditest sama sekali selain manual", ternyata bisa
> lewat mekanisme resmi Odoo (QUnit + Tour) yang sebelumnya tidak dipertimbangkan.

| # | Tipe | File | Condition | Expected | Provenance | Risiko sintaks |
|---|---|---|---|---|---|---|
| 01 | JS Unit | `product_configurator_dialog_tests.js` | `_isPossibleCombination` dengan ptav excluded/tidak (AC-09-02) | true/false sesuai kombinasi | `[HASIL-BACA]` | Rendah (pure function via `.call()`, tanpa mount) |
| 02 | JS Unit | `product_configurator_dialog_tests.js` | `_removeProduct` pada optional product 1 vs 2 parent (AC-07-01/02) | Parent tunggal → child ikut terhapus; multi-parent → child bertahan | `[HASIL-BACA]` | Rendah-Sedang (`.call()` dengan fake `this.state`) |
| 03 | JS Unit | `product_configurator_dialog_tests.js` | `get_product_update_price` dengan `id_vendor` cocok/tidak cocok supplierinfo (AC-05-01/02) | Harga ikut vendor yang cocok, fallback ke supplierinfo pertama kalau tidak (BUKAN standard_price) | `[HASIL-BACA]` | Sedang (mock `orm.call` manual) |
| 04 | JS Unit | `product_configurator_dialog_tests.js` | Elemen `id_vendor_0` tidak ada di DOM (AC-06-02, F-04) | `TypeError` saat baca `.value` | `[PERLU-KEPUTUSAN]` | Rendah (test penanda perilaku JS generik, bukan mount OWL) |
| 05 | JS Unit | `purchase_product_field_tests.js` | `_onProductTemplateUpdate` — 6 skenario `result` (single variant, optional products, warning block/warning, mode configurator/matrix) (AC-01-01 s/d 06) | Cabang buka dialog/grid/update record sesuai `03B_TEST_PLAN.md` | `[HASIL-BACA]` | **TINGGI** — bergantung `super._onProductTemplateUpdate` via `patch()` tetap resolve benar lewat `.call(fakeThis)`, belum terverifikasi |
| 06 | Tour | `purchase_product_optional_tour.js` + `test_tours.py` | Alur penuh: buka PO → pilih vendor → pilih produk configurable → dialog terbuka → confirm → baris tersimpan (Smoke #1) | Tour lulus tanpa error step | `[HASIL-BACA]` | **TINGGI** — selector CSS (`.o_field_widget[name=...]`, dst) belum diverifikasi ke DOM modul ini sungguhan |

**Prasyarat environment TERPISAH:** semua 6 TC di atas butuh Chrome/Chromium headless di container
(lihat §Status Eksekusi di atas) — beda dari 11 TC Python yang cuma butuh Odoo+Postgres.

### 2e. Test Matrix Summary

| Area | Unit | JS Unit | Integration | Tour | Provenance |
|---|---|---|---|---|---|
| Currency onchange (BR-02) | ✓ | | | | `[HASIL-BACA]` / `[PERLU-KEPUTUSAN]` (AC-02-03) |
| Currency conversion (BR-03/F-05) | ✓ | | | | `[PERLU-KEPUTUSAN]` |
| `product_add_mode` dead field (F-01) | ✓ | | | | `[PERLU-KEPUTUSAN]` |
| Compute attribute values (BR-08) | ✓ | | | | `[HASIL-BACA]` |
| Controller routes (BR-07/BR-09) | | | ✓ | | `[HASIL-BACA]` |
| Dialog trigger/branching (BR-01) | | ✓ | | ✓ | `[HASIL-BACA]` |
| Vendor pricing (BR-05/BR-06) | | ✓ | | ✓ | `[HASIL-BACA]` / `[PERLU-KEPUTUSAN]` (F-04) |
| Optional products rekursif (BR-07) | | ✓ | ✓ (data layer) | | `[HASIL-BACA]` |

### 2f. Ringkasan

- Unit (Python): 9 TC (`test_purchase_order_currency.py` ×5, `test_purchase_order_line_fields.py`
  ×4) — jalankan lewat Mode B: `docker compose up` di `docker-env/` (lihat command lengkap di
  §Status Eksekusi di atas).
- Integration (Python): 2 TC (`test_controllers.py`) — sama, satu run `--test-enable` mencakup
  keduanya.
- JS Unit (QUnit): 5 file-level scenario group (lihat §2d) — butuh Chrome headless, risiko sintaks
  bervariasi per file (lihat kolom "Risiko sintaks").
- Tour: 1 skenario (`test_tours.py`) — butuh Chrome headless, risiko TINGGI soal selector CSS.
- **0 AC tersisa TANPA test Python/JS sama sekali** (revisi dari 13 AC di draft awal Test Plan,
  setelah `odoo-testing-taxonomy.md` diperbaiki menambah JS Unit/Tour). Step 07 (AI-interaktif +
  AI-Browser) tetap dijalankan sebagai verifikasi visual — QUnit `.call()`-style TIDAK mem-verify
  rendering DOM sungguhan (kecuali TC JS Unit #04), jadi bukan pengganti penuh AI-Browser.
- **STATUS FINAL Step 04 (run #7, baseline):** 11/11 test Python (Unit+Integration) PASS bersih.
  2 TC JS (QUnit+Tour) TIDAK PERNAH benar-benar tereksekusi di sesi ini — Chrome tidak tersedia di
  image `odoo:17.0`, satu percobaan menambahkannya (`apt-get install chromium`) gagal dan tidak
  dikejar lebih lanjut sesuai batas workaround `CLAUDE.md`. Gate Step 04 ditutup berdasarkan cakupan
  Unit/Integration yang lengkap dan bersih; verifikasi visual dialog (termasuk F-04) dilimpahkan ke
  Step 07 (AI-Browser) sebagai jalur alternatif — lihat `FINDINGS.md` §Limitasi Tool.
