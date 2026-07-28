# QA Testing — purchase_product_optional

**Step:** 07 — QA Testing (backfill, TANPA UAT — BACKFILL berhenti di sini)
**Ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`, `test/03B_TEST_PLAN.md`, `test/04A_DEV_TESTING.md`
**Tanggal:** 2026-07-28

> File ini sekaligus jadi skenario, tracker, DAN laporan (tidak ada file business-flow/QA-report
> terpisah — lihat `doc-dev-backfill/templates/test/07_QA_TESTING.md` untuk rasional).

---

## 1. Area / AC yang Harus Dicakup

Diturunkan dari `01A_FUNCTIONAL_SPEC.md` BR-01..BR-09 / `01B_ACCEPTANCE_CRITERIA.md` (25 AC total):

- [x] AC-01 (6 AC) — Trigger dialog configurator (BR-01)
- [x] AC-02 (3 AC) — Update currency dari partner (BR-02, F-02)
- [x] AC-03 (3 AC) — Konversi harga (BR-03, F-03/F-05)
- [x] AC-04 (2 AC) — Field `product_add_mode` dead code (BR-04, F-01)
- [x] AC-05 (3 AC) — Harga per-vendor supplierinfo (BR-05)
- [x] AC-06 (2 AC) — Vendor ID dari DOM (BR-06, F-04)
- [x] AC-07 (2 AC) — Optional products rekursif (BR-07)
- [x] AC-08 (2 AC) — Sinkronisasi attribute value (BR-08)
- [x] AC-09 (2 AC) — Pembuatan varian dynamic saat confirm (BR-09)

**Pembagian metode verifikasi (lihat `04A_DEV_TESTING.md` §Status Eksekusi untuk detail run):**
AC-02, AC-03, AC-04, AC-07, AC-08, AC-09-01 sudah **benar-benar dieksekusi nyata** lewat Unit/
Integration test Python (Mode B, run #7, 11/11 pass bersih) — Step 07 di sini MERANGKUM hasil itu
sebagai bukti, tidak mengulang eksekusi. AC-01, AC-05, AC-06, AC-09-02 murni logic JS
(`purchase_product_field.js`/`product_configurator_dialog.js`) yang QUnit-nya **tertulis tapi TIDAK
PERNAH tereksekusi** (Chrome tidak tersedia di image Mode B, lihat `FINDINGS.md` §Limitasi Tool) —
untuk kelompok ini, Step 07 memakai **AI-interaktif (desk-review kode)** sebagai metode default,
dan `07B_QA_AI_BROWSER.md` sebagai verifikasi tambahan KALAU koneksi browser tersedia.

---

## 2. Format Skenario

Lihat `doc-dev-backfill/templates/test/07_QA_TESTING.md` §2 (dipakai bersama `07B_QA_AI_BROWSER.md`).

---

## 3. Skenario

### S-01: Trigger dialog configurator vs grid vs update langsung (AC-01-01..06)
**Precondition:** Baca `purchase_product_optional/static/src/js/purchase_product_field/purchase_product_field.js` method `_onProductTemplateUpdate` (patch atas `PurchaseOrderLineProductField` bawaan `purchase_product_matrix`).
**Mode eksekusi:** Desk-review (AI-interaktif) — QUnit `purchase_product_field_tests.js` (6 skenario, risiko sintaks TINGGI karena pola `patch()`/`super` via `.call(fakeThis)`) tertulis tapi TIDAK tereksekusi (Chrome tidak tersedia di Mode B, lihat `FINDINGS.md`).
**Steps:**
1. Baca cabang `result.product_id` ada + tidak ada optional products → assign langsung, tidak buka dialog (AC-01-02).
2. Baca cabang `purchase_warning.type === 'block'` → `WarningDialog` + reset `product_template_id` ke `false` (AC-01-03).
3. Baca cabang `purchase_warning.type === 'warning'` → notifikasi non-blocking, lanjut ke pengecekan `result.mode` (AC-01-04).
4. Baca cabang `result.mode` kosong/`'configurator'` → `_openProductConfigurator()` (AC-01-01/05).
5. Baca cabang `result.mode !== 'configurator'` → `_openGridConfigurator()` (AC-01-06).
**Expected:** Kelima cabang if/elif konsisten dengan deskripsi AC-01-01..06 di `01B_ACCEPTANCE_CRITERIA.md` — tidak ada cabang yang salah urutan/logic terbalik.
**Actual:** Dikonfirmasi via pembacaan kode penuh — kelima cabang cocok persis dengan yang didokumentasikan di `01A_FUNCTIONAL_SPEC.md` BR-01 (ditulis saat Step 01, dibaca ulang saat Step 07, tidak ada perubahan kode di antaranya). Tidak ada indikasi bug pada urutan percabangan itu sendiri — risiko yang ada murni risiko SINTAKS test QUnit (belum tereksekusi), bukan risiko pada kode modul.
**Status:** ☐ Pass (desk-review) / **TIDAK Pass via eksekusi nyata** — lihat §4 keterbatasan.
**Provenance:** `[HASIL-BACA]`

### S-02: Update currency dari partner (AC-02-01..03, F-02)
**Precondition:** Test `test_purchase_order_currency.py::TestPurchaseOrderCurrency` sudah dieksekusi real (Mode B run #7).
**Mode eksekusi:** Mode B (docker, real execution) — sudah dilakukan di Step 04, dirangkum di sini.
**Steps:** Lihat `04A_DEV_TESTING.md` §2a TC-CUR-01.
**Expected:** `currency_id` PO TIDAK PERNAH berubah dari mata uang pembelian partner di ketiga cabang (no-partner, currency-sama, currency-beda) — bertentangan dengan docstring method.
**Actual:** `test_ac_02_01/02/03` — **3/3 PASS** (run #7). F-02 dikonfirmasi sebagai bug nyata, bukan dugaan.
**Status:** ☑ Pass (eksekusi nyata, bug dikonfirmasi — keputusan fix ada di FINDINGS.md, bukan di sini)
**Provenance:** `[PERLU-KEPUTUSAN]` (bug dikonfirmasi, keputusan fix di tangan pemilik modul)

### S-03: Konversi harga produk (AC-03-01..03, F-03/F-05)
**Precondition:** Test `test_purchase_order_currency.py` (`TC-CP-01/02`) dieksekusi real.
**Mode eksekusi:** Mode B (docker, real execution).
**Steps:** Lihat `04A_DEV_TESTING.md` §2a TC-CP-01/02.
**Expected:** Short-circuit currency sama → harga apa adanya (AC-03-01); currency beda → konversi via `_convert()` ke currency GLOBAL param, bukan currency PO pemanggil kalau ada race condition (AC-03-02, F-03); AC-03-03 (F-05, direvisi) → TIDAK crash.
**Actual:** `test_ac_03_01` PASS, `test_ac_03_03_convert_price_real_conversion_no_crash` PASS (run #7) — F-05 tertutup sebagai tidak terbukti. F-03 (race condition `ir.config_parameter` global) TIDAK bisa disimulasikan penuh dalam SATU `TransactionCase` (butuh 2 request concurrent sungguhan) — tetap `[PERLU-KEPUTUSAN]` terbuka, dicatat sebagai limitasi tool di `FINDINGS.md`, bukan gagal verifikasi.
**Status:** ☑ Pass (AC-03-01/03) / ⚠️ Tidak bisa diverifikasi penuh (AC-03-02/F-03, limitasi tool)
**Provenance:** `[PERLU-KEPUTUSAN]` (F-03 terbuka)

### S-04: Field `product_add_mode` dead code (AC-04-01/02, F-01)
**Precondition:** Test `test_purchase_order_line_fields.py::TC-F-01` dieksekusi real.
**Mode eksekusi:** Mode B (docker, real execution).
**Steps:** Lihat `04A_DEV_TESTING.md` §2b TC-F-01.
**Expected:** Modul load tanpa `SyntaxError` (AC-04-01); `product_add_mode` TIDAK ada di `_fields` (AC-04-02).
**Actual:** `test_ac_04_01/02` — **2/2 PASS**, DIPERKUAT oleh WARNING log Odoo sendiri saat load modul (`docker-env/logs/odoo.log`: "unknown parameter 'product_add_mode'"). F-01 dikonfirmasi ganda (test + log runtime independen).
**Status:** ☑ Pass — bug dikonfirmasi ganda.
**Provenance:** `[PERLU-KEPUTUSAN]` (bug dikonfirmasi, dampak fungsional saat ini NOL — lihat `FINDINGS.md`)

### S-05: Harga per-vendor supplierinfo (AC-05-01..03)
**Precondition:** Baca `product_configurator_dialog.js` method `get_product_update_price`/`get_optional_product_prices`.
**Mode eksekusi:** Desk-review (AI-interaktif) — QUnit TC JS Unit #03 (`product_configurator_dialog_tests.js`) tertulis (mock `orm.call`) tapi TIDAK tereksekusi (Chrome gap).
**Steps:**
1. Baca cabang supplierinfo match `id_vendor` → pakai harga+currency supplierinfo itu (AC-05-01).
2. Baca cabang tidak ada yang match, list tidak kosong → fallback ke `supplierinfo[0]`, BUKAN `standard_price` (AC-05-02).
3. Baca cabang list `supplierinfo` kosong → fallback ke `standard_price` (AC-05-03).
**Expected:** Ketiga cabang sesuai `01B_ACCEPTANCE_CRITERIA.md` AC-05-01..03.
**Actual:** Dikonfirmasi via pembacaan kode — ketiga cabang cocok dengan `01A_FUNCTIONAL_SPEC.md` BR-05. Tidak ada perubahan kode sejak Step 01.
**Status:** ☐ Pass (desk-review) / **TIDAK Pass via eksekusi nyata**
**Provenance:** `[HASIL-BACA]`

### S-06: Vendor ID dari DOM `id_vendor_0` (AC-06-01/02, F-04)
**Precondition:** Baca `product_configurator_dialog.js` baris 41-43 (`setup()`), `purchase_order_views.xml` baris 27-36 (CSS `visibility: hidden`).
**Mode eksekusi:** Desk-review (AI-interaktif). **PALING BERNILAI untuk `07B_QA_AI_BROWSER.md`** kalau browser tersedia — ini satu-satunya AC yang butuh observasi DOM runtime sungguhan untuk benar-benar dipastikan (bukan cuma dugaan dari baca kode).
**Steps:**
1. Baca asumsi implisit `document.getElementById('id_vendor_0')` — konvensi id Odoo untuk field pertama bernama `id_vendor` (AC-06-01).
2. Baca konsekuensi kalau elemen tidak ditemukan — `.value` pada `null` → `TypeError` runtime (AC-06-02, F-04).
**Expected:** AC-06-01 benar SELAMA konvensi id Odoo tidak berubah + hanya satu form PO aktif; AC-06-02 benar secara teori JS (`null.value` selalu `TypeError`), tapi FREKUENSI kejadian nyata (apakah konteks render ganda pernah benar-benar terjadi di pemakaian modul ini) tidak bisa dipastikan tanpa observasi langsung.
**Actual:** Dikonfirmasi via pembacaan kode (mekanismenya valid secara teknis) — TAPI tidak ada satupun eksekusi nyata (QUnit skip Chrome, Tour skip Chrome) yang benar-benar membuktikan perilaku ini di DOM sungguhan. Ini gap verifikasi TERBESAR yang tersisa dari seluruh 25 AC.
**Status:** ☐ Pass (desk-review, teori) / ❌ **BELUM diverifikasi lewat eksekusi/observasi nyata sama sekali**
**Provenance:** `[PERLU-KEPUTUSAN]`

### S-07: Optional products rekursif (AC-07-01/02)
**Precondition:** Test `test_controllers.py::test_ac_07_01_get_optional_products_route` dieksekusi real (data layer); logic client-side (`_addProduct`/`_removeProduct`/`_getOptionalProducts`) di-desk-review.
**Mode eksekusi:** Mode B (data layer, real execution) + Desk-review (logic client-side JS, QUnit TC JS Unit #02 tertulis tapi tidak tereksekusi).
**Steps:** Lihat `04A_DEV_TESTING.md` §2c TC-01; baca `product_configurator_dialog.js` untuk `_removeProduct`/nested optional products.
**Expected:** Route `get_optional_products` mengembalikan `optional_product_ids` (AC-07-01, data layer); optional product dengan >1 parent TIDAK ikut terhapus selama masih ada parent lain (AC-07-02, client logic).
**Actual:** `test_ac_07_01` — **PASS** (HTTP 200, data layer terverifikasi nyata). Logic client-side `_removeProduct` (AC-07-02) — dikonfirmasi via baca kode saja, TIDAK tereksekusi lewat QUnit.
**Status:** ☑ Pass (AC-07-01, data layer) / ☐ Pass (AC-07-02, desk-review saja)
**Provenance:** `[HASIL-BACA]`

### S-08: Sinkronisasi attribute value saat ganti produk (AC-08-01/02)
**Precondition:** Test `test_purchase_order_line_fields.py::TC-F-02` dieksekusi real.
**Mode eksekusi:** Mode B (docker, real execution).
**Steps:** Lihat `04A_DEV_TESTING.md` §2b TC-F-02.
**Expected:** Value custom/no-variant attribute lama dibersihkan saat `product_id` diganti (AC-08-01/02).
**Actual:** `test_ac_08_01/02` — **2/2 PASS** (run #7).
**Status:** ☑ Pass — eksekusi nyata.
**Provenance:** `[HASIL-BACA]`

### S-09: Pembuatan varian dynamic saat confirm (AC-09-01/02)
**Precondition:** Test `test_controllers.py::test_ac_09_01_create_product_route` (data layer) dieksekusi real; `isPossibleConfiguration()`/`onConfirm()` guard (client-side) di-desk-review.
**Mode eksekusi:** Mode B (route, real execution) + Desk-review (guard client-side, QUnit TC JS Unit #01 tertulis tapi tidak tereksekusi — risiko RENDAH karena pure function).
**Steps:** Lihat `04A_DEV_TESTING.md` §2c TC-02; baca `onConfirm()` untuk early-return guard.
**Expected:** Route `create_product` membuat varian baru dari kombinasi dynamic SEBELUM `props.save()` (AC-09-01); `onConfirm()` early-return kalau ada kombinasi invalid, dialog tetap terbuka (AC-09-02).
**Actual:** `test_ac_09_01` — **PASS** (setelah 2 perbaikan test kombinasi atribut di run #2, lihat `04A_DEV_TESTING.md`). AC-09-02 dikonfirmasi via baca kode (`_isPossibleCombination`/early-return logic jelas dan sederhana), TIDAK tereksekusi lewat QUnit.
**Status:** ☑ Pass (AC-09-01, data layer) / ☐ Pass (AC-09-02, desk-review saja, risiko rendah)
**Provenance:** `[HASIL-BACA]`

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | 9 skenario (S-01..S-09), mencakup 25 AC | ✅ Selesai ditulis | Ya (11 sub-AC via Mode B real; 14 sub-AC via desk-review saja) | Mode B (real, sebagian) + Desk-review (AI-interaktif, sebagian) |
| `07B_QA_AI_BROWSER.md` | Verifikasi browser AI langsung (5 skenario S-10..S-14) | ✅ Selesai dieksekusi | Ya | AI-in-the-loop (Claude in Chrome, Mode B G2) |

**Keterbatasan eksekusi via Mode B (QUnit/Tour, tetap berlaku):** 14 dari 25 AC (AC-01 ×6, AC-05
×3, AC-06 ×2, AC-07-02, AC-09-02) adalah logic JS murni yang **TIDAK PERNAH tereksekusi lewat
QUnit/Tour** — QUnit sudah ditulis (`product_configurator_dialog_tests.js`,
`purchase_product_field_tests.js`) dan terbukti valid sintaksnya (berhasil di-bundle di run
#1/#2), tapi Mode B tidak punya Chrome headless untuk menjalankannya (satu percobaan `apt-get
install chromium` gagal, tidak dikejar lebih lanjut — lihat `FINDINGS.md`/`04A_DEV_TESTING.md`).
**Sebagian besar dari 14 AC ini SUDAH diverifikasi lewat jalur alternatif** — lihat §4b di bawah:
`07B_QA_AI_BROWSER.md` (AI-in-the-loop, Claude in Chrome) berhasil memverifikasi AC-01 (sebagian,
+ menemukan bug baru F-06), AC-05, AC-07-02 secara LIVE. Sisa yang masih murni desk-review:
AC-06-02 (DOM element hilang, kondisi abnormal) dan AC-09-02 (guard kombinasi invalid) — lihat
§Keterbatasan di `07B_QA_AI_BROWSER.md`.

### 4b. Keputusan AI-Browser (`07B_QA_AI_BROWSER.md`)

**Koneksi browser tersedia** (Claude in Chrome terhubung ke browser lokal dev) — dipilih eksekusi
**Full 07B — semua skenario** (keputusan pemilik modul, bukan subset). Mode B diswitch dari G1
(test-run) ke G2 (server hidup, `docker-env/docker-compose.yml`, database
`purchase_product_optional_demo`, `http://localhost:8079`), data test dibuat langsung lewat UI
(attribute dynamic baru + supplierinfo vendor baru pada produk demo "Customizable Desk").

5 skenario (S-10..S-14) dieksekusi LIVE — ringkasan:
- **S-10 (AC-01 dasar):** dialog "Configure your product" terbuka benar DAN menemukan bug baru
  tidak terduga — dialog grid `purchase_product_matrix` ikut terbuka bertumpuk di belakang tanpa
  koordinasi (**F-06, baru**, Tinggi — lihat `FINDINGS.md`). Kalau user cuma mengisi dialog depan,
  baris produk UTAMA hilang total dari PO tanpa error.
- **S-11 (AC-05-01, F-04):** harga per-vendor **CONFIRMED benar** ($700 sesuai supplierinfo, bukan
  $750 list price) — mekanisme DOM `id_vendor_0` (F-04) terbukti bekerja di kondisi normal.
- **S-12/S-13 (AC-07-01/02):** tambah & hapus optional product dari dalam dialog **CONFIRMED
  benar** kedua arah.
- **S-14 (klarifikasi F-06):** kalau user melalui KEDUA dialog (grid + configurator) dengan benar
  DAN save eksplisit, data tersimpan benar setelah full reload — mempersempit F-06 jadi murni soal
  dialog tidak terkoordinasi/mudah diabaikan, bukan korupsi data lebih dalam.

**Tidak sempat direproduksi:** AC-06-02 (DOM element hilang, butuh kondisi multi-form abnormal),
AC-09-02 (guard kombinasi invalid), sub-cabang AC-01 lain (direct-assign, warning/block dialog) —
waktu sesi dialihkan ke investigasi F-06 yang bernilai lebih tinggi dari rencana awal. Detail
lengkap semua skenario + screenshot findings: lihat `07B_QA_AI_BROWSER.md`.

---

## 5. Rekap Findings (per tag, detail lengkap di `doc-dev/backfill/FINDINGS.md`)

| Tag | Jumlah (level AC, dari `01B_ACCEPTANCE_CRITERIA.md`) |
|---|---|
| `[PERLU-KEPUTUSAN]` | 9 (AC-02 ×3, AC-03-01/02 ×2, AC-04-02 ×1, AC-06 ×2, AC-01/F-06 ×1) |
| `[DIKONFIRMASI]` | 3 (AC-05-01, AC-07-01, AC-07-02 — via AI-Browser, Step 07B) |
| `[HASIL-BACA]` (tanpa masalah) | 13 |

| Findings (`FINDINGS.md`) | Status |
|---|---|
| F-01 — `product_add_mode` dead field | ✅ CONFIRMED (Mode B + log runtime) — Rendah, dampak fungsional NOL |
| F-02 — `onchange_partner_id` tidak update currency | ✅ CONFIRMED (Mode B, 3/3 test) — Sedang |
| F-03 — `ir.config_parameter` global race condition | Mekanisme CONFIRMED, frekuensi TIDAK bisa dipastikan (limitasi tool) — Tinggi |
| F-04 — DOM `id_vendor_0` fragile | Mekanisme kondisi-normal **✅ CONFIRMED bekerja benar** (AI-Browser, Step 07B); edge-case (id conflict) tetap tidak diverifikasi — Sedang |
| F-05 — `convert_price` diduga crash | ❌ TIDAK TERBUKTI (3× Mode B, test dikoreksi) — CLOSED |
| **F-06 — dialog configurator vs grid tumpang tindih, baris produk utama bisa hilang** | **✅ CONFIRMED via AI-Browser** (Step 07B, direproduksi live) — **Tinggi, BARU ditemukan sesi ini** |

**Verdict:** Backfill dokumentasi selesai sampai Step 07 (termasuk 07B — full AI-Browser
verification). **Tidak ada sign-off** — bukan release gate. 11/25 AC (44%) dikonfirmasi lewat
eksekusi nyata Mode B; ditambah 3 AC dikonfirmasi live via AI-Browser (07B); sisanya tetap
desk-review karena limitasi lingkungan Chrome untuk QUnit/Tour spesifik. Temuan paling bernilai
dari Step 07B: **F-06** (bug fungsional nyata, bukan cuma risiko teoretis seperti F-03/F-04) —
prioritaskan review F-06 di atas finding lain kalau pemilik modul waktu terbatas. Keputusan atas
F-01..F-04 dan F-06 ada di tangan pemilik modul.

---

## 6. Bug / Perlu Perbaikan (konsolidasi)

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| Step 01 (desk-review) + Step 04 (Mode B) | S-04 | F-01: `product_add_mode` tidak pernah jadi field nyata (kurung `Many2many` tidak ditutup) | ☐ Belum — keputusan pemilik modul |
| Step 01 (desk-review) + Step 04 (Mode B) | S-02 | F-02: currency PO tidak pernah ikut currency partner meski docstring bilang begitu | ☐ Belum — keputusan pemilik modul |
| Step 01 (desk-review) | S-03 | F-03: `currency_id` disimpan ke `ir.config_parameter` GLOBAL, berisiko race condition multi-user | ☐ Belum — keputusan pemilik modul |
| Step 01 (desk-review) | S-06 | F-04: harga vendor bergantung `document.getElementById('id_vendor_0')`, rapuh terhadap perubahan konteks render | ☐ Belum — keputusan pemilik modul; mekanisme kondisi-normal **sudah dikonfirmasi bekerja** via 07B, edge-case tetap terbuka |
| Step 07B (AI-Browser, live) | S-10 (07B) | **F-06 (BARU): dialog "Configure your product" dan "Choose Product Variants" (grid) tumpang tindih tanpa koordinasi — baris produk UTAMA bisa hilang dari PO tanpa error apapun kalau user hanya mengisi dialog depan** | ☐ Belum — keputusan pemilik modul, **prioritas Tinggi** |

---

## 7. Slot Metode Masa Depan

Sama seperti template (`07C_QA_PLAYWRIGHT.md` — belum dibuat, belum dibutuhkan).
