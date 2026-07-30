# Migration Spec (Teknis) — purchase_product_optional

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-07-29

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` (step 1). Lihat step 5.

---

## 1. Ringkasan Strategi

> **Revisi retroaktif (2026-07-29, setelah Checkpoint G2 & Step 8 Code Review):** draft asli
> dokumen ini ditulis SEBELUM G2 (validasi runtime browser) dijalankan. G2 menemukan 2 fix mekanis
> tambahan yang tidak teridentifikasi lewat static review (step 2/3) — **MF-13** (`useService("rpc")`
> dihapus total di 18.0, ganti fungsi `rpc()` dari `@web/core/network/rpc`) dan **MF-14**
> (`optional_product_ids`/`has_optional_products` hanya ada lewat modul `sale`, yang hilang transitif
> begitu `sale_product_configurator` dihapus dari `depends` sesuai DIFF-02 — eskalasi ke user, resolved
> dengan menambah `'sale'` eksplisit ke `depends`). Detail lengkap: `FINDINGS.md` MF-13/MF-14,
> `06_implementation/06c_IMPLEMENTATION_LOG.md` §[Fase G2]. Poin 1-4 di bawah TETAP seperti draft asli
> (ditulis dari step 2/3, sebelum G2) — dipertahankan apa adanya untuk jejak historis keputusan.

Sebagian besar modul **port langsung 1:1** (models, controllers, 4 komponen Owl sekunder, test suite)
— tidak ada breaking change yang ditemukan di area itu (dari static review step 2/3). **4 area butuh
perubahan mekanis wajib** (bukan business logic) supaya modul bisa install dan berfungsi identik di
18.0 (+ 2 area tambahan, MF-13/MF-14, baru ketahuan lewat G2 — lihat revisi di atas):

1. **Manifest** — hapus `sale_product_configurator` dari `depends` (DIFF-02, modul dihapus total di
   18.0). Install-breaking kalau tidak diperbaiki.
2. **View** — `<tree>` → `<list>` di `views/purchase_order_views.xml` (DIFF-06). Install-breaking.
3. **JS patch** — rename `_editProductConfiguration` → `onEditConfiguration` di
   `purchase_product_field.js` (DIFF-04). Bukan install-breaking, tapi regresi silent (BSL-009) kalau
   dibiarkan.
4. **JS patch** — verifikasi `_openGridConfigurator()` (dipanggil tanpa argumen, DIFF-05) tetap aman
   di base class 18.0 yang mensyaratkan parameter `edit`.

**2 area DIDOKUMENTASIKAN sebagai keterbatasan yang harus tetap identik (TIDAK diperbaiki/di-scope
ulang tanpa persetujuan eksplisit):** `result.purchase_warning` (DIFF-03) dan `result.mode`/
`product_add_mode` (DIFF-07) kemungkinan besar sudah tidak reachable di 18.0 karena mekanisme
sumbernya (Enterprise `sale_product_configurator` 17.0) sudah hilang total dari platform — ini BUKAN
sesuatu yang bisa "diperbaiki" lewat port kode (menambah override baru = fitur baru, di luar scope
port kode kecuali disetujui eksplisit terpisah).

---

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` | DIFF-02 | Hapus `sale_product_configurator` dari `depends`; bump `version` ke `18.0.1.0.0`. Cek `web.qunit_suite_tests`/`web.assets_tests` bundle key masih valid (belum ada indikasi berubah) | Rendah (mekanis), tapi WAJIB — install-breaking kalau terlewat | — |
| `views/purchase_order_views.xml` | DIFF-06 | `<tree>` → `<list>` di 3 titik (2× xpath target `//tree/field[...]`, 1× inner tree `product_custom_attribute_value_ids`). XML-ID (`purchase_order_view_form`) TIDAK diubah — cuma tag view | Rendah (mekanis), murni sintaks, tidak menyentuh field/atribut | — |
| `static/src/js/purchase_product_field.js` — override `_editProductConfiguration` | DIFF-04 | Rename method jadi `onEditConfiguration()`, isi/behavior method TIDAK diubah (cuma nama hook) | **Tinggi** — kalau lupa/salah rename, alur edit baris tersimpan (BSL-009) diam-diam salah pakai grid dialog | BSL-009 |
| `static/src/js/purchase_product_field.js` — pemanggilan `_openGridConfigurator()` | DIFF-05 | Port apa adanya dulu (tanpa argumen) — `undefined` tetap falsy, kemungkinan aman. **Verifikasi eksplisit di step 9**, baru tambah argumen `false` eksplisit kalau ternyata bermasalah | Sedang | AC-01-06 (via BSL-007) |
| `static/src/js/purchase_product_field.js` — baca `result.purchase_warning`/`result.mode` | DIFF-03, DIFF-07 | Port apa adanya (JANGAN dihapus/di-refactor "karena toh tidak reachable") — kode ini valid secara sintaks dan tidak error, cuma cabangnya kemungkinan tidak pernah tereksekusi. Dokumentasikan status ini di komentar/log internal migrasi, BUKAN di kode modul | Rendah (kode itu sendiri aman) — risiko ada di *ekspektasi* testing, bukan di kode | BSL-004, BSL-005, BSL-006, BSL-007 |
| `models/product_template.py` — `convert_price` | DIFF-01 | Port 1:1, tidak ada perubahan diperlukan — signature `_convert()` 18.0 dikonfirmasi kompatibel | Rendah | BSL-016, BSL-017, BSL-018 |
| `models/purchase_order.py`, `models/purchase_order_line.py` | — (tidak ada DIFF ditemukan) | Port 1:1, termasuk field `product_add_mode` yang rusak (F-01/MF-01/BSL-008) — TIDAK diperbaiki | Rendah (port murni), tapi lihat DIFF-07 untuk konteks kenapa field ini tetap tidak berfungsi meski di-port | BSL-008, BSL-010, BSL-011, BSL-012, BSL-021, BSL-022 |
| `controllers/main.py` (4 route) | — (tidak ada DIFF spesifik ditemukan, TAPI method yang dipanggil pindah modul) | Port 1:1. **WAJIB verifikasi di G1/G2**: `_get_first_possible_combination`, `_create_product_variant`, `_get_variant_for_combination`, `_get_attribute_exclusions` sekarang didefinisikan di `product` (bukan lagi `sale_product_configurator`) — signature terlihat kompatibel dari pembacaan kode `native-target`, tapi belum diverifikasi lewat instalasi nyata | **Sedang** — method pindah modul, signature perlu dikonfirmasi jalan nyata bukan cuma baca kode | BSL-013, BSL-014, BSL-015, BSL-019, BSL-023 |
| 5 komponen Owl (`Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`, `ProductConfiguratorDialogPurchase`) | — (tidak ada DIFF spesifik ditemukan — sudah Owl 2 modern) | Port 1:1. Cek visual/runtime di G2 (belum ada bukti breaking change spesifik, tapi Owl framework detail seperti `Dialog` props/`useRecordObserver` belum 100% diverifikasi byte-level) | Rendah-Sedang (lihat catatan Owl/JS di `migration-records/`) | Terkait BSL §6 |
| `static/tests/*.js`, `static/tests/tours/*.js` | — | Port 1:1 — test suite bawaan BACKFILL, tidak spesifik ke perubahan versi | Rendah | — |
| `tests/*.py` (5 file: `test_controllers.py`, `test_purchase_order_currency.py`, `test_purchase_order_line_fields.py`, `test_qunit.py`, `test_tours.py`) | — (tidak ada DIFF ditemukan) | Port 1:1 — suite ini adalah bukti eksekusi nyata BACKFILL (11/11 pass, run #7). WAJIB dijalankan ulang di environment 18.0 (Mode B) di step 9 sebagai baseline regresi, bukan diasumsikan otomatis pass karena sudah pernah pass di 17.0 | Rendah (port), tapi **wajib re-run** — hasil run jadi bukti utama step 9 | Seluruh BSL-NNN (test ini adalah realisasi baseline spec) |
| `__init__.py` (root, `models/`, `controllers/`) | — | Port 1:1 — murni import statement, tidak ada logic | Sangat rendah | — |
| `i18n/*.po` (44 file bahasa) | — | Port 1:1 — tidak ada perubahan format PO file antar versi Odoo yang ditemukan di `knowledge/version-diffs/17-to-18.md`. Catatan: `i18n/sale_product_configurator.pot` (nama file warisan, isinya string modul ini sendiri) tetap di-port apa adanya — cuma nama file, bukan dependency aktif | Sangat rendah | — |
| `static/description/*` (banner.png, icon.png, `img/*.png`, `index.html`) | — | Port 1:1 — asset listing Odoo Apps Store, tidak mempengaruhi runtime/business logic | Tidak ada (kosmetik) | — |
| Root misc: `README.md`, `LISEZMOI.md`, `LICENSE`, `googleaeed8a7b9ec156e7.html` | — | Port 1:1 apa adanya — tidak ada isi teknis untuk dimigrasikan (google-site-verification file khususnya murni artefak hosting, bukan bagian addon) | Tidak ada | — |

---

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi di 18.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | `depends` mencantumkan `sale_product_configurator` — modul tidak ada lagi di 18.0 | `__manifest__.py` | `02_DIFF_ANALYSIS.md` DIFF-02; kandidat `knowledge/version-diffs/17-to-18.md` (CAND-01 `migration-records/`) |
| 2 | `<tree>` dipakai di view (2× xpath, 1× inner) | `views/purchase_order_views.xml` | `knowledge/version-diffs/17-to-18.md` §1 (`<tree>`→`<list>`, sudah ada entry) |
| 3 | `version` manifest masih `17.0.1.0.0` | `__manifest__.py` | Konvensi standar migrasi Odoo |

**Priority:** HIGH — perbaiki ketiganya di Fase A1/A2 sebelum G1 (install test) pertama.

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `PurchaseOrderLineProductField` (patch) | `purchase_product_field.js` | **Tinggi** | Rename `_editProductConfiguration`→`onEditConfiguration` (DIFF-04, WAJIB); verifikasi `_openGridConfigurator()` tanpa argumen (DIFF-05); base class 18.0 berubah jadi extends `ProductLabelSectionAndNoteField` (dari `@account`) — trigger mechanism (`useRecordObserver` di `setup()`) beda dari asumsi lama, pastikan `super.setup(...)` di patch tetap benar memanggil rantai baru ini |
| `ProductConfiguratorDialogPurchase` | `product_configurator_dialog/product_configurator_dialog.js` | Rendah-Sedang | Sudah ES6/Owl 2 modern (`onWillStart`, `useState`, `useSubEnv`). Cek prop `Dialog size="size"` (`this.size` tidak pernah di-set di `setup()` — kemungkinan `undefined`, port apa adanya, ini existing behavior 17.0 juga, BUKAN sesuatu yang berubah karena migrasi) |
| `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice` | `product/`, `product_list/`, `product_template_attribute_line/`, `badge_extra_price/` | Rendah | Tidak ada pola classic (`Component.extend()`/`odoo.define`) ditemukan — port 1:1, verifikasi visual di G2 |

**Urutan wajib:** migrasi SEMUA JavaScript dulu (tetap pakai syntax Owl lama di template), baru
upgrade template ke syntax Owl baru terakhir. Lihat `06a_CODE_MIGRATION_PHASES.md` Fase E & F.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | 4 route (`get_values_purchase`, `create_product`, `update_combination`, `get_optional_products`) memanggil method `product.template` yang PINDAH dari `sale_product_configurator` ke `product` — signature terlihat sama dari baca kode `native-target`, tapi belum diverifikasi eksekusi nyata | `controllers/main.py` | **Sedang** — wajib jadi bagian smoke test G2 |
| 2 | `type='json', auth='user'` — tidak ada perubahan konvensi routing yang ditemukan di `knowledge/version-diffs/17-to-18.md` untuk pola ini | `controllers/main.py` | Rendah |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `depends: ['purchase', 'purchase_product_matrix', 'sale_product_configurator']` — item ke-3 wajib dihapus (DIFF-02) | `__manifest__.py` | **Kritis** |
| 2 | `assets.web.assets_backend` — key masih valid di 18.0 (tidak ada indikasi rename di `native-target`) | `__manifest__.py` | Rendah |
| 3 | `assets.web.qunit_suite_tests`/`web.assets_tests` (ditambahkan BACKFILL untuk test JS) — verifikasi masih dikenali 18.0 saat G1 | `__manifest__.py` | Rendah-Sedang |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Field `product_add_mode` tetap rusak (kurung tidak tertutup) — port apa adanya, TIDAK diperbaiki | `models/purchase_order_line.py:24-28` | Rendah (port), tapi WAJIB tidak disentuh | BSL-008 |
| 2 | `product_custom_attribute_value_ids`/`product_no_variant_attribute_value_ids` compute logic — tidak ada breaking change ORM ditemukan untuk pola `store=True, readonly=False, precompute=True` di 18.0 | `models/purchase_order_line.py` | Rendah | BSL-021, BSL-022 |
| 3 | `onchange_partner_id`/`onchange_id_vendor` — pola `@api.onchange` tidak berubah 17→18 (tidak ada di `knowledge/version-diffs/`) | `models/purchase_order.py`, `models/purchase_order_line.py` | Rendah | BSL-010, BSL-011, BSL-012 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `result.purchase_warning` kemungkinan tidak pernah terkirim (DIFF-03) — perlu skenario test eksplisit produk dengan `purchase_line_warn` diisi, untuk MEMBUKTIKAN (bukan cuma menduga) cabang ini unreachable di 18.0 | `purchase_product_field.js` | **Tinggi** — verifikasi step 9 |
| 2 | `result.mode`/`product_add_mode` kemungkinan tidak pernah terisi (DIFF-07) — sama, butuh skenario test eksplisit untuk konfirmasi | `purchase_product_field.js` | **Tinggi** — verifikasi step 9 |
| 3 | F-06 (dialog configurator vs grid tumpang tindih) — WAJIB direproduksi ulang identik di 18.0, bukan diasumsikan otomatis sama karena `purchase_product_matrix` (parent class) berubah struktur (DIFF-04) | `purchase_product_field.js` | **Tinggi** — prioritas step 9/10 |

### Urutan Prioritas Testing

1. Install & startup — manifest (hapus `sale_product_configurator`, bump version), dependency resolve bersih
2. `<tree>`→`<list>` — parsing view tidak error
3. Core user flow — pilih produk dengan optional products di baris PO → dialog Product Configurator terbuka (BSL-001..BSL-007)
4. Edit baris yang sudah terkonfigurasi → dialog terbuka kembali dengan data tersimpan (BSL-009, verifikasi DIFF-04 sudah diperbaiki)
5. Harga per-vendor (supplierinfo) + konversi currency (BSL-013..BSL-018)
6. F-06 — reproduksi ulang skenario dialog tumpang tindih, pastikan behavior identik (bukan tiba-tiba "terselesaikan" oleh perubahan `purchase_product_matrix`, atau sebaliknya jadi lebih parah)
7. DIFF-03/DIFF-07 — buktikan `purchase_warning`/`mode` memang unreachable (skenario eksplisit), bukan diasumsikan
8. Widget backend (Owl) — render visual 5 komponen
9. Optional products rekursif, dynamic variant creation (BSL-019, BSL-023)

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Inline tree di form (xpath target 1) | `views/purchase_order_views.xml`, xpath `//tree/field[@name='product_template_id']` (2 xpath terpisah pakai target ini) | `//tree/...` → `//list/...` |
| 2 | Inline tree di form (xpath target 2) | `views/purchase_order_views.xml`, xpath `//tree/field[@name='product_id']` | `//tree/...` → `//list/...` |
| 3 | Inner tree (sub-view) | `views/purchase_order_views.xml`, field `product_custom_attribute_value_ids` | `<tree>...</tree>` → `<list>...</list>` |

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| Fase A (manifest + view mekanis) | Kecil (< 1 jam) | 3 perubahan mekanis, jelas |
| Fase D1/D2 (controllers/assets) | Kecil | Port 1:1, verifikasi saat G1/G2 |
| Fase E (JavaScript) | Sedang | 1 rename wajib (DIFF-04) + verifikasi beberapa titik (DIFF-05, Dialog props), sisanya port 1:1 — lebih ringan dari dugaan awal karena sudah Owl 2 modern |
| Fase F (Template) | Kecil | Menyusul Fase E, tidak ada perubahan sintaks Owl besar yang teridentifikasi |
| Verifikasi G1/G2 & step 9/10 | Sedang-Besar | 3 risiko integrasi (DIFF-03/DIFF-07/F-06) butuh skenario test eksplisit, bukan cuma smoke check biasa |

---

## 3. Data Migration (ringkas)

Tidak relevan — sifat migrasi **port kode saja** (instalasi baru di 18.0, tanpa data produksi). Tidak
ada field yang berubah struktur yang butuh transformasi data lama. Step 7 tetap N/A (dikonfirmasi
`01a_MIGRATION_INTAKE.md` §3).

## 4. Scope

### Termasuk
- Fix mekanis wajib: manifest (`depends`, `version`), view (`<tree>`→`<list>`), rename
  `_editProductConfiguration`→`onEditConfiguration`.
- Verifikasi (bukan perubahan kode) untuk: `_openGridConfigurator()` tanpa argumen, method
  `product.template` yang pindah modul, `purchase_warning`/`mode` unreachability, F-06 reproduksi.
- Port 1:1 seluruh business logic, termasuk 6 bug/quirk warisan (F-01..F-06/MF-01..MF-06).

### Di Luar Scope (sengaja, disetujui di intake)
- Re-implementasi `purchase_warning` (butuh override baru `get_single_product_variant` di modul ini
  — fitur baru, bukan port) — TIDAK dikerjakan kecuali user meminta eksplisit setelah verifikasi step
  9 membuktikan ini benar-benar hilang.
- Re-implementasi mekanisme `product_add_mode`/`result.mode` penuh (mengikuti pola
  `sale_product_matrix`) — sama, fitur baru di luar scope port kode.
- Memperbaiki F-01 (kurung `product_add_mode` tidak tertutup) — dilarang eksplisit oleh prinsip
  Source of Truth (`CLAUDE.md`), meski sekarang dipahami lebih jelas lewat DIFF-07.
