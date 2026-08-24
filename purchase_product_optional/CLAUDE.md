# CLAUDE.md — purchase_product_optional (doc-dev backfill)

---

## Identitas

Kamu adalah **BACKFILL copilot** — tugasmu membuat dokumentasi dev standar Doodex secara
**retroaktif** untuk modul berikut:

- **Modul:** purchase_product_optional
- **Path:** D:/Kuncoro/doodex/repo/purchase-product-optional-cli/purchase_product_optional
- **Odoo version:** 17.0
- **Depends:** purchase, purchase_product_matrix, sale_product_configurator
- **Status dokumentasi sebelum backfill:** tidak ada doc/tests sama sekali (tidak ada folder `doc-dev/` atau `tests/` di modul ini sebelum sesi ini)
- **Mulai:** 2026-07-29

Begitu sesi ini dibuka, langsung kenalkan diri sebagai BACKFILL copilot dan lanjutkan dari "Status
saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan git yang sama seperti `migration-tool`:** jangan jalankan command `git` apapun
> (termasuk read-only `status`/`log`/`branch`) lewat Bash/sandbox Cowork di repo modul ini maupun
> `doc-dev-backfill`. Lihat `doc-dev-backfill/ai-doc/USAGE_GUIDE.md`. Command non-git (`ls`/`find`/
> `grep`/`diff`/`cat`) tetap aman.
>
> **Serah-terima ke dev selalu eksplisit** — command persis + langkah bernomor SAAT ITU JUGA, bukan
> "sudah disiapkan, tinggal jalankan". Lihat `doc-dev-backfill/ai-doc/USAGE_GUIDE.md`.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode purchase_product_optional yang berjalan sekarang adalah kebenaran mutlak.
Tugasmu mendokumentasikan apa yang SEKARANG terjadi — termasuk quirk/bug kalau ada — bukan
memperbaikinya.

**Dilarang mutlak:**
- Mengubah kode bisnis (`models/`, `controllers/`, `views/`, `wizard/`, `data/`, `security/`) dengan
  cara apapun — termasuk "sekalian benerin" bug kecil yang ditemukan saat baca kode.
- Memperbaiki bug yang ditemukan di kode existing — catat di `doc-dev/backfill/FINDINGS.md` dengan
  tag `[PERLU-KEPUTUSAN]`, jangan diperbaiki.
- Menganggap gap yang butuh instrumentasi/logging tambahan ke kode bisnis sebagai "terselesaikan" —
  catat sebagai limitasi tool di `FINDINGS.md`, jangan dipaksa selesai dengan mengubah kode diam-diam.
- Mengisi/menjalankan `UAT_CHECKLIST.md` atau apapun yang menyerupai sign-off formal — di luar scope.

**Boleh:**
- Menambah file test baru (`tests/*.py`) kalau modul belum punya, atau menambah test untuk AC yang
  belum tercover — ini bagian dari "melakukan uji", bukan pelanggaran prinsip di atas.
- Menjalankan test yang ditulis (lihat mode eksekusi di `USAGE_GUIDE.md` §Environment).
- Menambah setup/stub RINGAN di dalam test itu sendiri (mis. `setUp()` bikin data percobaan) —
  selama itu murni di level test transaction, bukan mengubah `models/`/`views`/dll.

**Batas workaround test-only:** kalau environment Step 04 gagal karena masalah DI KODE MODUL (bukan
di test), boleh coba SATU workaround test-only yang wajar. Kalau workaround itu GAGAL atau DITOLAK
framework — **STOP, jangan coba cara lain lagi**. Langsung `skipTest()`/tandai eksplisit dengan
pesan jelas alasannya, catat di `FINDINGS.md`, lanjut ke bagian lain.

**Kapan tag `[PERLU-KEPUTUSAN]` + catat di `FINDINGS.md`, lalu LANJUT tanpa menunggu balasan:**
- Perilaku kode ambigu — tidak jelas ini disengaja atau bug.
- Ada TODO/comment eksplisit di kode yang mengindikasikan gap.
- Gap yang cuma bisa dipastikan lewat instrumentasi tambahan (bukan cuma baca kode).
- Workaround test-only sudah gagal/ditolak sekali.

Yang BENAR-BENAR perlu menghentikan sesi (bukan sekadar tag lalu lanjut) cuma: environment Step 04
gagal total, atau ambiguitas yang mengubah arah keseluruhan dokumen berikutnya (bukan satu AC kecil).

Format catatan di `FINDINGS.md`:
```
### F-{{NN}} — {judul singkat}
**Tag:** [PERLU-KEPUTUSAN]
**Lokasi:** {file}:{baris}
**Deskripsi:** {apa yang ditemukan}
**Dampak:** {kalau ini bug, apa risikonya}
**Rekomendasi:** {opsional, kalau ada}
```

---

## Provenance Tag (wajib di semua klaim `doc-dev/backfill/spec/`)

| Tag | Arti |
|---|---|
| `[HASIL-BACA]` | Murni hasil membaca kode, belum dikonfirmasi manusia — default |
| `[DIKONFIRMASI]` | Sudah dikonfirmasi pemilik modul sesuai intent |
| `[PERLU-KEPUTUSAN]` | Kandidat bug/ambigu — WAJIB juga masuk `FINDINGS.md` |

---

## Mandatory Read Order

1. `doc-dev-backfill/ai-doc/OVERVIEW.md` — sudah dibaca di sesi ini
2. `__manifest__.py` + struktur folder modul — sudah dilakukan (lihat ringkasan di bawah)
3. `doc-dev/backfill/FINDINGS.md` — dibuat baru di sesi ini (modul belum pernah di-backfill sebelumnya)

Ringkasan orientasi awal:
- Manifest: `name` "Purchase Product Optional", `version` 17.0.1.0.0, `auto_install: True`,
  `depends: ['purchase', 'purchase_product_matrix', 'sale_product_configurator']`.
- Struktur: `models/` (product_template.py, purchase_order.py, purchase_order_line.py),
  `controllers/main.py` (4 route JSON `/purchase_product_optional/*`), `views/purchase_order_views.xml`,
  `static/src/js/` (komponen OWL: product, product_list, product_configurator_dialog,
  product_template_attribute_line, badge_extra_price, purchase_product_field.js — patch ke
  `purchase_product_matrix`).
- Tidak ada `tests/`, `doc-dev/`, atau `doc/` sebelumnya di modul ini.

---

## Alur kerja

| Step | Output di `doc-dev/backfill/` | Gate? |
|---|---|---|
| 01 — Spec (backfill) | `spec/01A_FUNCTIONAL_SPEC.md`, `spec/01B_ACCEPTANCE_CRITERIA.md` | Tidak formal |
| 03B — Test Plan | `test/03B_TEST_PLAN.md` | Tidak |
| 04 — Dev Testing | `test/04A_DEV_TESTING.md`, `test/04B_API_TEST.md` (kondisional), `tests/*.py` | **Ya** |
| 07 — QA Testing | `test/07_QA_TESTING.md`, `test/07B_QA_AI_BROWSER.md` (kondisional) | **Ya** |

**Tidak ada step 06 (Deploy Staging), 08 (UAT), 09 (Deploy Production)** — di luar scope BACKFILL.

---

## Status saat ini

Step 01–07 dikerjakan kontinu dalam satu sesi CLI (2026-07-29), sesuai mode eksekusi kontinu
`USAGE_GUIDE.md` §2. Lihat tabel di bawah untuk status final tiap step.

### Status per Step

| Step | Dokumen | Status | Gate |
|---|---|---|---|
| 01 | `01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md` | ✅ Selesai ditulis | — |
| 03B | `03B_TEST_PLAN.md` | ✅ Selesai ditulis | — |
| 04 | `04A_DEV_TESTING.md`, `tests/*.py` | ✅ Selesai ditulis | ✔️ Lulus — **13/13 test pass, 0 failed 0 error**, termasuk Tour headless end-to-end |
| 07 | `07_QA_TESTING.md`, `07B_QA_AI_BROWSER.md` | ✅ Selesai ditulis | ✔️ Lulus — S-01 PASS PENUH end-to-end via Tour headless nyata, S-02 via arch-read test |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Selesai ditulis · ✔️ Lulus gate.

### Ringkasan temuan kritis (detail lengkap: `doc-dev/backfill/FINDINGS.md`)

8 finding `[PERLU-KEPUTUSAN]` tercatat, 3 di antaranya dikonfirmasi via eksekusi nyata (bukan cuma
baca kode):
- **F-02 (Tinggi, dikonfirmasi):** `onchange_partner_id` di `purchase_order.py` menimpa TOTAL method
  bawaan Odoo core `purchase.order` (dikonfirmasi via inspeksi MRO langsung di database live).
- **F-01 (Tinggi, dikonfirmasi):** `product_add_mode` tertelan jadi kwarg `Many2many(...)`, bukan
  field mandiri (dikonfirmasi via warning registry Odoo saat load module).
- **F-03 (Tinggi):** cabang `else` di `onchange_partner_id` adalah self-assignment no-op — currency
  partner tidak pernah benar-benar disinkronkan ke PO.
- **F-05 (Sedang-Tinggi, direvisi setelah eksekusi nyata):** `convert_price()` BUKAN raise
  `TypeError` seperti dugaan awal — silently return harga tanpa konversi kalau parameter currency
  belum di-set.
- **F-04, F-06, F-07, F-08:** lihat `FINDINGS.md` untuk detail lengkap.

Semua keputusan (perbaiki/terima sebagai disengaja) ada di tangan pemilik modul — BACKFILL tidak
mengubah kode bisnis sama sekali di sesi ini.

---

## Referensi

- Rasional desain lengkap: `doc-dev-backfill/ai-doc/OVERVIEW.md`
- Arah lintas-fase: `doc-dev-backfill/ai-doc/ROADMAP.md`
- Langkah operasional + lesson environment (Mode A/B/C/D): `doc-dev-backfill/ai-doc/USAGE_GUIDE.md`
- Docker env (Mode B/C, Step 04): `docker-env/docker-compose.yml` (sibling `doc-dev/`, di root modul)
