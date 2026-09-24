# Prompt Log — purchase_product_optional (19.0 → 20.0)

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` Fase 5 — prompt Normal vs Tool-fix
per step (template `migration-tool/templates/PROMPT_LOG.md`).

## Klasifikasi

Mengikuti template: **Normal** (menjalankan/mereview konten migrasi), **Tool-fix** (mengubah
`migration-tool` templates/ai-doc/SOP), **Tidak dihitung** (orientasi).

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap | — | — | Conditioning di sesi terpisah (2026-09-24) |
| 1 — Intake & Baseline Spec | 1 | 0 | Satu prompt kickoff ("migrasi 19→20 ... jalan terus sampai Step 9, STOP sebelum Step 10") menjalankan Step 1-9 |
| 2 — Diff & Compatibility Analysis | (idem) | 0 | |
| 3 — Migration Spec | (idem) | 0 | |
| 4 — Spec Completeness Review | (idem) | 0 | |
| 5 — Acceptance Criteria & Test Plan | (idem) | 0 | |
| 6 — Code Migration (A-G2) | (idem) | 0 | |
| 7 — Data Migration Scripts | — | — | N/A (port kode saja) |
| 8 — Code Review | (idem) | 0 | |
| 9 — Dev Testing | (idem) | 0 | |
| 10 — QA Testing | 1 | 0 | "lannjut step 10" — Cross-Version-Compare 19 vs 20 + Enterprise, 1 regresi (ikon) difix |
| 11 — UAT Sign-off | 1 | 0 | "lanjut step 11, sign-off percaya test ai" |
| **Total** | 6 | 0 | kickoff (Step 1-9) + 3 prompt status/keputusan (MF-01/03/05) + kickoff Step 10 + kickoff Step 11 |

## Catatan Definisi

Tidak ada revisi.
