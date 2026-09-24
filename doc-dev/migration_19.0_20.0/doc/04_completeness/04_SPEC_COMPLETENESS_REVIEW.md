# Spec Completeness Review — purchase_product_optional

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, kode `migration/19.0` (`git ls-files purchase_product_optional`)
**Tanggal:** 2026-09-24

> Enumerasi SEMUA file tracked modul di branch source, dicocokkan ke spec.

---

## Tabel Cakupan

| Elemen source | Di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | §2 baris manifest | ✅ Covered | Bump versi; `data`/`assets`/`depends`/`images` tetap |
| `__init__.py`, `models/__init__.py`, `controllers/__init__.py`, `tests/__init__.py` | Implisit (tidak berubah) | ✅ Covered | Tidak ada API yang dipakai |
| `models/purchase_order.py` | §2 (DIFF-10) | ✅ Covered | `set_param`→`set_int`; override total dipertahankan |
| `models/purchase_order_line.py` | §2b Data Model #1 (tidak berubah), DIFF-13/14 | ✅ Covered | Field/compute stabil; `product_add_mode` quirk tetap |
| `models/product_template.py` | §2 (DIFF-10) | ✅ Covered | `get_param`→`get_int` |
| `controllers/main.py` | §2 (DIFF-11, DIFF-12) | ✅ Covered | 3 titik `parent_combination`, `parent_exclusions={}` |
| `views/purchase_order_views.xml` | §2 (DIFF-17/18) | ✅ Covered | xpath `<column>` |
| `static/src/js/purchase_product_field.js` | §2 (DIFF-06/07) | ✅ Covered | import `orm_plugin` |
| `static/src/js/product_configurator_dialog/*.js/.xml` | §2 (DIFF-01..05, 03) | ✅ Covered | |
| `static/src/js/product_list/*.js/.xml` | §2 | ✅ Covered | |
| `static/src/js/product/*.js/.xml/.scss` | §2, DIFF-19 | ✅ Covered | scss tanpa perubahan |
| `static/src/js/product_template_attribute_line/*.js/.xml/.scss` | §2, DIFF-19 | ✅ Covered | scss tanpa perubahan |
| `static/src/js/badge_extra_price/*.js/.xml` | §2 | ✅ Covered | |
| `static/tests/tours/purchase_product_optional_tour.js` | §2 (DIFF-09) | ✅ Covered | test-only |
| `tests/test_purchase_product_optional.py` | §2 (DIFF-10) | ✅ Covered | test-only |
| `tests/test_purchase_product_optional_tour.py` | Implisit (`start_tour("/web", ...)` stabil) | ✅ Covered | |
| `i18n/*.po` (warisan `sale_product_configurator` 17.0) | Tidak disentuh | ✅ Covered (N/A) | Tidak ada perubahan format `.po` 20.0 yang relevan |
| `static/description/**`, `README.md`, `LISEZMOI.md`, `LICENSE`, `googleaeed8a7b9ec156e7.html` | Out of scope §4 (MF-01) | ✅ Covered (N/A) | Aset store/metadata |
| `docker-env/Dockerfile`, `docker-compose.yml` | Tidak di spec fungsional — infra test | ✅ Covered | Diganti ke build-from-source 20.0 di Step 6 (belum ada image resmi `odoo:20.0`) |
| `docker-env/logs/odoo.log` (tracked walau di-`.gitignore`) | — | ✅ N/A | Log lama, tidak disentuh |
| `security/`, `data/`, `report/`, `wizard/` | — | ✅ N/A | Tidak ada di modul |

## Cek `FINDINGS.md` (wajib gate)

| MF | Status | Menghalangi gate? |
|---|---|---|
| MF-01 | Default diambil (tidak port aset store) | Tidak — di luar kode fungsional |
| MF-02 | Dipertahankan | Tidak |
| MF-03 | Default diambil (satu-satunya opsi tanpa menambah fitur) | Tidak — konsekuensi platform, dikomunikasikan; keputusan dev dibutuhkan hanya jika ingin mengimplementasi ulang (di luar scope) |

## Verdict

- [x] ✅ Lulus — semua elemen Covered, lanjut ke Step 5.
