# Cross-Version Compare — purchase_product_optional (19.0 vs 20.0)

**Titik panggil:** A (in-flow, Step 10) — kriteria terpenuhi: instance produksi bisa Enterprise (MF-05)
+ area risiko tinggi (rewrite Owl 3, DIFF-01..06).
**Tanggal:** 2026-09-24
**Findings:** `FINDINGS.md` prefix `RMV-NN`.

## 1. Environment

| Versi | URL | Kode | Core | Compose |
|---|---|---|---|---|
| 19.0 | `http://localhost:8202` | worktree `../purchase-product-optional-migration-20-wt19` (`migration/19.0` @ `4736c36`, read-only mount) | image `purchase_product_optional_18_19_target-odoo` (odoo:19.0) + `enterprise19` | scratch compose project `ppo_cvc_19` (tidak di repo) |
| 20.0 | `http://127.0.0.1:8201` | `migration/20.0` (working tree) | Odoo 20 from source (`odoo20`) + `enterprise20` | `docker-env/docker-compose.yml`, `docker compose run --service-ports --name ppo20_qa` |

Kedua DB: install bersih, tanpa demo, modul + `account_budget_purchase` + `purchase_quality_control`,
seed identik lewat `odoo shell` (id record sama di kedua DB). Host berbeda (`localhost` vs `127.0.0.1`)
supaya cookie sesi tidak saling menimpa. Kedua stack dimatikan (`down -v`) setelah sesi.

## 2. Scope

Satu addon; alur: dialog configurator (buka, harga vendor, eksklusi, 5 tipe atribut, custom value,
optional add/remove, qty), jalur template configurable (dua dialog, CAND-08), edit ulang (T-03), Cancel.

## 3. Static-diff (kandidat)

Dari Step 2 (DIFF-01..19): semua area JS/template yang di-port Owl 3, xpath `<column>`, controller
exclusions, config param. Kandidat tambahan yang TIDAK tertangkap Step 2/8: aset ikon (Font Awesome) —
ketemu di visual pass.

## 4. Live-test & visual pass

Lihat `10_qa/10_BUSINESS_FLOW_MIGRATION.md` S-01..S-09 (skrip Playwright identik 19/20). Visual pass:
screenshot sejajar `10_qa/screenshots/{19,20}/`.

## 5. Klasifikasi

| ID | Klasifikasi | Ringkas | Tindak lanjut |
|---|---|---|---|
| RMV-01 | NATIVE-DIFF | 2× `console.error` "Component is destroyed" di jalur template configurable (20 me-reject RPC dari instance dialog yang di-destroy; 19 menggantungkannya diam-diam). Dialog di-setup 2×/destroy 1× di KEDUA versi | Dicatat |
| RMV-02 | REGRESI | Ikon `fa fa-minus`/`fa fa-plus` tidak ter-render di 20 (backend 20 tanpa CSS Font Awesome) — tombol qty kosong, "+ Add" tanpa ikon | **Difix** (`oi` + `data-icon`), diverifikasi live + asersi Tour |
| RMV-03 | GAP-LAMA | Template configurable: grid Confirm lalu Cancel configurator → Save "Oops!" (`virtual_NN`) — identik 19/20 (CAND-08/F-06) | Dicatat (dipertahankan) |
| RMV-04 | NATIVE-DIFF | Label varian "(Red)" tidak lagi tampil di sel produk baris PO; `purchase.order.line.name` tanpa nama produk; judul dialog grid = nama produk; gaya tombol secondary | Dicatat |
| RMV-05 | GAP-LAMA | Harga optional template multi-varian $0.00 (`standard_price` template = 0); nilai `no_variant` tidak tersimpan di baris (0 record) — identik 19/20 | Dicatat |

## 6. Laporan penutup

1 REGRESI (difix), 2 NATIVE-DIFF, 2 GAP-LAMA, 0 PERLU-DEV. Gap tetap terbuka: tidak ada. Rekomendasi
human QA sebelum go-live: `10_qa/human_qa/01_SMOKE.md` + `02_MAIN_FLOW.md` di staging Enterprise.

## Kontribusi ke Knowledge Base

- [x] Ada — CAND-07 (Font Awesome tidak di-style di backend 20), CAND-08 (`useService` reject RPC komponen
  destroyed), CAND-09 (tour: `web_enterprise` home menu → pakai `stepUtils.showAppsMenuItem()`), CAND-10
  (`purchase.order.line.name`/`label` split) di `migration-records/purchase_product_optional_19.0_20.0/SUMMARY.md`.
