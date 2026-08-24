# CLAUDE.md — purchase_product_optional migration (17.0 → 18.0)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-08-24.
> File ini menggantikan CLAUDE.md BACKFILL sebelumnya (overwrite penuh, bukan merge — dua identitas
> "BACKFILL copilot" vs "migration copilot" tidak coexist). Isi BACKFILL lama masih ada di
> `source-codebase` (`purchase-product-optional-migration-18-source/purchase_product_optional/CLAUDE.md`),
> tidak hilang.
> Semua path `doc/...` yang disebut di file ini relatif terhadap
> `doc-dev/migration_17.0_18.0/doc/` — bukan relatif ke root `target-codebase` langsung.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** purchase_product_optional
- **Versi:** 17.0 → 18.0
- **Sifat migrasi:** port kode saja (tanpa data lama, instalasi baru di versi target)
- **Source masih aktif dikembangkan selama migrasi?** Tidak — source module dibekukan selama migrasi berjalan (default)
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya — Mode Git aktif (lihat `migration-tool/ai-doc/USAGE_GUIDE.md` "Mode Git"). Scope: HANYA `target-codebase` ini + bootstrap `source-codebase` (sudah selesai, 2026-08-24). Tidak pernah `push`/merge/force-push — itu tetap manual dev. Auto-commit di tiap gate (Step 1/4/8/9/10/11) aktif per `settings.json.mode-git` yang sudah ter-bootstrap di repo ini.
- **Mulai:** 2026-08-24

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di REPO MANAPUN yang terhubung ke project ini** — `migration-tool`, `source-codebase`, `native-*`, `third-party-*`. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman kapan saja. **Pengecualian: `target-codebase` ini SENDIRI**, karena Git eksekusi = Ya (Mode Git) — di situ `fetch`/`checkout`/`commit` boleh, TIDAK PERNAH `push`/merge/force-push/reset --hard.
>
> **Catatan penting soal credential (insiden 2026-08-24):** jangan pernah menjalankan command yang menyertakan token/secret mentah (mis. URL remote berisi `https://user:TOKEN@...`) — classifier permission akan menolaknya, dan itu memang perlindungan yang benar, jangan dicoba di-workaround. Kalau perlu operasi git ke remote, pastikan `origin` sudah pakai URL bersih (tanpa credential tertanam) + credential helper (`git config --global credential.helper manager`) sudah aktif di sisi dev — sudah dikonfirmasi aktif di repo ini per 2026-08-24.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, dst) — beri langkah bernomor konkret SAAT ITU JUGA**, bukan cuma "sudah disiapkan, tinggal kamu jalankan".

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 17.0 yang berjalan (`source-codebase`, branch `backfill/17.0`) — atau `01b_BASELINE_SPEC.md` sebagai dokumentasinya — adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 18.0 **harus identik** dengan 17.0, **termasuk bug yang sudah ada di sana** (F-01 s/d F-08 di `doc-dev/backfill/FINDINGS.md` source — jangan diperbaiki, dipertahankan, kecuali user eksplisit memutuskan sebaliknya di `FINDINGS.md` migrasi ini).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 17.0 (termasuk F-01..F-08 — itu keputusan pemilik modul, bukan efek samping migrasi)
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 18.0)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user:**
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

1. `01_intake/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/17-to-18.md` — constraint teknis umum
3. `01_intake/01b_BASELINE_SPEC.md` — apa yang modul lakukan
4. `FINDINGS.md` (root `doc/`, kalau sudah ada) — daftar gap/bug/ambiguitas yang masih terbuka
5. `03_spec/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
6. Step/fase yang sedang berjalan + `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

**Catatan khusus modul ini:** `migration-tool/knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` WAJIB juga dibaca sebelum Step 2/6 — modul ini men-patch `PurchaseOrderLineProductField` dari `purchase_product_matrix`.

---

## Alur kerja — 11 step

| # | Step | Output di `doc/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01_intake/01a_MIGRATION_INTAKE.md` + `01_intake/01b_BASELINE_SPEC.md` | Ya |
| 2 | Diff & compatibility analysis | `02_diff/02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_spec/03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_completeness/04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** |
| 5 | Acceptance criteria & test plan | `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` + `05b_TEST_PLAN_MIGRATION.md` | Tidak |
| 6 | Code migration | kode di `target-codebase` + `06_implementation/06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase) |
| 7 | Data migration scripts | N/A — port kode saja | — |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** |

Cross-cutting: `PROMPT_LOG.md`, `FINDINGS.md` di root `doc/`.

**Aturan paling penting:** `03_MIGRATION_SPEC.md` memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** — BUKAN migration spec.

---

## Status saat ini

**Step 1-9 selesai. Step 6 (kode) + Step 9 (test) sudah dieksekusi nyata via Docker (Mode C): G1 install PASS, Tour 15/15 PASS, 13/13 test PASS. Lanjut ke Step 10 (QA Testing, browser interaktif).**

> AI: update bagian ini sendiri di akhir tiap sesi kerja.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✔️ Disetujui (commit `9292ba5`) | ✔️ Lulus 2026-08-24 |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ✅ Selesai | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ✅ Selesai | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ✔️ Lulus | ✔️ Lulus 2026-08-24 |
| 5 | Acceptance Criteria & Test Plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05b_TEST_PLAN_MIGRATION.md` | ✅ Selesai | — |
| 6 | Code Migration | kode `target-codebase` + `06c_IMPLEMENTATION_LOG.md` | ✅ Selesai, G1 PASS | — |
| 7 | Data Migration Scripts | — (n/a, port kode saja) | — | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ✔️ Lulus | ✔️ Lulus 2026-08-24 |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ✔️ Lulus (13/13 test, Tour 15/15) | ✔️ Lulus 2026-08-24 |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | 🔄 Sedang dikerjakan | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang di-connect

| Folder | Path | Peran |
|---|---|---|
| `target-codebase` (folder UTAMA) | `D:\Kuncoro\doodex\repo\purchase-product-optional-migration-18` (branch `migration/18.0`) | CLAUDE.md + doc/ + kode hasil migrasi |
| `source-codebase` | `D:\Kuncoro\doodex\repo\purchase-product-optional-migration-18-source` (branch `backfill/17.0`, read-only) | Kode 17.0 asal + `doc-dev/backfill/` (functional spec + FINDINGS F-01..F-08, sudah diverifikasi eksekusi nyata) |
| `migration-tool` | `D:\Kuncoro\doodex\repo\migration-tool-project\migration-tool` | Template + knowledge base |
| `native-target` (Community 18.0) | `D:\Kuncoro\doodex\repo\odoo18` | Diff API core |
| `native-target-enterprise` (Enterprise 18.0) | `D:\Kuncoro\doodex\repo\enterprise18` | Cross-check dependency Enterprise |
| `native-source` (Community 17.0) | `D:\Kuncoro\doodex\repo\odoo17` | Cross-check API asal |
| `native-source-enterprise` (Enterprise 17.0) | `D:\Kuncoro\doodex\repo\enterprise17` | Cross-check — **catatan:** `sale_product_configurator` TERNYATA ada di `odoo17/addons/` (Community), BUKAN di sini (lihat `01a_MIGRATION_INTAKE.md` §2) |
| `third-party-*` | — | Tidak relevan — `purchase_product_matrix` & `sale_product_configurator` keduanya native Community, bukan OCA |

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
