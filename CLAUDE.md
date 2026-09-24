# CLAUDE.md — purchase_product_optional migration (19.0 → 20.0)

> Diinstansiasi ulang untuk migrasi 19.0→20.0 pada 2026-09-24 dari `CLAUDE_TEMPLATE.md`, menggantikan CLAUDE.md lama bertema 18.0→19.0 (SELESAI 2026-08-26). Root CLAUDE.md sebelumnya sudah digantikan file ini.
> File ini ditaruh di **ROOT `target-codebase`** (bukan di dalam `purchase_product_optional/` — lesson 18→19: file di subfolder TIDAK ter-auto-load) dan otomatis dibaca Claude Code sebagai instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap `doc-dev/migration_19.0_20.0/doc/` — bukan relatif ke root `target-codebase` langsung.
> CLAUDE.md lama (18.0→19.0) masih utuh di git: `git show migration/19.0:CLAUDE.md`.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** purchase_product_optional (kode di subfolder `purchase_product_optional/` — CLAUDE.md ini dan `doc-dev/` ada di ROOT repo, sejajar dengan subfolder itu; `depends: purchase, purchase_product_matrix, sale` — semua Community)
- **Versi:** 19.0 → 20.0
- **Sifat migrasi:** port kode saja (tanpa data produksi — instalasi baru di versi target). Diwarisi dari project 17.0→18.0 dan 18.0→19.0 (dikonfirmasi dev 2026-08-26) — **konfirmasi ulang eksplisit di Step 1 intake**. Step 7 N/A kecuali dev mengoreksi.
- **Source masih aktif dikembangkan selama migrasi?** Tidak (asumsi — branch `migration/19.0` adalah hasil akhir migrasi 18→19 yang sudah SELESAI). Konfirmasi di Step 1; kalau Ya, ikuti `SYNC_POLICY.md`.
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya — Mode Git aktif, dideteksi dari `.claude/settings.json` (varian `settings.json.mode-git.template`, bootstrap 2026-08-26, path referensi diperbarui untuk 19.0→20.0 pada 2026-09-24). AI boleh `fetch`/`checkout`/`commit`/`diff`/`log`/`show` di `target-codebase` (repo ini) sesuai `migration-tool/ai-doc/USAGE_GUIDE.md` "Mode Git", **tidak pernah** `push`/merge/force-push/PR. Auto-commit di setiap step aktif. `git push` 100% manual dev. Sebelum git pertama, pastikan GUI git client tertutup (lesson `.git/index.lock`).
- **Mulai:** 2026-09-24 (conditioning; Step 1 belum mulai)

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo lain yang terhubung ke project ini** — `migration-tool`, `native-source`/`native-target` (+Enterprise), `third-party-*`. Git hanya boleh di `target-codebase` (repo ini) sesuai scope Mode Git di atas. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja. `push`/merge/force-push/PR otomatis TETAP TERLARANG MUTLAK.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

> **Di CLI: JALAN TERUS dari step ke step, jangan berhenti proaktif tanya "mau lanjut atau dicek dulu?" tanpa alasan kuat.** Setelah Step 1 intake selesai, lanjut sampai Step 11 tanpa henti KECUALI kena salah satu dari 4 kondisi valid di `migration-tool/ai-doc/USAGE_GUIDE.md` "Prinsip: Eksekusi Berkelanjutan di CLI".

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 19.0 yang berjalan — branch `migration/19.0` di repo ini (hasil migrasi 18→19 yang sudah SELESAI), dibaca via `git show migration/19.0:<path>` / `git diff migration/19.0 migration/20.0 -- <path>` — BUKAN dokumen `doc-dev/` lama (itu cuma alat bantu/referensi awal, kode yang menang kalau menyimpang). Semua business logic, workflow, side effect, dan UX di 20.0 **harus identik** dengan 19.0 — termasuk bug/quirk yang sudah ada di sana (jangan diperbaiki, dipertahankan).

**Catatan dari migrasi sebelumnya:** project 18→19 (dan 17→18) TIDAK pernah membuat `FINDINGS.md` di root `doc/`-nya — gap & perilaku yang sengaja dipertahankan tersebar di: `doc-dev/backfill/FINDINGS.md` (F-01..F-08), `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` (CAND-01..CAND-11, termasuk CAND-08 — dua dialog "Choose Product Variants" terbuka bersamaan), `migration-tool/migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md`, dan `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (BSL-005 — override total `onchange_partner_id` core, dikonfirmasi dev dipertahankan apa adanya). Baca semuanya sebelum mulai Step 1 baseline spec, supaya perilaku yang sengaja dipertahankan tidak dianggap "baru" atau tidak sengaja "diperbaiki".

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 19.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 20.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 20.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 20.0
Step/Fase: {step/fase}
Modul: purchase_product_optional
Isu: {deskripsi singkat}
Opsi: 1) {opsi A} — Risiko: {rendah/sedang/tinggi}  2) {opsi B} — Risiko: ...
Rekomendasi: {kalau ada}
Perlu keputusan user sebelum lanjut.
```

---

## Mandatory Read Order

> **Catatan notasi versi:** file knowledge base pakai notasi singkat — `knowledge/version-diffs/19-to-20.md`, bukan `19.0-to-20.0.md`.

Sebelum membuat perubahan apapun, baca berurutan:

1. `01_intake/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/19-to-20.md` — constraint teknis umum
3. `01_intake/01b_BASELINE_SPEC.md` (kalau sudah ada) — apa yang modul lakukan di 19.0 (basis awal: `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md`, cross-check ulang ke kode 19.0 aktual)
4. `doc-dev/migration_18.0_19.0/doc/FINDINGS.md` — referensi gap migrasi sebelumnya (18→19) yang wajib dibaca sebelum mulai baseline spec 19→20. **File ini TIDAK ADA** (project 18→19 tidak membuatnya) — sebagai gantinya baca `migration-tool/migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md` + `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` + `doc-dev/backfill/FINDINGS.md` + catatan transparansi di `doc-dev/migration_18.0_19.0/doc/11_uat/11_UAT_CHECKLIST.md`
5. `FINDINGS.md` (root `doc/`, kalau sudah ada) — gap/bug/ambiguitas migrasi 19→20 yang masih terbuka (lihat `templates/FINDINGS.md`) — **project ini WAJIB membuatnya** begitu ada temuan pertama
6. `03_spec/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
7. Step/fase yang sedang berjalan (lihat tabel di bawah) + prompt fase terkait di `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

---

## Alur kerja — 11 step

Detail lengkap tiap step, alasan desain, dan template dokumen: `migration-tool/ai-doc/OVERVIEW.md`.

| # | Step | Output di `doc/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01_intake/01a_MIGRATION_INTAKE.md` + `01_intake/01b_BASELINE_SPEC.md` | Ya — functional spec/characterization test harus ada |
| 2 | Diff & compatibility analysis | `02_diff/02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_spec/03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_completeness/04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** — spec harus cover 100% source module |
| 5 | Acceptance criteria & test plan | `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` + `05_acceptance/05b_TEST_PLAN_MIGRATION.md` | Tidak |
| 6 | Code migration | kode di subfolder `purchase_product_optional/` + `06_implementation/06c_IMPLEMENTATION_LOG.md` (ref `06a_CODE_MIGRATION_PHASES.md` + `06b_PROMPTS_BY_PHASE.md`) | Tidak (tapi per-fase A→G disiplin) |
| 7 | Data migration scripts | `07_data/07_DATA_MIGRATION_PLAN.md` + script — **kondisional**, cuma kalau sifat migrasi = upgrade instance | — |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** — cek vs migration spec DAN acceptance criteria |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting (kondisional): `SYNC_POLICY.md` + `SYNC_LOG.md` di root `doc/` — kalau intake §4b menjawab "Ya" (source masih aktif dikembangkan).

Cross-cutting (direkomendasikan): `PROMPT_LOG.md` di root `doc/` — **AI wajib update tabelnya di akhir tiap giliran/sesi** (Normal/Tool-fix per step).

Cross-cutting (direkomendasikan): `FINDINGS.md` di root `doc/` — **AI wajib update begitu step manapun menemukan gap/bug/ambiguitas yang butuh keputusan manusia**. Step 4 dan Step 8 WAJIB baca file ini sebagai bagian gate.

Cross-cutting, LATEN: `HOTFIX_REVIEW.md` + `HOTFIX_LOG.md` di root `doc/` — dipicu hanya kalau `doc/MIGRATION_CLOSED.md` sudah ada (ditulis di akhir Step 11) DAN ada commit baru di branch target setelah SHA di file itu (lihat `templates/HOTFIX_REVIEW.md`).

**Cross-Version-Compare (Step 9/10, on-demand):** kalau butuh menjalankan versi 19.0 LIVE berdampingan dengan 20.0 di Docker, buat worktree fisik saat itu juga (`git worktree add <path> migration/19.0`) — lihat `templates/CROSS_VERSION_COMPARE.md`. Tidak dibuat saat conditioning.

**Konvensi penamaan:** nama file di `doc-dev/migration_19.0_20.0/doc/<step-folder>/` **selalu identik** dengan nama file template di `migration-tool/templates/` (termasuk prefix angka/huruf).

**Aturan paling penting — jangan lupa:** `03_MIGRATION_SPEC.md` (step 3) memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** dan kode 19.0 yang berjalan — BUKAN migration spec. Kalau ragu kenapa, baca §6 `ai-doc/OVERVIEW.md`.

**Phase discipline (step 6):** eksekusi HANYA scope fase yang sedang berjalan (lihat `06a_CODE_MIGRATION_PHASES.md`). Applicability Check wajib jalan dulu sebelum Fase A. Urutan A1→A2→A3→A4→A5→B1→B2→C1→C2→D1→D2→E→F→G2. Checkpoint G1 (install test) **wajib diulang di tengah Fase A** (setelah A2, setelah A3). **E (JavaScript) wajib selesai penuh sebelum F (Template)** — modul ini punya patch Owl berat (`static/src/js/purchase_product_field.js`), area risiko tertinggi di 18→19.

**Catatan QA (lesson 17→18 dan 18→19):** AI-interaktif browser tool DICOBA dan GAGAL dua kali lintas migrasi (pane tidak compositing, klik tidak sampai server) — Step 10 langsung pakai bukti Tour Odoo native yang terbukti reliable.

---

## Status saat ini

**Step 0 — Conditioning selesai (2026-09-24).** Branch `migration/20.0` dibuat dari `migration/19.0` (HEAD `4736c36`, "Perbaikan struktur: pindahkan CLAUDE.md + doc-dev/ ke root repo", setelah "Step 11 ditutup" `8e5767d`). `.claude/settings.json` diperbarui (deny list native 19/20, `git show` diizinkan), CLAUDE.md ini ditulis ulang, skeleton `doc-dev/migration_19.0_20.0/doc/` dibuat (folder kosong + `.gitkeep`). **Step 1 Intake belum mulai** — sesi eksekusi berikutnya mulai dari Step 1.

Open item untuk Step 1 intake (dicatat saat conditioning, belum diputuskan):
- CLAUDE.md lama menyebut branch hasil migrasi `migration/19.0_target`, tapi nama aktual branch-nya `migration/19.0` (lokal = `origin/migration/19.0`). Semua rujukan di file ini sudah pakai nama aktual.
- Gap yang diterima sadar di sign-off 18→19 dan terbawa ke baseline 19.0: T-03 (edit ulang konfigurasi baris) **tanpa evidence eksekusi apapun**; S-06 (fallback grid configurator, CAND-07 kemungkinan unreachable) belum tervalidasi runtime; AC-02-02, AC-04-01, AC-05-02 tanpa test existing; gap visual/UI tidak pernah diverifikasi mata manusia.
- Branch rilis `19.0`/`staging/19.0` berisi 5 commit pasca-migrasi yang TIDAK ada di `migration/19.0` (commit "cleaning" + aset store: `banner.gif`, update folder `assets`, hapus folder `img`, `index.html`, fix key `images` di manifest). Putuskan di intake apakah aset store perlu di-port ke 20.0.

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus lanjut dari mana tanpa tanya ulang ke user.

### Status per Step

Ringkasan cepat — detail lengkap tiap step ada di field `Status:` di header masing-masing file `doc/<step>/`. Tabel ini WAJIB di-update AI setiap kali satu step/dokumen berubah status.

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ⬜ Belum mulai | ⏳ Menunggu review user |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ⬜ Belum mulai | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ⬜ Belum mulai | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ⬜ Belum mulai | — |
| 5 | Acceptance Criteria & Test Plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05b_TEST_PLAN_MIGRATION.md` | ⬜ Belum mulai | — |
| 6 | Code Migration | kode `purchase_product_optional/` + `06c_IMPLEMENTATION_LOG.md` | ⬜ Belum mulai | — (disiplin per-fase A1→G2) |
| 7 | Data Migration Scripts | `07_DATA_MIGRATION_PLAN.md` + script — cuma kalau upgrade instance | ⬜ Belum mulai / — (n/a kalau port kode saja) | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ⬜ Belum mulai | — |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ⬜ Belum mulai | — |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | ⬜ Belum mulai | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda status: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang di-connect

> Semua folder referensi sudah diketahui path-nya sejak conditioning. Di akhir Step 1, tetap konfirmasi ulang ke dev (checklist `01a_MIGRATION_INTAKE.md` §0).

| Folder | Path | Peran | Read-only? |
|---|---|---|---|
| `target-codebase` (folder UTAMA) | `D:\Kuncoro\doodex\repo\purchase-product-optional-migration-20` (branch `migration/20.0`) | CLAUDE.md + `doc-dev/` di ROOT; kode modul & migrasi di subfolder `purchase_product_optional/` | Tidak |
| `migration-tool` | `D:\Kuncoro\doodex\repo\migration-tool-project\migration-tool` | Template + `ai-doc/OVERVIEW.md`; tulis ke `migration-records/purchase_product_optional_19.0_20.0/` | Tulis di `migration-records/` saja |
| `native-source` (Community 19.0) | `D:\Kuncoro\doodex\repo\odoo19` (git, branch `19.0`) | Cross-check API core 19.0 (`purchase`, `purchase_product_matrix`, `sale`) | Ya |
| `native-source-enterprise` (Enterprise 19.0) | `D:\Kuncoro\doodex\repo\enterprise19` (git, branch `19.0`, addons-only) | Referensi — dependency modul Community-only, tapi dev minta tetap di-connect (instance produksi kemungkinan jalan Enterprise) | Ya |
| `native-target` (Community 20.0) | `D:\Kuncoro\doodex\repo\odoo20` (git, branch `20.0`) | Diff API core 20.0 (step 2) | Ya |
| `native-target-enterprise` (Enterprise 20.0) | `D:\Kuncoro\doodex\repo\enterprise20` (git, branch `20.0`, addons-only) | Referensi Enterprise 20.0 — cek juga apakah `purchase_product_matrix`/configurator berpindah lisensi di 20.0 (lesson 17→18: `sale_product_configurator` pernah Enterprise) | Ya |
| `third-party-*` | — | Tidak ada — dikonfirmasi dev di 18→19 | — |

> **Tidak ada `source-codebase` folder terpisah.** Kode versi 19.0 direferensikan via `git diff`/`git show` ke branch `migration/19.0` di repo yang sama, tanpa folder terpisah. Worktree fisik hanya dibuat on-demand untuk Cross-Version-Compare (lihat §Alur kerja).

> **Struktur native (dicek 2026-09-24):** model dua-clone standar — `odoo19`/`odoo20` repo Community penuh, `enterprise19`/`enterprise20` addons-only terpisah. Empat path terpisah, versi tepat: source = `odoo19` + `enterprise19`, target = `odoo20` + `enterprise20`. BUKAN folder gabungan Community+Enterprise satu folder seperti yang dipakai project 18→19 (folder gabungan itu sudah tidak ada).

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` — `version-diffs/19-to-20.md` sudah ada (dari `optional_field_save` dan `pos-margin-sale`), plus `dependency-compat/purchase_product_matrix/18-to-19.md` (many2one `record.data` tuple→objek, `useMatrixConfigurator()` hook) sebagai konteks pasangan versi sebelumnya.

Temuan baru ditulis ke `migration-tool/migration-records/purchase_product_optional_19.0_20.0/SUMMARY.md` saat itu juga — **BUKAN** langsung ke `migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Riwayat migrasi sebelumnya (referensi historis — JANGAN dihapus)

| Project | Dokumen | Status | Catatan |
|---|---|---|---|
| Backfill 17.0 | `doc-dev/backfill/` (`spec/01A_FUNCTIONAL_SPEC.md`, `FINDINGS.md` F-01..F-08) | Selesai | Baseline behavior modul asli 17.0 |
| Migrasi 17.0→18.0 | `doc-dev/migration_17.0_18.0/doc/` (`01_intake/01b_BASELINE_SPEC.md`; tidak ada `FINDINGS.md`) | SELESAI | Branch `migration/18.0`. Migration record: `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` (CAND-01..11) |
| Migrasi 18.0→19.0 | `doc-dev/migration_18.0_19.0/doc/` — **baseline behavior:** `01_intake/01b_BASELINE_SPEC.md`; **gap yang sengaja dipertahankan:** tidak ada `FINDINGS.md` — lihat migration record + `11_uat/11_UAT_CHECKLIST.md` | SELESAI 2026-08-26 (UAT di-sign-off berbasis test AI — penyimpangan eksplisit) | Branch `migration/19.0` (di dokumen lama tertulis `migration/19.0_target`). Perubahan kode: manifest bump, `type='json'`→`'jsonrpc'` (4 route), rewrite `purchase_product_field.js` (DIFF-01 many2one tuple→objek, DIFF-02 `_openGridConfigurator` dihapus → `useMatrixConfigurator`, normalisasi `customAttributeValues` CAND-04). G1+G2 PASS, 13/13 test pass, Tour 15 langkah sukses, code review 0🔴 0🟡 0🔵, QA 6/7 Pass. Migration record: `migration-tool/migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md` |

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Panduan operasional: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Diagram dua jalur dokumen (functional vs teknis): `migration-tool/ai-doc/diagrams/spec-vs-test-tracks.svg`
