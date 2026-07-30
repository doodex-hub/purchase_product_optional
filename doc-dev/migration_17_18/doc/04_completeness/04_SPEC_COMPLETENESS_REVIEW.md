# Spec Completeness Review — purchase_product_optional

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `source-codebase` (`purchase_product_optional/purchase_product_optional/`)
**Tanggal:** 2026-07-29

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8). Enumerasi di bawah diambil dari `find` penuh atas
> `source-codebase` (`purchase_product_optional/purchase_product_optional/`, addon root), bukan
> dari ingatan/asumsi struktur modul lain.

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | Ya — §2 baris 1 | ✅ Covered | DIFF-02 (hapus `sale_product_configurator`), bump version |
| `__init__.py` (root) | Ya — §2 (ditambahkan saat review ini) | ✅ Covered | Port 1:1, cuma import |
| `models/__init__.py` | Ya — §2 (ditambahkan saat review ini) | ✅ Covered | Port 1:1, cuma import |
| `models/product_template.py` (`convert_price`) | Ya — §2 baris `convert_price` | ✅ Covered | DIFF-01, BSL-016..018 |
| `models/purchase_order.py` | Ya — §2 baris "port 1:1" | ✅ Covered | BSL-010..012 |
| `models/purchase_order_line.py` | Ya — §2 baris "port 1:1" | ✅ Covered | BSL-008, 021, 022; field `product_add_mode` rusak (F-01) TIDAK diperbaiki |
| `controllers/__init__.py` | Ya — §2 (ditambahkan saat review ini) | ✅ Covered | Port 1:1, cuma import |
| `controllers/main.py` (4 route) | Ya — §2b "Controller & Route" | ✅ Covered | Method pindah ke `product` — wajib verifikasi G1/G2 |
| `views/purchase_order_views.xml` | Ya — §2 baris view + §2b "View List Checklist" | ✅ Covered | DIFF-06, 3 titik `<tree>`→`<list>` |
| `security/` | — | N/A | Modul tidak punya folder `security/` — tidak mendefinisikan model baru, tidak butuh access rule sendiri |
| `data/` | — | N/A | Modul tidak punya folder `data/` |
| `report/` | — | N/A | Modul tidak punya folder `report/` |
| `wizard/` | — | N/A | Modul tidak punya folder `wizard/` |
| `static/src/js/purchase_product_field.js` | Ya — §2 (3 baris: rename method, `_openGridConfigurator`, `result.purchase_warning`/`result.mode`) | ✅ Covered | DIFF-04, DIFF-05, DIFF-03, DIFF-07 |
| `static/src/js/product/` (`product.js`, `.xml`, `.scss`) | Ya — §2b "OWL Widget" tabel (baris `Product`) | ✅ Covered | Risiko rendah |
| `static/src/js/product_list/` (`.js`, `.xml`) | Ya — §2b "OWL Widget" tabel (baris `ProductList`) | ✅ Covered | Risiko rendah |
| `static/src/js/product_template_attribute_line/` (`.js`, `.xml`, `.scss`) | Ya — §2b "OWL Widget" tabel (baris `ProductTemplateAttributeLine`) | ✅ Covered | Risiko rendah |
| `static/src/js/badge_extra_price/` (`.js`, `.xml`) | Ya — §2b "OWL Widget" tabel (baris `BadgeExtraPrice`) | ✅ Covered | Risiko rendah |
| `static/src/js/product_configurator_dialog/` (`.js`, `.xml`) | Ya — §2b "OWL Widget" tabel (baris `ProductConfiguratorDialogPurchase`) | ✅ Covered | Risiko rendah-sedang, catatan `Dialog size` |
| `static/tests/product_configurator_dialog_tests.js` | Ya — §2 baris "static/tests/*.js" | ✅ Covered | Port 1:1 |
| `static/tests/purchase_product_field_tests.js` | Ya — §2 baris "static/tests/*.js" | ✅ Covered | Port 1:1 |
| `static/tests/tours/purchase_product_optional_tour.js` | Ya — §2 baris "static/tests/tours/*.js" | ✅ Covered | Port 1:1 |
| `tests/*.py` (5 file: `test_controllers.py`, `test_purchase_order_currency.py`, `test_purchase_order_line_fields.py`, `test_qunit.py`, `test_tours.py`) | **Awalnya TIDAK** — ditemukan gap saat review ini, sudah ditambahkan ke `03_MIGRATION_SPEC.md` §2 sebelum gate ini ditutup | ✅ Covered (setelah perbaikan) | Wajib re-run di 18.0 (step 9) sebagai baseline regresi — lihat catatan di bawah |
| `i18n/*.po` (44 file) + `i18n/sale_product_configurator.pot` | **Awalnya TIDAK** — ditambahkan saat review ini | ✅ Covered (setelah perbaikan) | Port 1:1, risiko sangat rendah |
| `static/description/*` (banner, icon, img/, index.html) | **Awalnya TIDAK** — ditambahkan saat review ini | ✅ Covered (setelah perbaikan) | Port 1:1, kosmetik listing Apps Store |
| Root misc (`README.md`, `LISEZMOI.md`, `LICENSE`, `googleaeed8a7b9ec156e7.html`) | **Awalnya TIDAK** — ditambahkan saat review ini | ✅ Covered (setelah perbaikan) | Port 1:1, tidak ada isi teknis |

---

## Gap yang Ditemukan & Diperbaiki Saat Review Ini

Review ini menemukan 4 kategori elemen source module yang **belum** punya baris eksplisit di
`03_MIGRATION_SPEC.md` §2 (tests Python, i18n, static/description, root misc). Semua sudah
ditambahkan ke spec (lihat baris "ditambahkan saat review ini" di tabel atas) sebelum gate ini
ditutup — bukan Ditolak, karena:

- Ke-4 kategori itu **tidak mengandung risiko migrasi baru** yang belum diketahui (tidak ada
  business logic, tidak dependency ke native/Enterprise yang berubah) — beda dengan gap
  `sale_product_configurator`/method-rename yang ditemukan step 2 (itu genuinely butuh riset baru).
- Satu-satunya kategori yang punya konsekuensi nyata di step selanjutnya adalah `tests/*.py` — sudah
  ditandai eksplisit di spec sebagai "wajib re-run di step 9", bukan sekadar "port lalu lupakan".

**Kesimpulan:** gap ini murni soal *cakupan dokumen* (elemen belum ditulis eksplisit), bukan soal
*strategi migrasi yang salah/kurang* — jadi diperbaiki langsung di tempat (tambah baris ke spec
step 3 yang sudah ada), bukan mengembalikan seluruh step 3 untuk ditulis ulang.

---

## Verdict

- [x] ✅ **Lulus** — semua elemen source module (enumerasi `find` penuh atas addon root) ter-cover
  di `03_MIGRATION_SPEC.md`, termasuk 4 kategori yang ditambahkan saat review ini. Lanjut ke step 5
  (Acceptance Criteria & Test Plan).
- [ ] ❌ Ditolak

**Catatan untuk step 5:** dasar acceptance criteria/test plan tetap `01b_BASELINE_SPEC.md` +
kode 17.0 yang berjalan (BUKAN `03_MIGRATION_SPEC.md`) — sesuai aturan di `CLAUDE.md` "Aturan
paling penting". `03_MIGRATION_SPEC.md` dipakai lagi nanti sebagai panduan implementasi di step 6.
