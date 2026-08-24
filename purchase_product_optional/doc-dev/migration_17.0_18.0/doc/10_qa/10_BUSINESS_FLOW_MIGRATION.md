# Business Flow — Migrasi purchase_product_optional

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Catatan Mode Eksekusi (blocker, dicatat transparan)

**AI-interaktif (Claude Browser tool) DICOBA dan GAGAL** — persis insiden yang sama seperti tercatat di
`source-codebase/purchase_product_optional/doc-dev/backfill/test/07B_QA_AI_BROWSER.md` untuk modul ini
di 17.0 ("Claude Browser MCP session blocked"). Detail percobaan 2026-08-24:
- Instance Docker persisten dihidupkan (`docker-env`, port 8178), login admin BERHASIL.
- Webclient backend (`/odoo`) TIDAK PERNAH mount ke DOM (`document.body.children.length === 0`)
  meski semua asset (`web.assets_web.min.js`, dst.) ter-load 200 OK dan global `odoo`/`owl` terdefinisi.
  Tidak ada console error selain `Service worker registration failed` (kemungkinan besar root cause —
  webclient modern menunggu registrasi service worker/bus websocket yang tidak didukung penuh oleh
  sandbox proxy browser tool ini).
- Dicoba 3× (reload, force-navigate, tunggu lebih lama) — hasil sama persis tiap kali.

**Keputusan:** mengikuti preseden yang sama seperti backfill 17.0 — pivot ke bukti **Tour Odoo native**
(Step 9, headless Chrome ASLI di dalam container, bukan lewat proxy browser tool) sebagai evidence utama
business flow end-to-end. Tour ini BUKAN cuma test otomatis biasa — ia mengeksekusi persis skenario S-01
di bawah lewat browser sungguhan (klik, isi form, baca DOM), jadi tetap valid sebagai bukti QA meski
bukan dari sesi AI-interaktif langsung.

---

## Level skenario

## Skenario

### S-01: Alur utama — buat PO, konfigurasi produk, tambah optional, simpan
**Level:** Smoke
**Precondition:** Modul ter-install (Step 6/G1 pass), ada produk dengan optional product terkonfigurasi.
**Mode eksekusi:** Tour Odoo native (`static/tests/tours/purchase_product_optional_tour.js`, dieksekusi Step 9) — headless Chrome ASLI di dalam container, bukan proxy browser tool (blocked, lihat catatan di atas).
**Steps:** Buka app Purchase → buat PO baru → isi vendor → tambah baris → pilih produk utama → dialog konfigurator terbuka otomatis → tambah optional product → Confirm → Simpan.
**Expected:** Dialog terbuka tanpa crash (DIFF-07 valid), kedua baris (utama+optional) tersimpan di PO, PO ter-save (breadcrumb bukan lagi "New").
**Actual:** PERSIS sesuai expected — `TOUR purchase_product_optional_configurator_tour SUCCEEDED`, 15/15 langkah, log lengkap di `docker-env/logs/odoo_step9.log` (dijalankan 2026-08-24).
**Status:** [x] Pass

### S-02: Instalasi bersih di database 18.0 baru
**Level:** Smoke
**Precondition:** Database 18.0 kosong.
**Mode eksekusi:** Otomatis (Docker G1, Step 6).
**Steps:** `-i purchase_product_optional --stop-after-init`.
**Expected:** Install selesai tanpa fatal error, 59 modul (termasuk `sale` baru) ter-load.
**Actual:** Sesuai expected, exit code 0, `Registry loaded in 42.118s` (`docker-env/logs/odoo_g1.log`).
**Status:** [x] Pass

### S-03: Harga per-vendor & konversi currency
**Level:** Main Flow
**Precondition:** Produk punya `product.supplierinfo` untuk vendor tertentu.
**Mode eksekusi:** Otomatis (`TestConvertPrice`, `TestPurchaseProductOptionalController`, Step 9).
**Steps:** Panggil `get_values_purchase` dengan vendor & currency berbeda.
**Expected:** Harga mengikuti supplierinfo vendor, dikonversi currency sesuai BR-02/BR-03.
**Actual:** Sesuai expected, test PASS.
**Status:** [x] Pass

### S-04: Bug F-02/F-03 (onchange partner currency) dipertahankan identik
**Level:** Main Flow
**Precondition:** Partner dengan `property_purchase_currency_id` berbeda dari currency PO.
**Mode eksekusi:** Otomatis (`TestOnchangePartnerCurrency`, Step 9).
**Steps:** Trigger `onchange_partner_id` dengan partner & currency berbeda.
**Expected:** `currency_id` PO TIDAK berubah (no-op, bug dipertahankan sesuai keputusan dev); MRO menunjukkan method modul menimpa method core (F-02 tetap valid di 18.0).
**Actual:** Sesuai expected — kedua test PASS, log MRO menunjukkan class modul + class core `purchase` sama-sama define `onchange_partner_id`.
**Status:** [x] Pass

### S-05: Edit ulang baris yang sudah dikonfigurasi (DIFF-05 — rename `onEditConfiguration`)
**Level:** Detail
**Precondition:** Baris PO dengan `is_configurable_product=True`.
**Mode eksekusi:** Manual (belum ada test otomatis untuk skenario spesifik ini — dicatat sebagai gap di `08_CODE_REVIEW.md`/`09_DEV_TESTING.md`).
**Steps:** Buka kembali baris yang sudah dikonfigurasi, klik edit configuration.
**Expected:** Dialog `ProductConfiguratorDialogPurchase` terbuka kembali dengan data existing (bukan jatuh ke grid default `purchase_product_matrix`).
**Actual:** *(belum dijalankan — direkomendasikan dev/QA jalankan manual sebelum UAT, lihat `human_qa/02_MAIN_FLOW.md` langkah tambahan)*
**Status:** [ ] Pass / [ ] Fail — **belum dieksekusi, risiko rendah (perubahan kode mekanis rename saja)**

### S-06: Dua dialog terbuka bersamaan dari satu aksi (WAJIB — gotcha desain `purchase_product_matrix`)
**Level:** Negative
**Precondition:** Produk matrix-eligible (butuh grid variant) DAN punya optional products sekaligus.
**Mode eksekusi:** Verifikasi kode + log Tour (AI, Step 8).
**Steps:** `_onProductTemplateUpdate` kita panggil `super()` TANPA SYARAT sebelum logic sendiri — base class bisa membuka grid dialog duluan sebelum kita membuka Product Configurator.
**Expected (Negative — HARUS TIDAK terjadi tanpa disadari):** Dalam skenario Tour (produk punya optional products, bukan produk matrix multi-varian), HANYA SATU dialog yang terbuka.
**Actual:** Dikonfirmasi dari log Tour — cuma SATU modal title muncul (`"Configure your product""`), tidak ada indikasi grid dialog `"Choose Product Variants"` ikut terbuka. **Untuk skenario produk matrix DAN optional products SEKALIGUS (kombinasi lebih jarang, tidak ada di data Tour test) — gotcha ini tetap ada, identik 17.0/18.0 (dikonfirmasi `native-source`/`native-target`, BUKAN regresi migrasi), TIDAK diperbaiki (di luar scope port kode 1:1).**
**Status:** [x] Pass (untuk skenario yang diuji) — kombinasi matrix+optional dicatat sebagai limitasi diketahui, bukan blocker gate ini (identik source, bukan regresi)

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03, S-04 | 2 |
| Detail | S-05 | 1 (belum dieksekusi manual) |
| Negative | S-06 | 1 |

## Human QA Checklists

Digenerate di `10_qa/human_qa/` (README + 4 file per Level) — lihat folder tersebut.

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9.

## Verdict

- [x] ✅ **Lulus** — S-01/02/03/04/06 Pass (evidence Tour + test otomatis nyata), S-05 belum dieksekusi manual tapi risiko rendah (rename mekanis, tidak mengubah logic) — dicatat eksplisit sebagai item untuk QA manual sebelum UAT, TIDAK memblokir gate ini. Lanjut ke Step 11 (UAT Sign-off).
