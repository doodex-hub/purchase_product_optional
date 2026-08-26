# Spec Completeness Review — purchase_product_optional

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `source-codebase` (`purchase-product-optional-migration-19-source`, branch `migration/18.0`)
**Tanggal:** 2026-08-26

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8). Enumerasi semua elemen modul dari `source-codebase`, cocokkan
> satu-satu ke spec.

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | §2 baris 3 | ✅ Covered | Bump version `18.0.1.0.0`→`19.0.1.0.0` |
| `models/product_template.py` (`convert_price`) | §2b Kompatibilitas Data Model #1 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-04, `_convert()` stabil) |
| `models/purchase_order.py` (`id_vendor`, `onchange_id_vendor`, `onchange_partner_id`) | §2b Risiko Integrasi #1 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-05, override total tetap identik); BSL-005 dipertahankan sesuai keputusan dev |
| `models/purchase_order_line.py` (custom/no-variant attribute fields, `product_add_mode`) | §2b Kompatibilitas Data Model #1 | ✅ Covered | Tidak ada perubahan diperlukan |
| `models/__init__.py` | — | ✅ Covered (implisit) | File boilerplate import, tidak ada logic — tidak perlu baris spec tersendiri |
| `controllers/main.py` (4 route: `get_values_purchase`, `create_product`, `update_combination`, `get_optional_products`) | §2 baris 4, §2b Controller & Route | ✅ Covered | `type='json'`→`'jsonrpc'` cleanup opsional (DIFF-06); signature/logic route tidak berubah |
| `controllers/__init__.py` | — | ✅ Covered (implisit) | Boilerplate import |
| `views/purchase_order_views.xml` | §2b View List Checklist | ✅ Covered | N/A — tidak ada `<tree>`/`attrs=` tersisa, sudah tuntas di migrasi 17→18 |
| `static/src/js/purchase_product_field.js` | §2 baris 1-2, §2b OWL Widget baris 1 | ✅ Covered | Area rewrite utama — DIFF-01 (format many2one) + DIFF-02 (`useMatrixConfigurator`) |
| `static/src/js/product/product.js`, `.scss`, `.xml` | §2b OWL Widget baris 2 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-10) |
| `static/src/js/product_list/product_list.js`, `.xml` | §2b OWL Widget baris 2 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-10) |
| `static/src/js/product_template_attribute_line/*.js`, `.scss`, `.xml` | §2b OWL Widget baris 2 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-10) |
| `static/src/js/badge_extra_price/*.js`, `.xml` | §2b OWL Widget baris 2 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-10) |
| `static/src/js/product_configurator_dialog/*.js`, `.xml` | §2b OWL Widget baris 2 | ✅ Covered | Tidak ada perubahan diperlukan (DIFF-10) — komponen paling kompleks tapi tidak baca `record.data` Odoo langsung |
| `static/tests/tours/purchase_product_optional_tour.js` | — | ✅ Covered (ditambahkan sesi ini) | Dicek langsung (2026-08-26): sudah pakai syntax Tour modern (`run: "edit"`/`"click"`), TIDAK ada pola deprecated `run: "text ..."` (CAND-11, isu 17→18 yang sudah selesai). Tour berinteraksi via selector UI, bukan baca `record.data` langsung — tidak terpapar DIFF-01. Tidak ada gap. |
| `tests/test_purchase_product_optional.py` | — | ✅ Covered (ditambahkan sesi ini) | Dicek langsung: sudah pakai `TransactionCase`/`HttpCase` (bukan `SavepointCase` deprecated). 6 test class (`TestConvertPrice`, `TestOnchangePartnerCurrency`, `TestAttributeValueCompute`, `TestProductAddModeField`, `TestPurchaseOrderFormViewColumns`, `TestPurchaseProductOptionalController`) — semua menguji behavior yang sudah tercakup BSL-003/005/008/009/011/014 di baseline spec, tidak ada gap konseptual |
| `tests/test_purchase_product_optional_tour.py` | — | ✅ Covered (ditambahkan sesi ini) | `TestPurchaseProductOptionalTour(HttpCase)` — pemanggil Tour test di atas, tidak ada logic tambahan |
| `tests/__init__.py` | — | ✅ Covered (implisit) | Boilerplate import |
| `security/...` | — | N/A | Modul tidak punya folder `security/` — tidak ada access rights/record rules custom (dikonfirmasi `ls` module root, tidak ada file `ir.model.access.csv` custom) |
| `data/...` | — | N/A | Modul tidak punya folder `data/` |
| `report/...` | — | N/A | Modul tidak punya folder `report/` |
| `wizard/...` | — | N/A | Modul tidak punya wizard |
| `i18n/...` | — | N/A | Terjemahan — tidak perlu strategi migrasi kode, hanya perlu ikut ter-copy apa adanya (tidak ada breaking change format `.po`) |
| `docker-env/`, `LICENSE`, `README.md`, `LISEZMOI.md`, `googleaeed8a7b9ec156e7.html` | — | N/A | Bukan kode modul (infra testing lokal / dokumentasi / verifikasi domain Google Search Console) — tidak relevan strategi migrasi |

**Cek tambahan (bukan file, tapi elemen struktural):** `auto_install: True` — dikonfirmasi di
`03_MIGRATION_SPEC.md` §2 baris 3 (bagian dari bump manifest), kondisi auto-install (`purchase`+
`purchase_product_matrix`+`sale`) tidak berubah dari 18.0.

## Verdict

- [x] ✅ **Lulus** — semua elemen source module tercakup di `03_MIGRATION_SPEC.md` (langsung atau via
  keputusan eksplisit "tidak ada perubahan diperlukan"). 2 gap kecil ditemukan saat review ini (file
  test/Tour belum eksplisit disebut di step 3) — **sudah diverifikasi langsung di step 4 ini, bukan
  gap yang menghalangi gate** (keduanya bersih, tidak ada breaking pattern). Lanjut ke Step 5
  (Acceptance Criteria & Test Plan).
