# CLAUDE.md — purchase_product_optional migration (17.0 → 18.0)

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** purchase_product_optional
- **Versi:** 17.0 → 18.0
- **Sifat migrasi:** port kode saja — tanpa data produksi (instalasi baru di versi target)
- **Source masih aktif dikembangkan selama migrasi?** Tidak — source module (`source-codebase`,
  `purchase-product-optional`) dibekukan selama migrasi berjalan. `SYNC_POLICY.md`/`SYNC_LOG.md`
  tidak dibuat.
- **Mulai:** 2026-07-29

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Catatan khusus project ini (Test 2b, `migration-tool/ai-doc/ROADMAP.md` §3):** dua variabel baru
> divalidasi bersamaan — (1) modul ini punya komponen Owl/JS sungguhan (Fase E/F step 6 WAJIB
> dikerjakan penuh, bukan N/A — belum pernah tervalidasi di project migrasi sebelumnya), dan
> (2) project migrasi PERTAMA yang pakai struktur 3-clone baru (`migration-tool` + `source-codebase`
> + `target-codebase` terpisah, CLAUDE.md+doc di root `target-codebase`). Kalau ada bagian yang
> terasa janggal, sudah dicatat & ditandai sumbernya (`[OWL/JS]` vs `[STRUKTUR-FOLDER]`) di
> `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` — lanjutkan
> kebiasaan itu di sesi-sesi berikutnya, jangan biarkan dua sinyal itu bercampur.

> **Larangan mutlak: JANGAN jalankan command `git` apapun (lewat Bash/sandbox Cowork) di REPO MANAPUN yang terhubung ke project ini** — `migration-tool`, `source-codebase` (`purchase-product-optional`), `target-codebase` (`purchase-product-18`). Ini termasuk command read-only (`git status`, `git log`, `git branch`), bukan cuma yang mengubah state (`checkout`/`commit`/`add`). Alasan & insiden nyata: `migration-tool/ai-doc/USAGE_GUIDE.md` §1 dan §5 (dua kejadian `.git/index.lock` macet, salah satunya dipicu `git status` doang). Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja. Kalau butuh info repo (branch aktif/riwayat commit/status), tanya dev — jangan cari tahu sendiri lewat `git`.

> **Setiap kali menyerahkan aksi ke dev (git commit, jalankan docker, install test, dst) — beri langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".** Lihat `migration-tool/ai-doc/USAGE_GUIDE.md` "Prinsip: Serah-terima ke Dev Selalu Eksplisit".

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 17.0 yang berjalan (atau `01b_BASELINE_SPEC.md` sebagai dokumentasinya) adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 18.0 **harus identik** dengan 17.0 — termasuk bug yang sudah ada di sana (jangan diperbaiki, dipertahankan). Modul ini sudah punya 6 bug/quirk terdokumentasi dari project BACKFILL sebelumnya (F-01..F-06 di `doc-dev/backfill/FINDINGS.md`) — SEMUA wajib dipertahankan identik di 18.0, bukan diperbaiki "sekalian".

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 17.0 (termasuk F-01..F-06 — lihat `doc-dev/backfill/FINDINGS.md`)
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 18.0 — itu wajib, mis. `<tree>`→`<list>`)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 18.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 18.0
Step/Fase: {step/fase}
Modul: purchase_product_optional
Isu: {deskripsi singkat}
Opsi: 1) {opsi A} — Risiko: {rendah/sedang/tinggi}  2) {opsi B} — Risiko: ...
Rekomendasi: {kalau ada}
Perlu keputusan user sebelum lanjut.
```

---

## Mandatory Read Order

Sebelum membuat perubahan apapun, baca berurutan:

1. `doc-dev/migration_17_18/doc/01_intake/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/17-to-18.md` — constraint teknis umum (termasuk blocker `<tree>`→`<list>` yang SUDAH dikonfirmasi relevan ke modul ini)
3. `doc-dev/migration_17_18/doc/01_intake/01b_BASELINE_SPEC.md` — apa yang modul lakukan (disusun dari `doc-dev/backfill/spec/` + cross-check kode langsung)
4. `doc-dev/migration_17_18/doc/FINDINGS.md` — konsolidasi gap/bug yang butuh keputusan manusia (MF-01..MF-06, semua diwarisi dari `doc-dev/backfill/FINDINGS.md` F-01..F-06 — lihat `migration-tool/templates/FINDINGS.md` untuk beda perannya dari `[GAP]`/`ESCALATION`)
5. `doc-dev/migration_17_18/doc/03_spec/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
6. Step/fase yang sedang berjalan (lihat tabel di bawah) + prompt fase terkait di `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

---

## Alur kerja — 11 step

Detail lengkap tiap step, alasan desain, dan template dokumen: `ai-doc/OVERVIEW.md` di folder `migration-tool`.

| # | Step | Output di `doc/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01_intake/01a_MIGRATION_INTAKE.md` + `01_intake/01b_BASELINE_SPEC.md` | Ya — functional spec/characterization test harus ada |
| 2 | Diff & compatibility analysis | `02_diff/02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_spec/03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_completeness/04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** — spec harus cover 100% source module |
| 5 | Acceptance criteria & test plan | `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` + `05_acceptance/05b_TEST_PLAN_MIGRATION.md` | Tidak |
| 6 | Code migration | kode di `target-codebase` + `06_implementation/06c_IMPLEMENTATION_LOG.md` (ref `06a_CODE_MIGRATION_PHASES.md` + `06b_PROMPTS_BY_PHASE.md`) | Tidak (tapi per-fase A→G disiplin) |
| 7 | Data migration scripts | — **N/A, sifat migrasi = port kode saja** | — |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** — cek vs migration spec DAN acceptance criteria |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` — hasil test vs acceptance criteria | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting (direkomendasikan, tidak kondisional): `PROMPT_LOG.md` di root `doc/` — **AI wajib update tabelnya di akhir tiap giliran/sesi**.

**Konvensi penamaan:** nama file di `doc-dev/migration_17_18/doc/<step-folder>/` **selalu identik** dengan nama file template di `migration-tool/templates/`.

**Aturan paling penting — jangan lupa:** `03_MIGRATION_SPEC.md` (step 3) memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** dan kode 17.0 yang berjalan — BUKAN migration spec.

**Phase discipline (step 6 — Code Migration):** eksekusi HANYA scope fase yang sedang berjalan (lihat `06a_CODE_MIGRATION_PHASES.md`). Applicability Check wajib jalan dulu sebelum Fase A — untuk modul ini, `01a_MIGRATION_INTAKE.md` §2b sudah memastikan Fase D1 (controllers), D2/E/F (assets/JS/Owl) SEMUA relevan (bukan N/A) — ini modul kandidat "Owl/JS sungguhan" Test 2b. Urutan A1→A2→A3→A4→A5→B1→B2→C1→C2→D1→D2→E→F→G2. Checkpoint G1 wajib diulang setelah A2, setelah A3. **E (JavaScript) wajib selesai penuh sebelum F (Template)**, kebalikannya menyebabkan `OwlError: Unknown QWeb directive`.

---

## Status saat ini

✔️ **Step 1 (Intake & Scope) LULUS GATE (2026-07-29)** — user mengonfirmasi tidak ada poin
mengkhawatirkan di "Ringkasan untuk Review" `01a_MIGRATION_INTAKE.md`. Lanjut ke Step 2 (Diff &
Compatibility Analysis).

✅ **Step 2 (Diff & Compatibility Analysis) draft selesai (2026-07-29)** — `native-target`
(`D:\Kuncoro\doodex\repo\odoo18`, Community) di-connect user. Ditemukan 2 hal KRITIS yang belum
diketahui sebelumnya: (1) `sale_product_configurator` **dihapus total** di 18.0 (fungsinya pindah ke
`product`/`sale` core) — install-breaking, wajib fix manifest Fase A1; (2) `purchase_product_matrix`
ternyata Community (bukan Enterprise seperti dugaan awal), dan `PurchaseOrderLineProductField`-nya
berubah struktur besar — method `_editProductConfiguration` yang di-patch modul ini **tidak ada lagi**
(jadi dead code, regresi silent di BSL-009) kalau tidak di-rename ke `onEditConfiguration` saat step 6.
Juga ditemukan `result.purchase_warning` kemungkinan tidak pernah terkirim lagi di 18.0 (perlu
verifikasi G1/G2 nyata). Detail lengkap: `doc-dev/migration_17_18/doc/02_diff/02_DIFF_ANALYSIS.md`,
`FINDINGS.md` (MF-07..MF-10). MF-05 (BACKFILL) ditutup `✅ RESOLVED` — `_convert()` dikonfirmasi aman
juga di 18.0. Menunggu review user sebelum lanjut Step 3 (tidak ada gate formal di step 2, tapi
temuan ini cukup signifikan untuk dikonfirmasi dulu).

**Koreksi 2026-07-29 (lesson penting, sesi sama):** draft Step 2 di atas sempat ditulis HANYA dari
`native-target` (Community), TANPA cek Enterprise 18.0 dulu — user menegaskan ini tergesa. Enterprise
18.0 (`enterprise18`) di-connect susulan, ditemukan **DIFF-07/MF-11 (baru)**: field `product_add_mode`
(F-01/MF-01) ternyata meniru pola SAH `sale_product_matrix` (field related + override
`get_single_product_variant` inject `res['mode']`) — tapi modul ini tidak pernah menambahkan bagian
kedua (override Python-nya). `purchase_product_matrix` 18.0 malah punya comment eksplisit "purchase
cuma pakai matrix, tidak perlu cek `product_add_mode`" — desain SENGAJA Purchase core tidak dapat
mekanisme ini. Kesimpulan: BSL-007/AC-01-06 (cabang grid via `result.mode`) kemungkinan tidak pernah
reachable, baik di 17.0 maupun 18.0 — bukan regresi migrasi. DIFF-02/DIFF-03 makin dikonfirmasi (juga
tidak ada di Enterprise). **Pelajaran untuk sesi berikutnya: JANGAN anggap step 2 selesai kalau
`native-target` DAN Enterprise (kalau modul depend ke Enterprise) belum keduanya dicek** — folder
`native-target` di §Folder yang perlu di-connect sekarang dipecah jadi baris Community + Enterprise
terpisah supaya tidak terlewat lagi.

✅ **Step 3 (Migration Spec teknis) draft selesai (2026-07-29)** — `03_spec/03_MIGRATION_SPEC.md`
ditulis lengkap dari DIFF-01..07/MF-01..11/BSL-001..028 (murni sintesis, tanpa riset baru). Isi
utama: 3 fix mekanis wajib (manifest hapus `sale_product_configurator` + bump version, `<tree>`→
`<list>` 3 titik, rename `_editProductConfiguration`→`onEditConfiguration`), 2 area verifikasi-saja
(DIFF-05 `_openGridConfigurator()` tanpa argumen, method controller yang pindah dari
`sale_product_configurator`→`product`), 2 area yang eksplisit didokumentasikan sebagai "tetap
identik, jangan diperbaiki" (DIFF-03 `purchase_warning`, DIFF-07 `result.mode`). Tidak ada gate
formal di step 3, tapi mengandung keputusan scope yang perlu diketahui user sebelum step 6: F-01
(`product_add_mode`) tetap TIDAK diperbaiki meski sekarang dipahami lebih jelas kenapa dia rusak.

✔️ **Step 4 (Spec Completeness Review) LULUS GATE (2026-07-29)** — `04_SPEC_COMPLETENESS_REVIEW.md`
dibuat dari enumerasi `find` penuh atas `source-codebase` (bukan asumsi struktur). Ditemukan 4
kategori elemen belum eksplisit tercakup di spec step 3 (`tests/*.py` 5 file, `i18n/*.po`,
`static/description/*`, root misc README/LICENSE/dll) — semua ditambahkan langsung ke
`03_MIGRATION_SPEC.md` §2 sebelum gate ditutup (gap murni cakupan dokumen, bukan strategi salah,
jadi tidak perlu balik ulang seluruh step 3). Tidak ada model baru di modul ini → `security/`,
`data/`, `report/`, `wizard/` semuanya N/A (dikonfirmasi, bukan terlewat). Catatan penting untuk
step 5: `tests/*.py` (suite BACKFILL, 11/11 pass run #7) WAJIB di-re-run di environment 18.0 sebagai
baseline regresi step 9, bukan diasumsikan otomatis pass.

✅ **Step 5 (Acceptance Criteria & Test Plan) draft selesai (2026-07-29)** — `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
mewarisi AC-01..AC-09 dari `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md` (traceable ke
BSL-001..028), plus **AC-10 baru** untuk F-06 (dialog overlap) yang sebelumnya tidak pernah punya AC
formal. AC yang overlap risiko migrasi (DIFF-03/04/05/07) ditandai eksplisit `⚠` — terutama AC-01-09
(dampak langsung rename DIFF-04) dan AC-01-03/04/06 (buktikan `purchase_warning`/`result.mode`
unreachable atau tidak di 18.0, bukan diasumsikan). `05b_TEST_PLAN_MIGRATION.md` memetakan tugas step
9 sebagai **re-run suite existing** (bukan tulis ulang) di environment 18.0 + 1 gap ditemukan: AC-10
(F-06) belum punya test otomatis sama sekali (hanya manual/AI-Browser BACKFILL) — jadi step 10
AI-interaktif jadi wajib, bukan opsional, untuk AC ini. Tidak ada gate formal di step 5.

🔄 **Step 6 (Code Migration) DIMULAI (2026-07-29)** — Applicability Check dicatat di
`06c_IMPLEMENTATION_LOG.md` (B2/C2 N/A, D1/D2/E/F relevan, sesuai `01a` §2b). **Fase A1** (manifest:
hapus `sale_product_configurator`, bump version 18.0.1.0.0) dan **Fase A2** (4 titik `<tree>`→`<list>`
di `views/purchase_order_views.xml` — ternyata 4, bukan 3 seperti dugaan awal, lihat log) sudah
selesai. **Checkpoint G1 #1 PASS** (Mode B, docker instance 18.0 baru/terpisah dari BACKFILL 17.0 di
`docker-env/`, port 8082) — 51 modul loaded bersih, tanpa error. 3 WARNING semua expected: 2×
konfirmasi MF-01/BSL-008 tetap identik, 1× temuan baru **MF-12** (label duplikat "ID", kosmetik,
bukan regresi — sudah dicatat `FINDINGS.md`). A3 dikonfirmasi N/A (tidak ada `security/`).

**A4, A5, B1, C1, D1, D2 semua selesai (2026-07-29)** — mayoritas "DITINJAU, TIDAK ADA PERUBAHAN":
struktur folder/`__init__.py` sudah bersih (A4), 3 file model sudah kompatibel API 18.0 tanpa
perubahan (A5/B1 — tidak ada `create()` override, `.sudo()` sudah benar, tidak ada API deprecated),
tree→list sudah tuntas via A2 (C1), controller (D1) & SCSS (D2) dicek struktural tapi verifikasi
runtime nyata (signature method yang pindah modul, compile SCSS) dilimpahkan ke G2/step 9 — bukan
diasumsikan aman hanya dari baca kode.

**Fase E & F selesai (2026-07-29)** — DIFF-04 (`_editProductConfiguration`→`onEditConfiguration`) dan
DIFF-05 (`_openGridConfigurator(false)` eksplisit) dieksekusi di `purchase_product_field.js`. 5
komponen Owl lain + 5 template XML: **DITINJAU, TIDAK ADA PERUBAHAN** (sudah Owl 2/QWeb modern dari
awal) — mengonfirmasi modul ini bukan kasus Owl-classic terberat yang dikhawatirkan Test 2b.

🔄 **Fase G2 (validasi runtime browser) SEDANG BERJALAN (2026-07-29)** — server hidup (Mode B, docker
18.0, port 8082), data test dibuat via UI ("Customizable Desk" + vendor baru), dicoba live via
Claude in Chrome. **2 bug ditemukan, TIDAK terdeteksi review statis Fase E** (validasi kuat prinsip
G1≠G2 — G1 cuma cek install Python/XML, bukan runtime JS/Owl browser):

1. **MF-13** (`useService("rpc")` dihapus total di 18.0) — dialog crash instan saat dibuka. Fix:
   ganti ke `import { rpc } from "@web/core/network/rpc"` + panggilan langsung, mengikuti idiom
   native `sale` 18.0. **Sudah diperbaiki & diverifikasi ulang (error hilang).**
2. **MF-14** (`optional_product_ids`/`has_optional_products` tidak ada tanpa modul `sale`) — setelah
   MF-13 fix, dialog crash lagi (`AttributeError` di `controllers/main.py:90`). Root cause: field ini
   HANYA didefinisikan di `sale/models/product_template.py`, sebelumnya tertarik transitif lewat
   `sale_product_configurator` (dihapus sesuai DIFF-02) — TIDAK ada penggantinya di `purchase`/
   `product` bare. **Dieskalasi ke user (2026-07-29) — user pilih tambah `'sale'` eksplisit ke
   `depends`** (net footprint sama seperti 17.0, cuma sekarang eksplisit). Sudah diedit di
   `__manifest__.py`, `docker-compose.yml` command diganti `-i`→`-u` (supaya Odoo mendeteksi
   dependency baru pada modul yang sudah terinstall). **Belum di-restart & di-retest** — ini next
   step begitu sesi lanjut.

**✔️ Fase G2 SELESAI (2026-07-29)** — container direstart dengan `-u purchase_product_optional`
(`sale` berhasil terinstall, 58→59 modul, tanpa error). Retest live browser: dialog "Configure your
product" terbuka BERSIH — Legs, Color, DAN section "Add optional products" (fitur inti yang tadi
mati karena MF-14) semua render & berfungsi. **MF-13 dan MF-14 KONFIRMASI RESOLVED lewat eksekusi
nyata**, bukan cuma baca kode.

Efek samping bernilai: begitu dialog custom terbuka bersih, grid "Choose Product Variants"
(`purchase_product_matrix`) ikut terbuka BERSAMAAN — mereproduksi **F-06/MF-06 identik** dengan
17.0 (baris produk utama "Customizable Desk" hilang total dari PO setelah confirm dialog custom,
hanya optional product "Conference Chair" tersisa, silent tanpa error). Bug warisan dikonfirmasi
TETAP IDENTIK di 18.0, sesuai prinsip Source of Truth — tidak diperbaiki. Detail tambahan (bukan
regresi): console menunjukkan 3× `Error: Component is destroyed` (kemungkinan Owl 2 lebih strict
soal lifecycle vs Owl 1). Harga `$0.00` selama test — kemungkinan besar db demo 18.0 belum ada
`supplierinfo` custom (bukan regresi MF-04), dilimpahkan ke Step 10 untuk verifikasi dengan setup
data yang sepadan.

Detail lengkap: `FINDINGS.md` MF-13/MF-14 (+ catatan MF-06 reproduksi), `06c_IMPLEMENTATION_LOG.md`
§[Fase G2].

**Step 6 (Code Migration) SELESAI.** **Step 7 N/A** (port kode saja, dikonfirmasi ulang, tidak ada
tindakan). **✔️ Step 8 (Code Review) SELESAI (2026-07-29)** — `08_review/08_CODE_REVIEW.md` ditulis:
0 🔴, 1 🟡 (dokumentasi — `03_MIGRATION_SPEC.md` sudah diupdate retroaktif menyebut MF-13/MF-14), 5 🔵
(semua warisan/observasi, bukan regresi). **Verdict: ✅ Lulus gate**, lanjut Step 9. Satu catatan
prioritas dibawa ke Step 9: **AC-01-09** (edit baris tersimpan → dialog reopen dengan data,
pembuktian langsung fix DIFF-04 risiko Tinggi) belum pernah dieksekusi sama sekali — jadikan
skenario PERTAMA yang dites di Step 9, sebelum re-run suite Python lengkap.

**✔️ Step 9 (Dev Testing) SELESAI (2026-07-29)** — `09_devtest/09_DEV_TESTING.md` ditulis. Re-run
`tests/*.py` di environment 18.0 Mode B (fresh db `_test`, install dari nol termasuk `sale`): **0
failed, 0 error(s) of 13 tests** — 11/11 Unit+Integration PASS, IDENTIK baseline BACKFILL 17.0 run
#7 (tidak ada regresi). Tour/QUnit tetap SKIP ("Chrome executable not found") — limitasi lingkungan
sama seperti BACKFILL, bukan kegagalan baru. **AC-01-09 (prioritas dari Code Review) diverifikasi
live via browser: PASS** — dialog reopen dengan Legs=Steel/Color=White tersimpan, membuktikan fix
DIFF-04 bekerja end-to-end. F-06/MF-06 direproduksi lagi (konsisten). **Verdict: ✅ Lulus, lanjut
Step 10.** 5 item dibawa ke Step 10 (AC-01-01..06, AC-05, AC-06, AC-10-03 verifikasi lebih teliti,
reproduksi F-06 penuh terkontrol) — lihat detail lengkap di `09_DEV_TESTING.md`.

**✔️ Step 10 (QA Testing) SELESAI (2026-07-30)** — `10_qa/10_BUSINESS_FLOW_MIGRATION.md` ditulis
dengan 10 skenario (S-01..S-10, ber-`Level` Smoke/Main Flow/Detail/Negative) + folder `human_qa/`
(5 file) digenerate. Setup data test dilengkapi: `supplierinfo` Azure Interior @ $350.00 di
"Customizable Desk", toggle "Warnings" diaktifkan di Settings > Purchase.

Hasil kunci:
- **AC-05/AC-06 (harga vendor + DOM `id_vendor_0`):** ✅ PASS — dengan `supplierinfo` lengkap, harga
  tampil benar ($350.00), vendor id terbaca benar dari DOM. Anomali harga $500/variant-mismatch yang
  sempat terlihat di Step 9 terbukti murni gap setup data, BUKAN bug.
- **AC-01-03/04 (DIFF-03, `purchase_warning`)** dan **AC-01-06 (DIFF-07, `result.mode`):**
  **CONFIRMED unreachable secara definitif** lewat baca kode (`get_single_product_variant` 18.0
  tidak pernah mengisi `purchase_warning`/`mode`) DAN live test (dialog peringatan yang muncul saat
  produk punya `purchase_line_warn` terbukti berasal dari mekanisme NATIVE core `purchase.order.line`
  onchange, bukan dari `WarningDialog` custom modul ini — membuktikan cabang custom benar-benar dead
  code). Bukan regresi migrasi — sesuai prediksi step 2/3.
- **AC-10-01/02/03 (F-06/MF-06, dialog overlap):** direproduksi ulang terkontrol. Grid ditutup +
  hanya dialog depan confirm → baris utama hilang total (P00016, identik 17.0). Grid confirm dulu
  baru dialog depan → satu baris bersih, harga/varian konsisten (P00015) — resolusi bersih untuk
  ambiguitas Step 9.
- **AC-09-02** (guard kombinasi invalid): tidak berhasil direproduksi via UI manual (radio button
  hanya menampilkan opsi valid) — dicatat sebagai limitasi eksekusi (bukan kegagalan), risiko rendah
  karena kode terkait tidak disentuh migrasi.

**Verdict: ✅ Lulus, lanjut Step 11 (UAT Sign-off).** 9/10 skenario dieksekusi live dan PASS. Detail
lengkap: `10_qa/10_BUSINESS_FLOW_MIGRATION.md`, `FINDINGS.md` (MF-08/MF-11 resolved, MF-04/MF-06
terkonfirmasi ulang).

Lanjut ke **Step 11 (UAT Sign-off)** — belum dimulai.

---

### Riwayat (Step 1, selesai)

Bootstrap project baru selesai (2026-07-29):
CLAUDE.md ini diinstansiasi dari `CLAUDE_TEMPLATE.md`, struktur folder `doc-dev/migration_17_18/doc/`
dibuat. Ditemukan sejak awal (sebelum `01a`/`01b` ditulis): `target-codebase` ternyata byte-identical
dengan `source-codebase`, keduanya sudah membawa hasil project BACKFILL sebelumnya
(`doc-dev/backfill/` — FINDINGS.md dengan 6 finding F-01..F-06 terkonfirmasi, 01A_FUNCTIONAL_SPEC.md,
01B_ACCEPTANCE_CRITERIA.md, tests/). Ini dipakai sebagai "FUNCTIONAL_SPEC.md lama" untuk mengisi
`01b_BASELINE_SPEC.md` (lihat `01a_MIGRATION_INTAKE.md` §4). Detail lengkap anomali struktural &
catatan Owl/JS awal: `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`.

Blocker install kritis untuk 18.0 sudah teridentifikasi di step 1 (dari baca `views/purchase_order_views.xml`):
pemakaian `<tree>` (2× xpath target + 1× inner tree) — akan jadi fokus utama Fase C (Views) di step 6.

**`doc-dev/migration_17_18/doc/FINDINGS.md` sudah dibuat (2026-07-29)** — instance PERTAMA yang
memakai mekanisme `FINDINGS.md` baru di `migration-tool` (ditambahkan hari ini atas permintaan
eksplisit user, lihat `migration-tool/ai-doc/OVERVIEW.md` §11). Berisi `MF-01`..`MF-06`, semua
diwarisi dari 6 finding BACKFILL (`F-01`..`F-06`) — WAJIB diverifikasi ulang tetap identik di 18.0
saat step 6/9/10 tiba, terutama `MF-04` (risiko konkret: konvensi DOM id Odoo bisa berubah antar
versi) dan `MF-05` (signature `res.currency._convert()` perlu dicek ulang di step 2).

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus lanjut dari mana tanpa tanya ulang ke user.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✅ Selesai | ✔️ Lulus (dikonfirmasi user 2026-07-29) |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ✅ Draft selesai | Tidak ada gate formal — menunggu konfirmasi user karena temuan signifikan |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ✅ Draft selesai | Tidak ada gate formal |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ✅ Selesai | ✔️ Lulus (2026-07-29, 4 gap cakupan diperbaiki di tempat) |
| 5 | Acceptance Criteria & Test Plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05b_TEST_PLAN_MIGRATION.md` | ✅ Draft selesai | Tidak ada gate formal |
| 6 | Code Migration | kode `target-codebase` + `06c_IMPLEMENTATION_LOG.md` | ✅ Selesai — A1→G2 semua tuntas, MF-13/MF-14 resolved & terverifikasi, F-06/MF-06 dikonfirmasi identik | — (disiplin per-fase A1→G2) |
| 7 | Data Migration Scripts | — | N/A — port kode saja | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ✅ Selesai | ✔️ Lulus (0 🔴, 2026-07-29) |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ✅ Selesai | ✔️ Lulus (11/11 Unit+Integration pass; Tour/QUnit dilimpahkan ke Step 10) |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` + `human_qa/` | ✅ Selesai | ✔️ Lulus (9/10 skenario PASS live, 2026-07-30; DIFF-03/DIFF-07 confirmed unreachable, F-06 direproduksi terkontrol) |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda status: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Perlu di step | Read-only? | Status |
|---|---|---|---|
| `target-codebase` (`purchase-product-18`, folder UTAMA) | 1, 6, 7, 8 | Tidak | ✅ Connected |
| `migration-tool` | Semua step | Tulis di `migration-records/` saja | ✅ Connected |
| `source-codebase` (`purchase-product-optional`) | 1, 2, 4, 8 | Ya | ✅ Connected |
| `native-target` (Community) | 2 (diff API core/enterprise) | Ya | ✅ Connected (`D:\Kuncoro\doodex\repo\odoo18`) 2026-07-29 |
| `enterprise18` (Enterprise 18.0) | 2 (diff API Enterprise — WAJIB dicek juga, bukan cuma Community, lesson 2026-07-29) | Ya | ✅ Connected (`D:\Kuncoro\doodex\repo\enterprise18`) 2026-07-29 |
| `native-source` | 2 (diff API core/enterprise, versi 17.0) | Ya | Belum di-connect — cukup pakai baseline 17.0 (`01b_BASELINE_SPEC.md`, sudah divalidasi eksekusi nyata BACKFILL) untuk saat ini, minta kalau perlu cross-check langsung |
| `third-party-source` / `third-party-target` | 2 (kalau ada dependency OCA) | Ya | Belum relevan — dependency modul ini (`purchase`, `purchase_product_matrix`, `sale_product_configurator`) semuanya native/Enterprise Odoo, bukan OCA |

---

## Knowledge base

Sebelum step 2 mulai analisis, cek dulu `migration-tool/knowledge/INDEX.md` — sudah ada entry
`version-diffs/17-to-18.md` (dipakai project sebelumnya) yang relevan langsung ke modul ini, termasuk
blocker `<tree>`→`<list>` yang sudah dikonfirmasi dipakai modul ini di `views/purchase_order_views.xml`.

Temuan baru (general atau dependency-specific) ditulis ke
`migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` — BUKAN langsung ke
`migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Diagram dua jalur dokumen (functional vs teknis): `migration-tool/ai-doc/diagrams/spec-vs-test-tracks.svg`
- Hasil project BACKFILL sebelumnya (dipakai sebagai "FUNCTIONAL_SPEC.md lama" untuk step 1): `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`, `doc-dev/backfill/FINDINGS.md`
- Catatan anomali struktural + Owl/JS project ini: `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`
