# Migration Spec (Teknis) — purchase_product_optional

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md`. Lihat step 5.

---

## 1. Ringkasan Strategi

Migrasi ini **kecil dari sisi jumlah file, tapi ada 1 titik risiko tinggi**: sebagian besar modul
(Python, view XML, 5 dari 6 komponen Owl) port langsung tanpa perubahan — sudah dikonfirmasi bersih
di step 2. Satu file, `static/src/js/purchase_product_field.js`, butuh **rewrite terarah** (bukan
rewrite total) mengikuti 2 breaking change API `purchase_product_matrix` (DIFF-01, DIFF-02): format
data many2one berubah tuple→objek, dan method `_openGridConfigurator` dihapus dari base class diganti
hook `useMatrixConfigurator()`. Ditambah bump versi manifest dan (opsional, non-breaking) cleanup
`type='json'`→`type='jsonrpc'` di controller.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `static/src/js/purchase_product_field.js` — akses `record.data.xxx[0]`/`[1]` (8 titik) | DIFF-01 | Ganti SEMUA akses tuple `[0]`/`[1]` jadi akses objek `.id`/`.display_name`, ikuti pola persis native 19.0 (`purchase_product_matrix/static/src/js/purchase_product_field.js`). Tulis field many2one jadi `{id, display_name}` (bukan `[id, name]`). | Tinggi — kalau ada 1 titik terlewat, silent-wrong-read (baca `undefined` dari objek pakai index numerik) alih-alih crash langsung, lebih sulit terdeteksi review statis. | BSL-001, BSL-014 |
| `static/src/js/purchase_product_field.js::_onProductTemplateUpdate` — pemanggilan `this._openGridConfigurator()` (fallback, baris ~92) | DIFF-02 | Ganti jadi `this.matrixConfigurator.open(this.props.record, false)`. Tambahkan `this.matrixConfigurator = useMatrixConfigurator()` di `patch(...).setup()` (setelah `super.setup(...)`, sebelum dipakai) — import `useMatrixConfigurator` dari `@product_matrix/js/matrix_configurator_hook`. | Tinggi — tanpa fix ini, jalur fallback throw `TypeError` runtime (walau jalur ini jarang tereksekusi produksi per CAND-07, tetap wajib diperbaiki, bukan didiamkan). | BSL-001 |
| `__manifest__.py::version` | — (Critical Migration Blocker standar semua modul, bukan DIFF spesifik) | Bump `'18.0.1.0.0'` → `'19.0.1.0.0'` | Rendah, wajib | — |
| `controllers/main.py` — 4× `@route(..., type='json', ...)` | DIFF-06 | **Opsional** — ganti `type='json'`→`type='jsonrpc'`. Aman diport apa adanya (alias deprecated, tidak breaking) — kalau waktu terbatas, boleh di-skip di migrasi ini dan dicatat sebagai technical debt, bukan blocker. | Rendah | — |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x` | `__manifest__.py:4` (`version: '18.0.1.0.0'`) | Konvensi standar semua migrasi migration-tool |

**Priority:** HIGH — perbaiki sebelum runtime testing apapun. **Tidak ada blocker instalasi lain** —
tidak ada `<tree>`, tidak ada `attrs=`/`states=`, dependency (`purchase`/`purchase_product_matrix`/`sale`)
semua masih ada di 19.0 (dikonfirmasi step 2 §1).

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `PurchaseOrderLineProductField` (patch) | `static/src/js/purchase_product_field.js` | **Tinggi** | DIFF-01 (format many2one) + DIFF-02 (`_openGridConfigurator` dihapus) — lihat §2 tabel di atas. Satu-satunya widget yang butuh perubahan kode. |
| `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`, `ProductConfiguratorDialogPurchase` | `static/src/js/{product,product_list,product_template_attribute_line,badge_extra_price,product_configurator_dialog}/*.js` | Rendah | Dikonfirmasi step 2 (DIFF-10) — komponen ini kelola state sendiri (props + hasil `orm.call`/`search_read`, bukan `record.data` Odoo langsung), tidak terpapar perubahan format many2one. **Tetap wajib diverifikasi ulang lewat eksekusi nyata (G2/Tour, step 6/9)**, bukan cuma grep statis — grep tidak menjamin 0% risiko runtime. |

**Urutan wajib:** migrasi SEMUA JavaScript dulu (tetap pakai syntax Owl lama di template), baru
upgrade template ke syntax Owl baru terakhir. Kebalikannya → error runtime template. **Catatan project
ini:** tidak ada perubahan template QWeb yang diketahui dari step 2 (semua breaking change yang
ditemukan murni di layer JS `purchase_product_field.js`, bukan `.xml` template) — Fase F (Template)
kemungkinan besar N/A/minimal untuk migrasi ini, akan dikonfirmasi ulang di step 6 Applicability Check.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `type='json'` deprecated alias untuk `type='jsonrpc'` (DIFF-06) | `controllers/main.py` (4 route) | Rendah — opsional, non-blocking |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada isu — `depends: purchase, purchase_product_matrix, sale` semua tersedia & tidak berubah struktur di 19.0 (dikonfirmasi step 2 §1) | `__manifest__.py` | — |
| 2 | `assets` (`web.assets_backend`, `web.assets_tests`) — key manifest tidak berubah antar versi, tidak perlu disentuh | `__manifest__.py` | — |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Tidak ada perubahan struktur data model yang mempengaruhi field custom modul ini (`product_custom_attribute_value_ids`, `product_no_variant_attribute_value_ids`, `id_vendor`) — dikonfirmasi step 2, tidak ada DIFF terkait field-field ini | `models/*.py` | — | BSL-002..009 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `onchange_partner_id` override total core — perilaku dikonfirmasi TIDAK berubah 18.0→19.0 (DIFF-05), tapi tetap risiko desain bawaan (BSL-005, dipertahankan sesuai keputusan dev) | `models/purchase_order.py` | Rendah untuk migrasi ini (tidak ada perubahan yang perlu dikerjakan), tapi tetap catatan risiko produksi jangka panjang di luar scope |
| 2 | CAND-08 (dua dialog terbuka bersamaan tanpa koordinasi, `_onProductTemplateUpdate` + `super()` tanpa syarat) — dipertahankan sesuai keputusan dev, TIDAK diperbaiki di migrasi ini | `static/src/js/purchase_product_field.js::onEditConfiguration`/`_onProductTemplateUpdate` | — (sengaja tidak dikerjakan) |

### Urutan Prioritas Testing

1. Install & startup — manifest version, dependency (`purchase`/`purchase_product_matrix`/`sale`)
2. Core user flow — buka form PO, pilih produk di baris → dialog Product Configurator/matrix "Choose Product Variants" terbuka sesuai `get_single_product_variant()` — ini yang paling terdampak DIFF-01/02
3. Persistensi data — baris PO tersimpan dengan `product_custom_attribute_value_ids`/`product_no_variant_attribute_value_ids` benar setelah dialog "Confirm"
4. Widget backend (Owl) — `purchase_product_field.js` (prioritas 1, area rewrite), lalu 5 komponen dialog lain (verifikasi regresi)
5. Currency conversion (BSL-003/013/018) — harga dialog terkonversi benar via `convert_price()`

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| — | Tidak ada `<tree>` tersisa di modul ini | `views/purchase_order_views.xml` | N/A — sudah selesai dimigrasi tuntas di 17→18 (dikonfirmasi step 2 §2b intake, grep bersih) |

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| `purchase_product_field.js` rewrite (DIFF-01/02) | Sedang | ~8 titik akses tuple + 1 penggantian method call + 1 import baru — mekanis tapi butuh ketelitian (silent-wrong-read kalau terlewat) |
| Manifest version bump | Trivial | 1 baris |
| `type='json'`→`type='jsonrpc'` cleanup | Trivial (opsional) | 4 baris, non-blocking |
| Testing (G1 install, G2 Tour, dev/QA testing) | Sedang-Tinggi | Perlu environment Docker Odoo 19.0 — belum diputuskan mode eksekusi (lihat checkpoint G1 di step 6) |

## 3. Data Migration (ringkas — detail di step 7)

**N/A — port kode saja** (dikonfirmasi `01a_MIGRATION_INTAKE.md` §3), tidak ada data produksi yang
perlu ditransformasi. Step 7 di-skip untuk migrasi ini.

## 4. Scope

### Termasuk
- Rewrite `static/src/js/purchase_product_field.js` mengikuti DIFF-01 (format many2one) dan DIFF-02 (`useMatrixConfigurator` hook)
- Bump `__manifest__.py` version ke `19.0.1.0.0`
- Verifikasi ulang (bukan perubahan kode) untuk 5 komponen Owl dialog lain, `models/*.py`, `views/*.xml`, `controllers/main.py`

### Di Luar Scope (sengaja, disetujui di intake)
- Perbaikan `onchange_partner_id` override total core (BSL-005) — dipertahankan apa adanya, dikonfirmasi dev
- Perbaikan pola dua dialog terbuka bersamaan (CAND-08) — dipertahankan apa adanya, dikonfirmasi dev
- Cleanup `type='json'`→`type='jsonrpc'` — opsional, boleh dikerjakan di step 6 kalau waktu memungkinkan, TIDAK wajib untuk migrasi dianggap selesai
- Data migration (step 7) — N/A, port kode saja
