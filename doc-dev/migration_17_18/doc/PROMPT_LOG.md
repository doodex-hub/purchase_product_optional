# Prompt Log — purchase_product_optional (17.0 → 18.0)

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` Fase 5 (Otomasi Bertahap).

---

## Klasifikasi

- **Normal** — prompt yang menjalankan/melanjutkan salah satu dari 11 step, atau review/verifikasi konten migrasi modul ini.
- **Tool-fix** — prompt yang hasilnya perubahan ke `migration-tool/templates/`, `migration-tool/ai-doc/`, atau proses SOP itu sendiri.
- **Tidak dihitung** — orientasi murni.
- Satu prompt user = satu unit hitung. Prompt yang menghasilkan KEDUA jenis dihitung sebagai Tool-fix.

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (sebelum step 1 resmi) | 1 | 0 | Satu prompt kickoff (2026-07-29) mencakup bootstrap penuh (baca `CLAUDE_TEMPLATE.md`, isi placeholder, tulis `CLAUDE.md` ke root target, buat struktur `doc-dev/migration_17_18/doc/`) SEKALIGUS instruksi mulai step 1 — dihitung sekali di sini, bukan dobel ke Step 1 |
| 1 — Intake & Baseline Spec | 0 | 0 | Draft `01a`/`01b` ditulis proaktif dalam prompt kickoff yang sama (lihat baris Bootstrap) — prompt review/konfirmasi user berikutnya baru dihitung di sini |
| 2 — Diff & Compatibility Analysis | | | |
| 3 — Migration Spec | | | |
| 4 — Spec Completeness Review | | | |
| 5 — Acceptance Criteria & Test Plan | | | |
| 6 — Code Migration (semua fase A-G2) | | | |
| 7 — Data Migration Scripts | — | — | N/A — sifat migrasi port kode saja |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 1 | 0 | |

## Catatan Definisi

- 2026-07-29: satu prompt kickoff user menghasilkan bootstrap PENUH + draft step 1 lengkap
  (`01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md`) sekaligus — ini karena baseline spec bisa
  disusun cepat dari `doc-dev/backfill/spec/` yang sudah ada (lihat catatan struktural di
  `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`), bukan indikasi step
  1 "biasanya" selesai dalam 1 prompt — catat ini kalau dipakai sebagai data pembanding lintas-project
  di `ROADMAP.md` §5, supaya tidak disalahartikan sebagai baseline normal tanpa spec lama.

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- Step dengan rasio Tool-fix tertinggi: *(isi di akhir)*
- Step yang paling "bersih": *(isi di akhir)*
- Salin ke `migration-tool/ai-doc/ROADMAP.md` §5 begitu project ini selesai.
