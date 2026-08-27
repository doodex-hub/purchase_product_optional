# Spec Completeness Review — purchase_product_optional

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `source-codebase/purchase_product_optional`
**Tanggal:** 2026-08-24

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | Ya — §2, §2b "Critical Migration Blockers" #1/#2, "Assets & Dependency" #1/#2 | ✅ Covered | Hapus `sale_product_configurator`, tambah `sale`, bump version |
| `models/purchase_order.py` | Ya — §2 "Tidak ada perubahan" | ✅ Covered | F-02/F-03 dipertahankan (keputusan dev) |
| `models/purchase_order_line.py` | Ya — §2 "Tidak ada perubahan" | ✅ Covered | F-01/F-06 dipertahankan |
| `models/product_template.py` | Ya — §2 "Tidak ada perubahan" | ✅ Covered | F-04/F-05 dipertahankan |
| `models/__init__.py` | Implisit (tidak ada import baru dibutuhkan, tidak ada model baru) | ✅ Covered | — |
| `controllers/main.py` | Ya — §2, §2b "Controller & Route" | ✅ Covered | Tidak ada perubahan, DIFF-04/DIFF-08 aman setelah fix manifest |
| `controllers/__init__.py` | Implisit | ✅ Covered | — |
| `views/purchase_order_views.xml` | Ya — §2, §2b "View List Checklist" (3 baris) | ✅ Covered | DIFF-01 |
| `security/` | Tidak ada folder ini di source module | ✅ N/A | Dikonfirmasi `find` langsung — modul tidak punya ACL/record rule custom (cuma `_inherit`, tidak ada model baru/TransientModel) |
| `data/` | Tidak ada folder ini di source module | ✅ N/A | Dikonfirmasi `find` langsung |
| `report/` | Tidak ada folder ini di source module | ✅ N/A | Dikonfirmasi `find` langsung |
| `wizard/` | Tidak ada folder ini di source module | ✅ N/A | Dikonfirmasi `find` langsung |
| `static/src/js/purchase_product_field.js` | Ya — §2 (DIFF-05, DIFF-06) | ✅ Covered | Rename + verifikasi arg |
| `static/src/js/product_configurator_dialog/product_configurator_dialog.js` | Ya — §2 (DIFF-07) | ✅ Covered | Hapus `useService("rpc")` |
| `static/src/js/product/product.js`, `product_list/product_list.js`, `product_template_attribute_line/*.js`, `badge_extra_price/badge_extra_price.js` | Ya — §2b "OWL Widget" tabel, baris terakhir | ✅ Covered | Port 1:1, sudah Owl 2 modern, tidak ada pola deprecated |
| `static/src/js/**/*.xml` (template Owl) | Ya — §2b "Urutan Prioritas Testing"/catatan Fase F | ✅ Covered | Tidak ada `t-att-on-click`/pola lama — kemungkinan N/A murni, dikonfirmasi ulang di Applicability Check step 6 |
| `static/src/**/*.scss` | Tidak eksplisit disebut — styling murni, tidak ada API yang berubah relevan | ✅ Covered (implisit "tidak ada perubahan") | Port 1:1 |
| `static/tests/tours/purchase_product_optional_tour.js` | Tidak eksplisit di §2, tapi relevan ke Step 9/10 (test, bukan kode produksi) | ✅ Covered (di luar scope §2, masuk scope Step 5/9) | Akan diverifikasi Step 9 (Dev Testing) |
| `static/description/**` (banner, icon, index.html) | Tidak relevan ke migrasi kode | ✅ N/A | Aset marketing/listing, port apa adanya |
| `tests/test_purchase_product_optional.py`, `test_purchase_product_optional_tour.py` | Tidak eksplisit di §2 — relevan Step 9 | ✅ Covered (scope Step 9) | — |
| `i18n/*.po` | Tidak eksplisit — tidak ada perubahan format PO antar versi yang relevan ke modul ini | ✅ Covered (implisit "tidak ada perubahan") | Port 1:1 |
| `LICENSE`, `README.md`, `LISEZMOI.md`, `googleaeed8a7b9ec156e7.html` | Non-kode | ✅ N/A | Port apa adanya, tidak relevan migrasi |
| `doc-dev/backfill/`, `docker-env/` (di source) | Bukan bagian addon Odoo — tooling/dokumentasi project BACKFILL sebelumnya | ✅ N/A — sengaja TIDAK diikutkan ke `target-codebase` | Scope boundary: `target-codebase` punya `doc-dev/migration_17.0_18.0/` sendiri; `docker-env/` untuk testing 18.0 dibuat baru di Step 6 (bukan copy dari source) |

## Verdict

- [x] ✅ **Lulus** — semua elemen source module (kode addon maupun non-kode) tercakup di `03_MIGRATION_SPEC.md`, baik sebagai "perlu diubah" (DIFF-01/02/03/05/07) maupun "tidak ada perubahan, port 1:1" secara eksplisit. Tidak ada gap. Lanjut ke Step 5 (Acceptance Criteria & Test Plan).
