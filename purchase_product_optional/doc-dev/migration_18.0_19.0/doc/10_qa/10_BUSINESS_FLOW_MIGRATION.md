# Business Flow — Migrasi purchase_product_optional

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Catatan Mode Eksekusi (blocker, dicatat transparan)

**AI-interaktif (Claude Browser tool) DICOBA dan GAGAL — insiden IDENTIK dengan migrasi 17→18** (lihat
`doc-dev/migration_17.0_18.0/doc/10_qa/10_BUSINESS_FLOW_MIGRATION.md` modul ini, dan
`doc-dev/backfill/test/07B_QA_AI_BROWSER.md` untuk 17.0 — persis pola yang sama TIGA kali berturut-turut
lintas versi). Detail percobaan 2026-08-26:
- Container live dihidupkan (`docker-env`, port 8199), database fresh-install dalam SATU lifetime
  container (menghindari isu filestore terpisah dari container `--rm` sebelumnya — lesson baru sesi
  ini, lihat catatan di bawah).
- Login form (`/web/login`) render dengan benar (dikonfirmasi `read_page`/`get_page_text` — DOM
  terbaca lengkap, field email/password/tombol submit semua ada).
- **Klik pada tombol "Log in" TIDAK PERNAH menghasilkan POST request ke server** — dikonfirmasi
  langsung dari log server (`docker logs`, hanya GET berulang, tidak ada POST) dan
  `read_network_requests` (tidak ada entry POST `/web/login` sama sekali, walau dicoba 3× dengan
  teknik berbeda: click by ref, form_input+click, click+Enter key).
- `computer{action:"screenshot"}` gagal eksplisit: `"Browser pane is not displayed, so the page is
  not compositing frames"` — mengonfirmasi root cause: pane tidak benar-benar compositing/rendering di
  sesi ini, sehingga koordinat klik tidak match hit-testing sungguhan meski `read_page` (akses DOM
  murni) tetap berfungsi normal.

**Kesimpulan:** ini keterbatasan environment Claude Browser tool pada sesi CLI ini (pane tidak
compositing), BUKAN bug kode migrasi — dikuatkan preseden identik di migrasi 17→18 (modul yang sama)
dan backfill 17.0 (kegagalan yang sama persis, root cause berbeda dugaan tapi gejala identik).

**Lesson baru (2026-08-26, docker-env):** database yang dibuat di container `docker compose run --rm`
kehilangan filestore-nya begitu container dihapus (`--rm`) — attachment DB record tetap ada di volume
Postgres persisten, tapi file asset fisiknya hilang, menyebabkan 500 pada asset bundle CSS/JS saat
dibuka lewat container LAIN. **Fix:** untuk uji coba browser hidup, install modul (`-i`) dan jalankan
server DALAM SATU container/lifetime yang sama (tanpa `--rm` sebelum selesai dipakai) — jangan
reuse database yang filestore-nya sudah hilang.

**Keputusan (mengikuti preseden 17→18 sepenuhnya):** pivot ke bukti **Tour Odoo native** (Step 9,
headless Chrome ASLI di dalam container test runner, bukan lewat proxy browser tool ini) sebagai
evidence utama business flow end-to-end — sudah terbukti valid & reliable di 2 migrasi sebelumnya.

---

## Skenario

### S-01: Alur utama — buat PO, konfigurasi produk, tambah optional, simpan
**Level:** Smoke
**Precondition:** Modul ter-install (Step 6/G1 pass), ada produk dengan optional product terkonfigurasi.
**Mode eksekusi:** Tour Odoo native (`static/tests/tours/purchase_product_optional_tour.js`, dieksekusi Step 9) — headless Chrome ASLI di dalam container, bukan proxy browser tool (blocked, lihat catatan di atas).
**Steps:** Buka app Purchase → buat PO baru → isi vendor → tambah baris → pilih produk utama → dialog konfigurator terbuka otomatis → tambah optional product → Confirm → Simpan.
**Expected:** Dialog terbuka tanpa crash (DIFF-01 valid — format many2one objek benar), kedua baris (utama+optional) tersimpan di PO, PO ter-save (breadcrumb bukan lagi "New").
**Actual:** PERSIS sesuai expected — `tour succeeded`, 15/15 langkah, log lengkap `docker-env/logs/odoo_test3.log` (dijalankan 2026-08-26).
**Status:** [x] Pass

### S-02: Instalasi bersih di database 19.0 baru
**Level:** Smoke
**Precondition:** Database 19.0 kosong.
**Mode eksekusi:** Otomatis (Docker G1, Step 6, Mode C — AI langsung, dikonfirmasi dev).
**Steps:** `-i purchase_product_optional --stop-after-init`.
**Expected:** Install selesai tanpa fatal error, 60 modul ter-load.
**Actual:** Sesuai expected, exit code 0, `Registry loaded in 88.764s` (`docker-env/logs/odoo_qa.log`).
**Status:** [x] Pass

### S-03: Harga per-vendor & konversi currency
**Level:** Main Flow
**Precondition:** Produk punya `product.supplierinfo` untuk vendor tertentu.
**Mode eksekusi:** Otomatis (`TestConvertPrice`, `TestPurchaseProductOptionalController`, Step 9).
**Steps:** Panggil `get_values_purchase` dengan vendor & currency berbeda.
**Expected:** Harga mengikuti supplierinfo vendor, dikonversi currency sesuai BSL-002/BSL-003.
**Actual:** Sesuai expected, test PASS.
**Status:** [x] Pass

### S-04: Bug BSL-005/006 (onchange partner currency) dipertahankan identik
**Level:** Main Flow
**Precondition:** Partner dengan `property_purchase_currency_id` berbeda dari currency PO.
**Mode eksekusi:** Otomatis (`TestOnchangePartnerCurrency`, Step 9).
**Steps:** Trigger `onchange_partner_id` dengan partner & currency berbeda.
**Expected:** `currency_id` PO TIDAK berubah (no-op, bug dipertahankan sesuai keputusan dev); core `purchase.order.onchange_partner_id` masih tertimpa total (DIFF-05, dikonfirmasi masih ada nama sama di 19.0).
**Actual:** Sesuai expected — test PASS.
**Status:** [x] Pass

### S-05: Variant dinamis & Confirm — format many2one objek (DIFF-01)
**Level:** Main Flow
**Precondition:** Produk dengan atribut `create_variant == 'dynamic'`, dan optional product.
**Mode eksekusi:** Tour Odoo native (Step 9) + `TestPurchaseProductOptionalController.test_create_product_creates_dynamic_variant`.
**Steps:** Konfigurasi produk di dialog, klik Confirm — memicu `applyProductPurchase()` yang menulis `product_id`/`custom_product_template_attribute_value_id` format objek `{id, display_name}` (bukan tuple lama).
**Expected:** Baris PO tersimpan benar dengan variant baru, tidak ada silent-wrong-read (lihat CAND-04).
**Actual:** Sesuai expected — Tour step 12-15 sukses, unit test PASS.
**Status:** [x] Pass

### S-06: Fallback grid configurator (DIFF-02, `useMatrixConfigurator` hook) — BELUM tereksekusi runtime
**Level:** Detail
**Precondition:** `get_single_product_variant()` mengembalikan `result.mode` selain `'configurator'`.
**Mode eksekusi:** Verifikasi kode (Step 8) — TIDAK ada test/Tour yang memicu jalur ini.
**Steps:** N/A — tidak ada skenario UI yang diketahui bisa memicu kondisi ini (CAND-07: `purchase`/`purchase_product_matrix` tidak pernah mengisi `mode`/`purchase_warning` untuk konteks Purchase).
**Expected:** `this.matrixConfigurator.open(this.props.record, false)` terpanggil tanpa `TypeError`.
**Actual:** *(belum dieksekusi — kode sudah mirror pola native 19.0 persis, diverifikasi lewat code review Step 8, bukan eksekusi runtime)*
**Status:** [ ] Pass / [ ] Fail — **belum dieksekusi, risiko rendah (jalur kemungkinan besar unreachable di produksi per CAND-07)**

### S-07: Dua dialog terbuka bersamaan dari satu aksi (WAJIB — gotcha desain `purchase_product_matrix`)
**Level:** Negative
**Precondition:** Produk matrix-eligible (butuh grid variant) DAN punya optional products sekaligus.
**Mode eksekusi:** Verifikasi kode + log Tour (Step 8/9).
**Steps:** `_onProductTemplateUpdate` kita panggil `super()` TANPA SYARAT sebelum logic sendiri — base class bisa membuka grid dialog duluan sebelum kita membuka Product Configurator.
**Expected (Negative — HARUS TIDAK terjadi tanpa disadari):** Dalam skenario Tour (produk punya optional products, bukan produk matrix multi-varian), HANYA SATU dialog yang terbuka.
**Actual:** Dikonfirmasi dari log Tour — cuma SATU modal title muncul (`"Configure your product"`), tidak ada indikasi grid dialog `"Choose Product Variants"` ikut terbuka. **Untuk skenario produk matrix DAN optional products SEKALIGUS (kombinasi lebih jarang, tidak ada di data Tour test) — gotcha ini tetap ada, identik 17.0/18.0/19.0 (dikonfirmasi `native-source`/`native-target`, BUKAN regresi migrasi), TIDAK diperbaiki (di luar scope port kode 1:1, dikonfirmasi keputusan dev).**
**Status:** [x] Pass (untuk skenario yang diuji) — kombinasi matrix+optional dicatat sebagai limitasi diketahui, bukan blocker gate ini (identik source, bukan regresi)

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03, S-04, S-05 | 3 |
| Detail | S-06 | 1 (belum dieksekusi runtime) |
| Negative | S-07 | 1 |

## Human QA Checklists

Digenerate di `10_qa/human_qa/` (README + 4 file per Level) — lihat folder tersebut.

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9. S-06 belum dieksekusi tapi bukan Fail
(tidak ada jalur reproduksi yang diketahui, risiko rendah dikonfirmasi analisis CAND-07).

## Verdict

- [x] ✅ **Lulus** — S-01/02/03/04/05/07 Pass (evidence Tour + test otomatis nyata + code review),
  S-06 belum dieksekusi runtime tapi risiko rendah dan dicatat eksplisit sebagai item untuk QA
  manual/monitoring produksi, TIDAK memblokir gate ini. Lanjut ke Step 11 (UAT Sign-off).
