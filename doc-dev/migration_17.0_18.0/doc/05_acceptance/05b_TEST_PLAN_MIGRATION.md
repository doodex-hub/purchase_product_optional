# Test Plan (Migrasi) — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Eksekusi: Mode C (AI jalankan langsung, Docker tersedia di environment Claude Code CLI ini) —
> `odoo-bin -i purchase_product_optional --test-enable --test-tags /purchase_product_optional --stop-after-init`.

Source module punya `tests/test_purchase_product_optional.py` (unit/integration, sudah execution-verified
di backfill 17.0 termasuk test MRO F-02) dan `tests/test_purchase_product_optional_tour.py` +
`static/tests/tours/purchase_product_optional_tour.js` (Tour, sudah PASS PENUH 13/13 di 17.0 — resep
Google Chrome + `websocket-client` di `Dockerfile.template`).

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | Install bersih | — | Checkpoint G1 (Fase A) | — |
| AC-02-01, AC-02-02 | Dialog terbuka otomatis + RPC tidak crash | — | — | Ya (`purchase_product_optional_tour.js`, step buka dialog) |
| AC-03-01, AC-03-02 | Harga per-vendor + currency no-op | Ya (test currency/price di `test_purchase_product_optional.py`) | — | — |
| AC-04-01 | Edit baris terkonfigurasi | — | Perlu ditambah manual (tour existing fokus create, bukan edit) — cek Step 9 |
| AC-05-01, AC-05-02 | Variant dinamis + exclusions | — | — | Ya (bagian tour "Add optional products") |
| AC-06-01, AC-06-02 | Onchange partner (bug dipertahankan) | Ya (`TestOnchangePartnerCurrency` — MRO shadowing test dari backfill) | — | — |
| AC-07-01 | View list (bukan tree) | — | Implisit (G1 install test gagal kalau masih `<tree>`) | — |
| AC-08-01 | Compute attribute values | Ya (kalau ada di test file existing — audit isi method di Step 9, bukan cuma nama) | — | — |
| AC-09-01 | `product_add_mode` tidak terdaftar (bug dipertahankan) | Ya (cek warning registry di log install) | — | — |
| AC-10-01, AC-11-01 | Multi-company/label (bug dipertahankan) | Tidak ada test otomatis existing — verifikasi manual/baca kode cukup (risiko rendah, sudah dikonfirmasi tidak berubah) | — | — |

**Audit isi test wajib (lesson `totp_enhancement`):** sebelum lapor "N test tersedia", baca isi tiap method `test_*` di `tests/test_purchase_product_optional.py` — pastikan bukan stub/docstring kosong. Dilakukan di Step 9 sebagai bagian eksekusi nyata.

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01 s/d AC-11-01 | Business flow end-to-end (buka app Purchase → PO baru → vendor → produk → dialog → confirm → save) | — | **Ya** — Claude in Chrome/Browser tool ke instance Docker 18.0 yang hidup dari Step 9, mereplikasi alur Tour secara visual + screenshot bukti | Tidak perlu — Tour Odoo native (Step 9) sudah cover Owl/JS in-modul |

Scope QA testing ini SEMPIT mengikuti alur Tour yang sudah terbukti PASS di 17.0 (13 langkah) — bukan
eksplorasi bebas di luar acceptance criteria.

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Instalasi & kompatibilitas 18.0 | AC-01-01, AC-07-01 | Business user/dev owner konfirmasi modul ter-install & tampil normal di instance staging 18.0 |
| Dialog konfigurator (core feature) | AC-02-01, AC-02-02, AC-04-01, AC-05-01, AC-05-02 | Business user coba alur nyata: buat PO, konfigurasi produk, edit ulang |
| Harga & currency | AC-03-01, AC-03-02 | Business user konfirmasi harga per-vendor tampil benar (currency no-op tetap sesuai ekspektasi lama) |
| Bug/quirk dipertahankan (F-01..F-08) | AC-03-02, AC-06-01, AC-09-01, AC-10-01, AC-11-01 | Business user/dev owner sign-off eksplisit bahwa bug ini SENGAJA dipertahankan (bukan terlewat) |

**Tool cuma generate skrip `11_UAT_CHECKLIST.md`** — eksekusi & sign-off selalu manual, business user asli.

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | AI (Mode C, Docker CLI) | Unit/Integration/Tour | Otomatis, dijalankan nyata | 11 AC (AC-01..AC-11) |
| 10 | AI-interaktif (Browser tool) + dev pendamping | Business flow E2E | Terhadap instance Docker hidup dari Step 9 | 11 AC |
| 11 | Business user/dev owner | UAT | Manual, selalu | 11 AC dikelompokkan 4 kategori |
