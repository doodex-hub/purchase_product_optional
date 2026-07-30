# Dev Testing — purchase_product_optional

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-07-29

---

> **Eksekusi:** Mode B (docker, dev menjalankan). Command final:
> ```
> odoo -d purchase_product_optional_18_test -i purchase_product_optional
>   --test-enable --test-tags /purchase_product_optional --stop-after-init
> ```
> `docker-env/docker-compose.yml` (target-codebase) sudah di-set ke command ini — database FRESH
> `_test` (bukan reuse `_demo` dari G2), supaya `-i` menginstall dari nol termasuk dependency baru
> `sale` (MF-14) tanpa perlu `-u`.

## 9a. Audit Kesiapan Test

Suite ini BUKAN baru ditulis untuk migrasi — diwarisi utuh dari `doc-dev-backfill` (2026-07-28,
project BACKFILL 17.0), yang sudah melalui audit stub-vs-lengkap dan koreksi isi (lihat riwayat run
#1-#7 di `doc-dev/backfill/test/04A_DEV_TESTING.md`). Tidak ada assert kosong/stub — dikonfirmasi
lewat 3 iterasi run nyata di 17.0 yang masing-masing mengoreksi test yang salah (F-05 sempat salah
diduga crash, AC-09-01 sempat salah setup data). Audit ulang penuh TIDAK diulang di sini (sudah
dilakukan tuntas di BACKFILL) — cukup port + re-run sebagai regresi.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-02-01/02/03 | Currency onchange (bug warisan) | `test_purchase_order_currency.py` | ✅ Lengkap | Assert nyata, dikonfirmasi baseline run #7 BACKFILL |
| AC-03-01/03 | `convert_price` (DIFF-01) | `test_purchase_order_currency.py` | ✅ Lengkap | AC-03-03 pernah dikoreksi (F-05 salah diduga crash) — versi final sudah benar |
| AC-04-01/02 | `product_add_mode` dead code | `test_purchase_order_line_fields.py` | ✅ Lengkap | |
| AC-08-01/02 | Sync custom/no-variant attribute value | `test_purchase_order_line_fields.py` | ✅ Lengkap | |
| AC-07-01 | `get_optional_products` route | `test_controllers.py` | ✅ Lengkap | |
| AC-09-01 | `create_product` route (dynamic variant) | `test_controllers.py` | ✅ Lengkap | Sempat dikoreksi (setup kombinasi ptav salah), versi final benar |
| AC-01-xx, AC-05, AC-06, AC-09-02, AC-10 | Alur JS/Owl (dialog, harga vendor, DOM, dialog overlap) | `static/tests/*.js` (QUnit) + `static/tests/tours/*.js` (Tour) | ⚠️ **Tidak tereksekusi otomatis** | Chrome/Chromium tidak tersedia di image `odoo:18.0` (sama seperti `odoo:17.0` di BACKFILL) — SKIP, bukan fail. Lihat §Verifikasi Tambahan di bawah untuk jalur manual. |

**Verdict audit:** Cakupan Unit/Integration (Python) lengkap dan sudah teruji tanpa stub. Cakupan
Owl/JS otomatis (QUnit/Tour) TIDAK bisa dieksekusi di lingkungan ini (limitasi Chrome, bukan gap
tulisan test) — dikompensasi sebagian lewat verifikasi manual interaktif (browser, lihat di bawah),
sisanya dilimpahkan ke Step 10 (QA Testing, format AI-Browser penuh seperti BACKFILL Step 07).

## Baseline

- **Characterization test asli (17.0, BACKFILL run #7, 2026-07-28):** 11/11 Unit+Integration PASS,
  2 (Tour+QUnit) SKIP karena Chrome tidak tersedia di image — baseline resmi untuk perbandingan.
- **Applicability Check Fase E (Owl/JS) dari step 6:** **Ya, applicable** — modul ini punya komponen
  Owl sungguhan (`ProductConfiguratorDialogPurchase` + 4 komponen lain), dikonfirmasi Test 2b.

## Hasil Unit, Integration & Tour Test (target-codebase, 18.0)

**Run dieksekusi 2026-07-29** (Mode B, `purchase_product_optional_18_test`, fresh db). Instalasi
bersih: 59 modul (termasuk `sale` dari nol, MF-14), 2 WARNING expected (MF-01, identik run G1
sebelumnya), tanpa CRITICAL/ERROR saat load. Hasil akhir log:

```
0 failed, 0 error(s) of 13 tests when loading database 'purchase_product_optional_18_test'
```

**IDENTIK dengan baseline 17.0 run #7** — tidak ada regresi.

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-02-01/02/03 | ✅ Pass | — | — | ✅ | Bug warisan (currency onchange) tetap identik |
| AC-03-01 | ✅ Pass | — | — | ✅ | |
| AC-03-03 (⚠ DIFF-01) | ✅ Pass | — | — | ✅ | `_convert()` tetap tidak crash — signature 18.0 kompatibel, dikonfirmasi eksekusi nyata (bukan cuma baca kode) |
| AC-04-01/02 | ✅ Pass | — | — | ✅ | `product_add_mode` tetap dead code, identik |
| AC-08-01/02 | ✅ Pass | — | — | ✅ | |
| AC-07-01 | — | ✅ Pass | — | ✅ | Route `get_optional_products` — method yang pindah dari `sale_product_configurator`→`product` terbukti kompatibel |
| AC-09-01 (⚠ Controller) | — | ✅ Pass | — | ✅ | Route `create_product`/`_create_product_variant` terbukti kompatibel eksekusi nyata |
| QUnit suite | — | — | ⚠️ SKIP | N/A | "Chrome executable not found" — limitasi lingkungan, identik BACKFILL 17.0, BUKAN regresi/bug |
| Tour `happy_path` | — | — | ⚠️ SKIP | N/A | Sama seperti di atas |

## Verifikasi Tambahan (manual, melengkapi Tour/QUnit yang skip)

Karena Tour/QUnit otomatis tidak bisa jalan (Chrome), beberapa AC berisiko tinggi diverifikasi
manual langsung via browser (Claude in Chrome) selama sesi Step 6 G2 dan awal Step 9 ini —
BUKAN pengganti penuh Step 10 (QA Testing formal), tapi mengurangi risiko sebelum lanjut ke sana:

| AC | Hasil | Catatan |
|---|---|---|
| **AC-01-09** (⚠ DIFF-04, prioritas Tinggi dari Code Review §C) | ✅ **PASS** | Baris PO yang sudah dikonfigurasi (Legs=Steel, Color=White) di-klik edit → dialog "Configure your product" terbuka kembali dengan Legs=Steel, Color=White ter-pilih (bukan kosong). **Fix rename `onEditConfiguration` (DIFF-04) terbukti bekerja end-to-end.** |
| AC-07-01/02 (optional products) | ✅ PASS (live) | "+Add" Conference Chair berhasil ditambahkan ke line optional products, tanpa error |
| AC-10-01/02 (F-06 dialog overlap) | ✅ Direproduksi identik | Dialog grid + configurator terbuka bersamaan; jika hanya dialog depan diselesaikan, baris utama hilang — identik 17.0 (bug warisan, TIDAK diperbaiki sesuai Source of Truth) |
| AC-10-03 (grid dulu baru configurator) | 🔶 Sebagian | Kedua dialog diselesaikan berurutan (grid dulu) — baris utama TERSIMPAN (tidak hilang, beda dari AC-10-02), TAPI data varian yang tampil (kode produk vs harga) menunjukkan sedikit inkonsistensi yang belum coba diverifikasi ulang secara sistematis. Dilimpahkan ke Step 10 untuk verifikasi lebih teliti dengan skenario terkontrol. |
| AC-01-01..06, AC-05, AC-06 | ⬜ Belum diverifikasi | Perlu skenario eksplisit (produk dengan `purchase_line_warn`, `supplierinfo` custom, dst) — Step 10 |

## Kontribusi ke Knowledge Base

- [x] **Ada** — sudah tercatat sebelumnya di `06c_IMPLEMENTATION_LOG.md` §Kontribusi ke Knowledge
  Base (kandidat MF-13/MF-14, belum dipromosikan). Tidak ada temuan BARU khusus dari eksekusi step 9
  ini — hasil run mengonfirmasi (bukan menambah) apa yang sudah diketahui dari step 6/8.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass — lanjut ke step 10.** 11/11 Python TC pass,
  identik baseline 17.0 run #7. AC-01-09 (prioritas Tinggi dari Code Review) sudah diverifikasi live
  dan PASS. Tour/QUnit skip karena limitasi lingkungan (Chrome), bukan kegagalan — konsisten dengan
  BACKFILL, tidak perlu dikejar ulang (sudah 1× gagal coba fix di BACKFILL run #6, sesuai batas
  workaround `CLAUDE.md`).

**Dibawa ke Step 10 (QA Testing, format AI-Browser penuh seperti BACKFILL Step 07):**
1. AC-01-01..06 (trigger dialog, `purchase_warning`/`mode` unreachability — DIFF-03/DIFF-07)
2. AC-05 (harga per-vendor) — perlu setup `supplierinfo` custom dulu (harga tampil `$0.00` di sesi
   G2 karena db demo/test tidak punya data ini)
3. AC-06 (DOM `id_vendor_0`)
4. AC-10-03 — verifikasi lebih teliti (data varian yang tampil setelah grid+configurator diselesaikan
   berurutan)
5. Reproduksi F-06/MF-06 penuh dengan skenario terkontrol (seperti BACKFILL Step 07)
