# Test Plan (Migrasi) — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `doc-dev/backfill/test/03B_TEST_PLAN.md`
**Tanggal:** 2026-07-29

> Beda dari test plan BACKFILL (`doc-dev/backfill/test/03B_TEST_PLAN.md`): di sana test DITULIS
> dari nol. Di migrasi ini, **suite test (Python + QUnit + Tour) SUDAH ADA** (warisan BACKFILL,
> 11/11 Python pass di run #7, 2 JS test di-skip karena limitasi Chrome environment). Tugas step 9
> migrasi BUKAN menulis ulang test, tapi **re-run identik di environment 18.0** + update titik yang
> memang wajib berubah mengikuti `03_MIGRATION_SPEC.md` (rename method, dst) — lihat kolom
> "Perubahan wajib di test" di bawah.

---

## Step 9 — Dev Testing

> Eksekusi: otomatis/background — `odoo-bin -i purchase_product_optional --test-enable
> --test-tags /purchase_product_optional --stop-after-init` di environment 18.0 (Mode B, docker
> image berbasis `odoo:18.0` — instantiate ulang `docker-env/` dari
> `templates/docker-compose.yml.template` kalau belum ada di `target-codebase`).

| AC | Deskripsi | Unit | Integration | Tour/QUnit (Owl/JS) | Perubahan wajib di test |
|---|---|---|---|---|---|
| AC-01-01 s/d AC-01-06 | Trigger dialog configurator/grid/warning | | | ✓ `purchase_product_field_tests.js` (QUnit), ✓ `purchase_product_optional_tour.js` (happy path) | Referensi ke `_editProductConfiguration` (kalau ada di test/mock) HARUS ikut di-update ke `onEditConfiguration` (DIFF-04) |
| AC-01-09 | Edit baris tersimpan → dialog terbuka dengan data lama | | | ✓ (bagian dari tour/QUnit di atas, kalau ter-cover eksplisit — **cek ulang saat re-run apakah skenario edit benar-benar dieksekusi test, bukan cuma happy-path create**) | **WAJIB** — ini AC yang paling langsung kena DIFF-04. Kalau QUnit test existing tidak eksplisit test alur edit, tambah 1 test case baru sebelum re-run dianggap cukup |
| AC-02-01 s/d AC-02-03 | Onchange currency (bug warisan) | ✓ `test_purchase_order_currency.py` | | | Tidak ada — port apa adanya |
| AC-03-01 s/d AC-03-03 | `convert_price` (short-circuit + konversi nyata) | ✓ `test_purchase_order_currency.py` (`test_ac_03_03_convert_price_real_conversion_no_crash`) | | | Tidak ada — nama test sudah benar (dikoreksi run #7), tinggal re-run. **Prioritas Tinggi**: ini titik paling rawan false-confidence (F-05 pernah salah diduga di 17.0) |
| AC-04-01 s/d AC-04-02 | `product_add_mode` dead field | ✓ `test_purchase_order_line_fields.py` | | | Tidak ada |
| AC-05-01 s/d AC-05-03 | Harga per-vendor | | | ✓ `product_configurator_dialog_tests.js` (QUnit, `.call()` style) | Tidak ada |
| AC-06-01 | Vendor ID dari DOM (normal) | | | ✓ (bagian tour happy path) | Tidak ada — tapi **flag risiko**: kalau skema DOM id 18.0 berubah, tour ini yang akan menangkap duluan |
| AC-06-02 | `id_vendor_0` hilang dari DOM (anomali) | | | ✓ (QUnit, penanda `TypeError`) | Tidak ada |
| AC-07-01 | Optional product diambil rekursif (data layer) | | ✓ `test_controllers.py` | | Tidak ada |
| AC-07-02 | Optional product dihapus berantai | | | ✓ (QUnit, `.call()` pada `_removeProduct`) | Tidak ada |
| AC-08-01 s/d AC-08-02 | Sinkronisasi custom/no-variant attribute value | ✓ `test_purchase_order_line_fields.py` | | | Tidak ada |
| AC-09-01 | Pembuatan varian dynamic via `create_product` | | ✓ `test_controllers.py` | | **Prioritas Sedang**: method core dipanggil sekarang tinggal di `product` (bukan `sale_product_configurator`) — kalau signature beda, test INI yang akan gagal duluan, jangan diabaikan sebagai "flaky" |
| AC-09-02 | Guard kombinasi tidak valid | | | ✓ (QUnit, `_isPossibleCombination`) | Tidak ada |
| AC-10-01 s/d AC-10-03 | **BARU** — dialog overlap (F-06) | | | ⚠ **Belum ada test otomatis** — di BACKFILL F-06 hanya diverifikasi manual/AI-Browser (Step 07), tidak ada Tour/QUnit yang eksplisit reproduce race dua dialog | Rekomendasi (opsional, bukan blocker step 9): tambah 1 tour test khusus skenario ini kalau waktu memungkinkan — kalau tidak, WAJIB tercakup di step 10 AI-Browser |

**Catatan lingkungan (warisan dari BACKFILL, `USAGE_GUIDE.md` §Mode B):** run #4-7 BACKFILL
menemukan 2 limitasi image Docker: `websocket-client` (untuk Tour) butuh dipasang di layer image
(`Dockerfile`, bukan `pip install` di `entrypoint`), dan **Chrome/Chromium tidak tersedia** di image
`odoo:17.0` dasar (percobaan install gagal, tidak dikejar lebih lanjut — lihat batas workaround
`CLAUDE.md` sumber). **Untuk 18.0, cek ulang dari awal apakah image dasar (`odoo:18.0`) punya
kendala yang sama** — jangan asumsikan otomatis sama seperti 17.0 tanpa dicek, tapi juga jangan
habiskan waktu berlebih di sini kalau ternyata kendala sama persis (F-06/Tour/QUnit sudah punya
jalur verifikasi alternatif di step 10 AI-Browser).

---

## Step 10 — QA Testing

> Prioritas: AC yang overlap dengan risiko migrasi (`DIFF-NNN`, ditandai `⚠` di `05a`) WAJIB masuk
> AI-interaktif/AI-Browser, tidak cukup hanya mengandalkan step 9 otomatis — karena beberapa di
> antaranya (DIFF-03/DIFF-07 unreachability, F-06 reproduction) butuh interpretasi visual/behavioral
> yang tidak selalu bisa dijamin oleh assertion test tertulis.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01 s/d AC-01-02, AC-01-05 | Trigger dialog (jalur normal) | | ✓ | |
| AC-01-03 s/d AC-01-04 | `purchase_warning` block/warning | | ✓ **wajib** — buktikan unreachable atau tidak di 18.0 (DIFF-03) | |
| AC-01-06 | `result.mode` → grid configurator | | ✓ **wajib** — buktikan unreachable atau tidak di 18.0 (DIFF-07) | |
| AC-01-09 | Edit baris tersimpan | | ✓ **wajib** — verifikasi langsung dampak rename DIFF-04 | |
| AC-02-01 s/d AC-02-03 | Onchange currency (cross-check visual) | | ✓ | |
| AC-03-01 s/d AC-03-03 | Konversi harga (cross-check angka tampil) | | ✓ | |
| AC-04-01 s/d AC-04-02 | `product_add_mode` (tidak ada UI terkait) | | ✓ | |
| AC-05-01 s/d AC-05-03 | Harga per-vendor | | ✓ | |
| AC-06-01 s/d AC-06-02 | Vendor ID dari DOM | | ✓ | |
| AC-07-01 s/d AC-07-02 | Optional products rekursif | | ✓ | |
| AC-08-01 s/d AC-08-02 | Sinkronisasi attribute value | | ✓ | |
| AC-09-01 s/d AC-09-02 | Pembuatan varian dynamic + guard | | ✓ **AC-09-01 prioritas** — method controller pindah modul | |
| AC-10-01 s/d AC-10-03 | **F-06 dialog overlap** | | ✓ **WAJIB, prioritas Tinggi** — direproduksi ulang persis skenario BACKFILL (`doc-dev/backfill/test/07B_QA_AI_BROWSER.md`), bandingkan behavior identik/berubah karena `purchase_product_matrix` restrukturisasi (DIFF-04) | |

**Tidak ada AI+tool eksternal** — semua skenario observable lewat AI-interaktif/Claude in Chrome
biasa di dalam Odoo, tidak butuh E2E lintas sistem/browser matrix.

---

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Product Configurator — trigger & edit | AC-01 (semua), AC-10 | Manual (business user, dengan awareness khusus F-06 — beri tahu user ini bug WARISAN yang sengaja tidak diperbaiki) |
| Currency & harga vendor | AC-02, AC-03, AC-05 | Manual |
| `product_add_mode` dead field | AC-04 | Manual (verifikasi negatif — tidak ada UI yang bergantung ke field ini) |
| Vendor ID dari DOM | AC-06 | Manual |
| Optional products rekursif | AC-07 | Manual |
| Sinkronisasi attribute value | AC-08 | Manual |
| Pembuatan varian dynamic | AC-09 | Manual |

---

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit (5 AC: AC-02, AC-03, AC-04, AC-08), Integration (2 AC: AC-07-01, AC-09-01), Tour/QUnit (13 AC: AC-01, AC-05, AC-06, AC-07-02, AC-09-02) | Otomatis/background, re-run suite existing di 18.0 (Mode B) — **AC-10 (3) belum punya test otomatis, rekomendasi opsional** | 20 dari 23 (AC-10 belum tercakup otomatis) |
| 10 | QA | AI-interaktif (semua 23 AC) | Live, prioritas Tinggi untuk AC ber-tanda `⚠` (DIFF-03/04/05/07) + AC-10 (F-06) | 23 (semua) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 7 kelompok fitur |

**Total AC:** 23 (AC-01 melalui AC-10, termasuk AC-01-09 dan 3 sub-AC AC-10 baru). Ini naik dari 24
AC BACKFILL (AC-01..AC-09) karena beberapa AC granular BACKFILL (mis. AC-01-01..06 dihitung sebagai
1 kelompok representatif untuk migrasi, ditambah AC-10 baru) — bukan pengurangan cakupan, murni
pengelompokan ulang di level dokumen ini.
