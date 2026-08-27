# Migration Spec (Teknis) — purchase_product_optional

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

---

## 1. Ringkasan Strategi

Modul ini kecil (1 model view, 4 route controller, 5 komponen Owl modern) dan sudah 100% ES6/Owl 2 —
sebagian besar port langsung tanpa perubahan. **4 area butuh perbaikan wajib** (2 install-blocking, 1
silent-crash pasca-install, 1 runtime-crash JS), dan **2 area butuh perbaikan disarankan** (regresi
silent kalau tidak difix, risiko rendah). Tidak ada perubahan business logic — seluruh 18 klaim
`01b_BASELINE_SPEC.md` (termasuk 8 bug/quirk F-01..F-08) dipertahankan bug-for-bug.

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` (`depends`) | DIFF-02, DIFF-03 | Hapus `'sale_product_configurator'`, tambah `'sale'` eksplisit. `auto_install: True` tetap dipertahankan (BSL-012) — sekarang auto-install saat `purchase`, `purchase_product_matrix`, `sale` ter-install. | Rendah (mekanis) | BSL-012 |
| `__manifest__.py` (`version`) | — | Bump ke `18.0.1.0.0` | Rendah | — |
| `views/purchase_order_views.xml` | DIFF-01 | 3× `<tree>` → `<list>` (2 xpath target, 1 inline sub-view). Tidak ada perubahan field/atribut lain. | Rendah (mekanis, tapi install-blocking kalau terlewat) | BSL-011 |
| `static/src/js/purchase_product_field.js` | DIFF-05 | Rename `_editProductConfiguration()` → `onEditConfiguration()`. Isi method TIDAK berubah. | Sedang | BSL-001, BSL-004 |
| `static/src/js/purchase_product_field.js` | DIFF-06 | `this._openGridConfigurator()` (baris 92) — port apa adanya (undefined tetap falsy, konsisten base class), verifikasi eksplisit di G2. | Rendah | BSL-001 |
| `static/src/js/product_configurator_dialog/product_configurator_dialog.js` | DIFF-07 | Hapus `this.rpc = useService("rpc")` dari `setup()`. Tambah `import { rpc } from "@web/core/network/rpc"` di top-level. Ganti 4× `this.rpc(url, params)` → `rpc(url, params)`. Tidak ada perubahan parameter/logic lain. | Tinggi (kalau terlewat = crash total saat dialog dibuka) | BSL-001, BSL-002, BSL-003, BSL-014 |
| `controllers/main.py` | DIFF-04, DIFF-08 | **Tidak ada perubahan** — kedua simbol (`optional_product_ids` lewat DIFF-03 fix di manifest, `_convert()` di DIFF-08) sudah aman setelah `sale` ditambahkan ke `depends`. | Tidak ada | — |
| `models/*.py` | — | **Tidak ada perubahan** — tidak ada pemakaian API yang dihapus/berubah di 18.0 (dikonfirmasi `grep` §1 `knowledge/version-diffs`: tidak ada `user_has_groups`/`check_access_rights`/`_name_search`/`_check_recursion`/`group_operator`/override `copy`/`create` custom). F-01 (`product_add_mode` kwarg asing) dipertahankan apa adanya (keputusan dev). | Tidak ada | BSL-005..009, 013, 017, 018 |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi di 18.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `18.0.x` | `__manifest__.py` | `knowledge/version-diffs/17-to-18.md` |
| 2 | `depends` ke `sale_product_configurator` (modul tidak ada di 18.0) | `__manifest__.py` | DIFF-02 |
| 3 | Tag `<tree>` di view (3 lokasi) | `views/purchase_order_views.xml` | DIFF-01, `knowledge/version-diffs/17-to-18.md` §1 |

**Priority:** HIGH — perbaiki sebelum G1/runtime testing apapun.

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `ProductConfiguratorDialogPurchase` | `product_configurator_dialog.js` | 🔴 Tinggi | `useService("rpc")` dihapus (DIFF-07) — WAJIB fix sebelum dialog bisa dibuka sama sekali |
| `PurchaseOrderLineProductField` (patch) | `purchase_product_field.js` | 🟡 Sedang | `_editProductConfiguration`→`onEditConfiguration` (DIFF-05); `_openGridConfigurator()` arg (DIFF-06, verifikasi bukan fix wajib) |
| `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice` | `static/src/js/**` | 🟢 Rendah | Sudah Owl 2 modern, tidak ada pola deprecated ditemukan — port 1:1, verifikasi di G2 |

**Urutan wajib:** JS dulu (Fase E), baru template (Fase F) — modul ini tidak punya perubahan template Owl yang perlu (tidak ada `t-att-on-click` ditemukan), jadi Fase F kemungkinan besar N/A murni port, tetap dicek di Applicability Check step 6.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada perubahan route/decorator yang diperlukan — `@route(..., type='json', auth='user')` tetap valid di 18.0 | `controllers/main.py` | — |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Hapus `sale_product_configurator`, tambah `sale` di `depends` | `__manifest__.py` | HIGH |
| 2 | Key `assets` (`web.assets_backend`, `web.assets_tests`) sudah pola modern — tidak perlu diubah | `__manifest__.py` | — |

### Kompatibilitas Data Model

Tidak ada — modul tidak menambah model baru, cuma `_inherit`. Tidak ada field yang berubah struktur besar antar versi yang relevan ke modul ini (BSL-NNN semua tetap berlaku).

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `purchase_product_matrix.PurchaseOrderLineProductField` breaking changes (DIFF-05, DIFF-06) | `purchase_product_field.js` | HIGH (05) / LOW (06) |
| 2 | Gotcha desain "dua dialog terbuka bersamaan" (`knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` poin 4) — dikonfirmasi TIDAK reachable untuk modul ini (override `_onProductTemplateUpdate` modul ini TIDAK memanggil `super()` di percabangan yang membuka `_openGridConfigurator` — cek ulang di Step 8) | `purchase_product_field.js:55-95` | Verifikasi saja, bukan fix |

### Urutan Prioritas Testing

1. Install & startup — manifest (`depends`, version), `<tree>`→`<list>`
2. Core user flow — buka form PO, pilih produk, dialog konfigurator terbuka (BSL-001)
3. Harga per-vendor + konversi currency (BSL-002, BSL-003, BSL-013, BSL-018)
4. Widget backend (Owl) — terutama `ProductConfiguratorDialogPurchase` (DIFF-07 fix)
5. Edit baris terkonfigurasi (DIFF-05 fix)

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Xpath target `//tree/field[@name='product_template_id']` | `views/purchase_order_views.xml:9` | `//tree/` → `//list/` |
| 2 | Xpath target `//tree/field[@name='product_id']` | `views/purchase_order_views.xml:23` | `//tree/` → `//list/` |
| 3 | Inline `<tree>` sub-view untuk `product_custom_attribute_value_ids` | `views/purchase_order_views.xml:15` | `<tree>` → `<list>` |
| 4 | `view_mode` di action | — | N/A, modul ini tidak mendefinisikan `ir.actions.act_window` sendiri |

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Fase A (manifest + view + ACL) | Kecil | 3 perubahan mekanis, tidak ada ACL custom di modul ini (tidak ada model baru/TransientModel) |
| Fase E (JavaScript) | Kecil-Sedang | 2 file, ~10 baris perubahan total (DIFF-05, DIFF-07) |
| Fase F (Template) | Kecil | Kemungkinan N/A murni, verifikasi di Applicability Check |
| Testing (G1/G2/Step 9/10) | Sedang | Docker tersedia (Mode C, Claude Code CLI) — eksekusi nyata dilakukan AI |

## 3. Data Migration

N/A — sifat migrasi port kode saja (`01a_MIGRATION_INTAKE.md` §3), tidak ada data produksi.

## 4. Scope

### Termasuk
- Fix DIFF-01, DIFF-02, DIFF-03, DIFF-05, DIFF-07 (wajib)
- Verifikasi DIFF-04, DIFF-06, DIFF-08 (tidak ada perubahan kode, cukup dikonfirmasi aman di G2/step 9)

### Di Luar Scope (sengaja, disetujui di intake)
- Perbaikan F-01 s/d F-08 (bug/quirk existing 17.0) — dipertahankan apa adanya, keputusan dev 2026-08-24
- Refactor/cleanup style apapun di luar yang wajib untuk kompatibilitas 18.0
