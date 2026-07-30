# Code Review — purchase_product_optional

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 17.0 → 18.0
**Files reviewed:** `__manifest__.py`, `views/purchase_order_views.xml`, `static/src/js/purchase_product_field.js`, `static/src/js/product_configurator_dialog/product_configurator_dialog.js` (+ 4 komponen Owl lain, dibaca ulang Fase E/F), `controllers/main.py`, `models/purchase_order.py`, `models/purchase_order_line.py`, `models/product_template.py`
**Tanggal:** 2026-07-29

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| I-01 | 🟡 Warning | Dokumentasi | `03_spec/03_MIGRATION_SPEC.md` | — | Spec ditulis SEBELUM Checkpoint G2 — belum menyebut MF-13 (`useService("rpc")` dihapus) atau MF-14 (`sale` dependency hilang), padahal keduanya ternyata jadi fix wajib. Traceability tetap utuh lewat `FINDINGS.md`/`06c_IMPLEMENTATION_LOG.md`, tapi spec teknis jadi tidak lengkap sebagai single-source. | Tambahkan baris singkat di `03_MIGRATION_SPEC.md` §2 yang mereferensikan MF-13/MF-14 (retroactive), supaya pembaca spec tanpa baca `FINDINGS.md` tidak salah kira scope A1 cuma soal `sale_product_configurator`. |
| I-02 | 🔵 Info | Code Quality (warisan) | `product_configurator_dialog.js` | 42-44 | `document.getElementById('id_vendor_0').value` tanpa null-check — ini MF-04 (warisan 17.0), BUKAN diperkenalkan migrasi. | TIDAK diperbaiki (prinsip Source of Truth) — tetap prioritas verifikasi Step 9/10 sesuai catatan MF-04 yang sudah ada. |
| I-03 | 🔵 Info | Code Quality (warisan) | `purchase_product_field.js` | 137, 147 | `console.log('Main Product Quantity:', ...)`/`console.log('tes')` — debug leftover warisan (BSL-028). | TIDAK dihapus — port 1:1 sesuai Source of Truth. |
| I-04 | 🔵 Info | Code Quality (warisan) | `product_configurator_dialog.js` | 97-162 | `get_supplierinfo_id`/`get_optional_product_prices`/`get_product_update_price` — duplikasi logic signifikan (pola lookup `supplierinfo`→`price`/`currency_id` ditulis ulang 2×), plus N+1 `orm.call` di dalam loop `for (const product of optionalProducts)`. Pola ini SUDAH ada di 17.0, tidak diperkenalkan migrasi. | Di luar scope port kode (refactor performa/readability dilarang `CLAUDE.md` kecuali wajib kompatibilitas). Catat sebagai kandidat tech-debt terpisah, bukan blocker migrasi. |
| I-05 | 🔵 Info | Business Logic (warisan) | `product_configurator_dialog.js` | 104-106, 118, 158-160 | 3 `try/catch` menelan error jadi `console.error` saja (tidak surface ke user) — ini kenapa "Component is destroyed" (temuan G2) tampil di console tapi tidak pernah muncul sebagai notifikasi. Pola warisan 17.0, bukan perubahan migrasi. | TIDAK diperbaiki — port 1:1. Dicatat murni sebagai konteks kenapa error G2 tidak terlihat user. |
| I-06 | 🔵 Info | Observasi baru (G2) | — (perilaku `purchase_product_matrix` 18.0) | — | AC-10-01 mendeskripsikan "grid di belakang, configurator di depan" — observasi live G2 (2026-07-29) menunjukkan urutan SEBALIKNYA (grid tampil di depan/atas). Root cause tetap sama (unconditional `super()` call, BSL-020, tidak disentuh modul ini). | Bukan bug kode modul ini (z-index ditentukan komponen native `Dialog`/urutan `dialog.add()`, di luar file yang di-migrasi). Catat sebagai koreksi deskripsi AC-10-01 untuk Step 9/10 — bukan regresi. |

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

**Ringkasan:** 0 🔴, 1 🟡 (dokumentasi, bukan kode), 5 🔵 (semua warisan/observasi, bukan regresi migrasi). Tidak ditemukan issue baru yang diperkenalkan oleh perubahan migrasi (DIFF-04, DIFF-05, MF-13, MF-14) — keempatnya mekanis, sempit, dan sudah diverifikasi eksekusi nyata (lihat §D).

---

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (`convert_price`, `product_template.py`) | Tidak ada perubahan | ✅ Selesai | Dikonfirmasi signature `_convert()` 18.0 kompatibel (step 2), port 1:1 tanpa insiden |
| DIFF-02 (manifest `depends`, hapus `sale_product_configurator`) | `depends` = `['purchase', 'purchase_product_matrix']` (A1), **direvisi lagi jadi `+ 'sale'`** setelah MF-14 | ✅ Selesai (dengan revisi) | Revisi tidak diantisipasi spec asli — lihat I-01 |
| DIFF-06 (`<tree>`→`<list>`, 4 titik) | Semua 4 titik diganti, dikonfirmasi `Grep` nihil `tree` tersisa | ✅ Selesai | Diverifikasi G1 (install bersih) |
| DIFF-04 (rename `_editProductConfiguration`→`onEditConfiguration`) | Rename dieksekusi persis, `super.onEditConfiguration(...arguments)` dipanggil | ✅ Selesai (kode) | **Belum diverifikasi lewat skenario AC-01-09 (edit baris tersimpan) secara eksplisit** — G2 baru menguji alur produk BARU, bukan re-edit baris existing. Lihat gap C. |
| DIFF-05 (`_openGridConfigurator(false)`) | Argumen eksplisit `false` ditambahkan | ✅ Selesai | Port aman, falsy-equivalent dengan versi lama |
| DIFF-03 (`purchase_warning` kemungkinan unreachable) | Kode dipertahankan apa adanya (baca `result.purchase_warning`) | ✅ Port selesai, verifikasi tertunda | Belum ada skenario eksplisit produk dengan `purchase_line_warn` diisi — dilimpahkan ke Step 9/10 sesuai rencana awal |
| DIFF-07 (`result.mode`/`product_add_mode` kemungkinan unreachable) | Kode dipertahankan apa adanya | ✅ Port selesai, verifikasi tertunda | Sama seperti DIFF-03 — dilimpahkan ke Step 9/10 |
| Controller & Route (method pindah ke `product`) | 4 route `controllers/main.py` port 1:1 | ✅ Selesai & terverifikasi | Dikonfirmasi eksekusi nyata G2 — `_get_first_possible_combination`, `_create_product_variant` (implisit via alur Confirm), `_get_variant_for_combination`, `_get_attribute_exclusions` semua jalan tanpa error |
| MF-13 (`useService("rpc")` dihapus, TIDAK ada di spec asli) | `import { rpc } from "@web/core/network/rpc"` + 4 call site diganti | ✅ Selesai & terverifikasi | Ditemukan & diperbaiki di G2 (setelah spec ditulis) — lihat I-01 |
| MF-14 (`sale` dependency hilang, TIDAK ada di spec asli) | `depends` + `'sale'` | ✅ Selesai & terverifikasi | Eskalasi user, resolved — lihat I-01 |
| 5 komponen Owl sekunder + 5 template XML | Tidak ada perubahan | ✅ Selesai | Dikonfirmasi Owl 2/QWeb modern dari awal (Fase E/F) |

**Kesimpulan B:** Tidak ada gap implementasi vs spec yang belum dieksekusi — hanya 1 gap dokumentasi (spec belum retroactive-update untuk MF-13/MF-14, I-01) dan 1 area verifikasi tertunda by design (DIFF-03/DIFF-07, sesuai rencana asli dilimpahkan ke step 9/10).

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01/02/05 | Trigger dialog / auto-select varian tunggal | 🔶 Sebagian — AC-01-01 implisit terkonfirmasi (dialog terbuka untuk produk dengan optional products, G2), AC-01-02/05 belum ditest eksplisit | Verifikasi penuh → Step 9/10 |
| AC-01-03/04 (⚠ DIFF-03) | `purchase_warning` block/warning | ⬜ Belum diverifikasi | Sesuai rencana, prioritas Step 9/10 |
| AC-01-06 (⚠ DIFF-05/07) | `result.mode` → grid | ⬜ Belum diverifikasi | Sesuai rencana, prioritas Step 9/10 |
| **AC-01-09 (⚠ DIFF-04, prioritas Tinggi)** | Edit baris tersimpan → dialog reopen dengan data | ⬜ **Belum diverifikasi** | **Gap paling penting di code review ini** — AC ini yang paling langsung terdampak fix DIFF-04 (rename method), TAPI G2 hanya menguji pembuatan baris BARU, tidak pernah klik-edit baris yang sudah tersimpan. Rekomendasi: jadikan skenario PERTAMA yang dites di Step 9 (dev testing interaktif) sebelum lanjut ke AC lain. |
| AC-02-01..03 | Currency onchange (bug warisan) | ⬜ Belum diverifikasi eksekusi 18.0 | Perlu re-run suite Python (`tests/*.py`) — Step 9 |
| AC-03-01..03 (⚠ DIFF-01) | `convert_price` | ⬜ Belum diverifikasi eksekusi 18.0 | Idem — Step 9 |
| AC-04-01/02 | `product_add_mode` dead code | ✅ Terverifikasi tidak langsung | G1 log menunjukkan WARNING field ini persis seperti diprediksi (MF-01/MF-12 log) — konsisten AC-04-01. AC-04-02 (akses langsung field) belum ditest eksplisit tapi risiko sangat rendah |
| AC-05-01..03 | Harga per-vendor (supplierinfo) | ⬜ Belum diverifikasi valid — G2 menunjukkan harga `$0.00` (kemungkinan db demo tidak ada `supplierinfo` custom, BUKAN regresi kode, lihat `FINDINGS.md`) | Perlu setup data test sepadan BACKFILL — Step 10 |
| AC-06-01/02 (⚠ MF-04) | Baca `id_vendor_0` dari DOM | 🔶 Sebagian — `id_vendor` terbaca (dipakai di harga, meski hasil `$0.00`), AC-06-02 (elemen tidak ada) belum ditest | Step 9/10 |
| AC-07-01/02 | Optional products rekursif | ✅ **Terverifikasi live G2** | "+Add" Conference Chair berhasil, tidak ada error — konsisten dengan BACKFILL 17.0 |
| AC-08-01/02 | Sync custom/no-variant attribute value | ⬜ Belum diverifikasi eksekusi 18.0 | Step 9 (test Python) |
| AC-09-01 (⚠ Controller) | Dynamic variant creation via `create_product` | ⬜ Belum diverifikasi — skenario G2 kemarin tidak memakai atribut `create_variant="dynamic"` | Step 9/10, tapi risiko rendah (endpoint sudah terbukti reachable tanpa error untuk kombinasi lain) |
| AC-09-02 | Kombinasi invalid → Confirm no-op | ⬜ Belum diverifikasi | Step 9/10 |
| **AC-10-01/02/03 (F-06/MF-06)** | Dialog overlap | ✅ **Terverifikasi live G2** — AC-10-02 direproduksi PERSIS (baris utama hilang, silent). AC-10-01 z-order sedikit beda dari deskripsi (lihat I-06), AC-10-03 (grid dulu baru configurator) belum ditest | Bug warisan dikonfirmasi identik — TIDAK diperbaiki, sesuai rencana |

**Kesimpulan C:** Mayoritas AC memang BELUM diverifikasi eksekusi penuh di 18.0 — ini SESUAI rencana workflow (Step 8/Code Review ≠ Step 9/Dev Testing ≠ Step 10/QA Testing, lihat `ai-doc/OVERVIEW.md` §6). Yang sudah terverifikasi live lewat G2 (AC-07-01/02, AC-10-01/02) memberi confidence tambahan lebih awal dari jadwal. **Satu gap ditandai prioritas Tinggi untuk Step 9: AC-01-09**, karena AC ini adalah bukti fungsional langsung dari fix DIFF-04 (risiko Tinggi di spec) dan belum pernah dieksekusi sama sekali.

## D. Cek Khusus Migrasi — P1 Fidelity

> Beda dari review kode "baru" biasa: yang dicari di sini BUKAN "apakah kodenya bagus secara umum", tapi **apakah kode migrasi diam-diam mengubah behavior** (memperbaiki bug lama, menambah/menghapus fitur, refactor gaya) padahal seharusnya port 1:1 kecuali yang eksplisit disetujui di `03_MIGRATION_SPEC.md` §4.

- [x] **Tidak ada perubahan behavior yang tidak disengaja** — semua deviasi dari source (`source-codebase`) sudah eksplisit tercatat & disetujui:
  - DIFF-04 (rename method) — mekanis, disetujui spec §4, diverifikasi tidak mengubah isi/logic method.
  - DIFF-05 (`_openGridConfigurator(false)`) — mekanis, falsy-equivalent dengan versi lama, disetujui spec §4.
  - MF-13 (`rpc` import) — mekanis murni (API compatibility), tidak mengubah parameter/payload RPC.
  - MF-14 (`+ 'sale'` di `depends`) — **disetujui eksplisit via eskalasi user** (bukan keputusan sepihak AI), net footprint sama seperti 17.0 (implisit tertarik sebelumnya).
  - F-01..F-06/MF-01..MF-06 (bug warisan) — SEMUA dipertahankan identik, tidak ada satupun yang "sekalian diperbaiki". Dikonfirmasi ulang lewat G2: MF-01 (log warning identik), MF-06 (direproduksi identik + detail baru "Component is destroyed" yang TIDAK dianggap sebagai perbaikan/perubahan, cuma manifestasi Owl 2).
  - `console.log` debug (BSL-028), pola DOM-read (MF-04), duplikasi kode (I-04) — semua TIDAK "dibersihkan" meski tergoda, sesuai larangan refactor gaya di `CLAUDE.md`.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [ ] Tidak ada perubahan yang tidak tertelusuri ke spec
- [x] **Ada, tapi TERTELUSUR lewat dokumen lain** — MF-13 dan MF-14 tidak ada di draft awal
  `03_MIGRATION_SPEC.md` (ditulis sebelum G2), tapi keduanya tertelusur penuh lewat: (1) `FINDINGS.md`
  MF-13/MF-14 (deskripsi, root cause, opsi, keputusan), (2) `06c_IMPLEMENTATION_LOG.md` §[Fase G2] +
  revisi retroaktif §[Fase A1], (3) `CLAUDE.md` status log. Rekomendasi I-01 (update
  `03_MIGRATION_SPEC.md` §2 secara singkat) akan menutup gap ini sepenuhnya — bukan blocker, murni
  kerapian dokumentasi.

## F. Kontribusi ke Knowledge Base

- [ ] Tidak ada temuan baru yang perlu dicatat
- [x] **Ada** — sudah dicatat sebagai kandidat (belum dipromosikan) di
  `06c_IMPLEMENTATION_LOG.md` §Kontribusi ke Knowledge Base: kelas risiko "menghapus 1 dependency
  untuk fix install-blocking bisa diam-diam menghilangkan dependency LAIN yang ditarik transitif
  olehnya, yang kodenya sendiri tetap bergantung padanya" (lahir dari MF-14). Juga kandidat kedua:
  "`useService('rpc')` dihapus total di 18.0, ganti `rpc()` function dari `@web/core/network/rpc`"
  (MF-13) — relevan untuk SEMUA modul custom yang masih pakai pola RPC lama, bukan spesifik modul
  ini. Kedua kandidat menunggu sesi curation eksplisit (`templates/CURATION_PROMPT.md`), tidak
  dipromosikan langsung di sini.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 1 🟡 · 5 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9
- [ ] ❌ Ditolak

**Catatan verdict:** Tidak ada issue kode yang wajib diperbaiki sebelum lanjut. Dua tindak lanjut
disarankan (bukan blocker gate ini, tapi prioritas Step 9):
1. **Wajib diverifikasi PERTAMA di Step 9:** AC-01-09 (edit baris tersimpan → dialog reopen dengan
   data) — satu-satunya AC yang langsung membuktikan fix DIFF-04 (risiko Tinggi) benar-benar bekerja
   end-to-end, belum pernah dieksekusi sama sekali sampai titik ini.
2. **Disarankan (kerapian dokumentasi, tidak blocking):** update `03_MIGRATION_SPEC.md` §2 untuk
   mereferensikan MF-13/MF-14 secara eksplisit (I-01), supaya spec teknis jadi single-source lengkap
   tanpa perlu silang-rujuk ke `FINDINGS.md` untuk tahu scope A1 final.
