# Diff & Compatibility Analysis — purchase_product_optional

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `01_intake/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | `migration-tool/knowledge/version-diffs/17-to-18.md` §1, §1c |
| `dependency-compat/purchase_product_matrix/` | Ya | `migration-tool/knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` |

Kedua entry ini adalah knowledge base yang sudah dikurasi (bukan `migration-records/purchase_product_optional_17_18/SUMMARY.md` dari project migrasi sebelumnya, yang DIABAIKAN sesuai instruksi dev) — dipakai sebagai referensi, tapi setiap klaim di dalamnya tetap diverifikasi ulang langsung ke `native-target`/`native-source` sebelum dipakai sebagai dasar keputusan (lihat catatan koreksi di DIFF-03).

## 0b. Gate Community vs Enterprise

- `01a_MIGRATION_INTAKE.md` §2: dependency `sale_product_configurator` **dikonfirmasi Community** (bukan Enterprise, koreksi atas dugaan awal) — jadi secara ketat gate ini tidak wajib (tidak ada baris "Native Enterprise" di §2). **Tetap dicek langsung ke `native-target-enterprise` (`enterprise18`) untuk memastikan** — hasilnya: modul `sale_product_configurator` juga TIDAK ADA di `enterprise18` (dicek `find` langsung, 2026-08-24). Kesimpulan tidak berubah dari status Community.
- `native-source-enterprise` (`enterprise17`) juga dicek: `sale_product_configurator` TIDAK ADA di sana juga (hanya ada di `odoo17/addons/`) — mengonfirmasi ulang modul ini murni Community di kedua versi.

## 0c. Gate Transitive Dependency

- Dependency yang akan dihapus dari `depends`: `sale_product_configurator`.
- Modul yang ditarik transitif olehnya di 17.0: dicek `odoo17/addons/sale_product_configurator/__manifest__.py` → depends ke `sale`, `product_matrix`... (`sale` yang paling relevan).
- Kode modul target (`controllers/main.py:90,203`) memakai `product_template.optional_product_ids` — **field ini HANYA didefinisikan di `sale/models/product_template.py`** (dikonfirmasi `grep` langsung ke `native-target`: TIDAK ADA di `product/models/product_template.py`, base Community). Lihat **DIFF-03** — `sale` WAJIB ditambahkan eksplisit ke `depends`.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `views/purchase_order_views.xml` — 2× xpath `//tree/field[...]`, 1× `<tree>` inline (sub-view `product_custom_attribute_value_ids`) | Tag view `<tree>` | **Dihapus** — 18.0 core menolak `<tree>`, hanya terima `<list>` (dikonfirmasi install gagal total, `ParseError: Invalid view type: 'tree'`) | **Kritis — install-blocking.** Modul tidak akan lolos parsing XML paling awal kalau tidak diganti `<list>`. | `knowledge/version-diffs/17-to-18.md` §1 (verified via dry run real, `odoo:18.0`) |
| DIFF-02 | `__manifest__.py` — `depends: [..., 'sale_product_configurator']` | Modul `sale_product_configurator` (native) | **Dihapus total** — tidak ada di `odoo18/addons/` maupun `enterprise18/` (dikonfirmasi langsung `find`, 2026-08-24; hanya tersisa `test_sale_product_configurators`, modul test) | **Kritis — install-blocking.** `depends` ke modul yang tidak ada = gagal install total. Dependency WAJIB dihapus dari manifest. | `native-target` + `native-target-enterprise`, dikonfirmasi langsung 2026-08-24 |
| DIFF-03 | `controllers/main.py:90,203` — `product_template.optional_product_ids` | Field `optional_product_ids` (Many2many) | Field ini ada di 18.0 tapi **hanya didefinisikan di `sale/models/product_template.py:53`** (dikonfirmasi `grep` langsung — TIDAK ADA sama sekali di `product/models/product_template.py` base Community) | **Tinggi — silent `AttributeError` pasca-install.** Di 17.0, `sale` ditarik transitif lewat `sale_product_configurator` (dihapus di DIFF-02) — begitu dependency itu hilang tanpa `sale` ditambahkan eksplisit, field ini hilang total. **Koreksi atas knowledge base `1c`** (yang menyebut fungsi "pindah ke `product` Community") — presisinya: method dasar (`_get_first_possible_combination`, `_create_product_variant`, `_get_variant_for_combination`, `_get_attribute_exclusions`, base `get_single_product_variant`) ada di `product`, TAPI field `optional_product_ids` itu sendiri cuma di `sale`. **Fix wajib: tambahkan `'sale'` eksplisit ke `depends`.** | `native-target` (`odoo18/addons/product/models/product_template.py` vs `sale/models/product_template.py`), dikonfirmasi langsung `grep`, 2026-08-24 |
| DIFF-04 | `static/src/js/purchase_product_field.js:78,89` — baca `result.purchase_warning`/`result.mode` dari RPC `get_single_product_variant` | `product.template.get_single_product_variant()` — base di `product/models/product_template.py:1413`, di-extend `sale/models/product_template.py:211` (nambah `sale_warning`/`has_optional_products`, BUKAN `purchase_warning`/`mode`) | **Tidak berubah** — dikonfirmasi tidak ada override khusus Purchase di `purchase`/`purchase_product_matrix` baik di 17.0 maupun 18.0. `purchase_warning`/`mode` sejak awal tidak pernah terisi (dead code) — bukan regresi migrasi. | **Rendah/informational** — perilaku identik 17.0↔18.0, dipertahankan apa adanya, TIDAK diperbaiki (konsisten prinsip bug-for-bug parity). | `knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` poin 3, dikonfirmasi ulang langsung ke `native-target` 2026-08-24 |
| DIFF-05 | `static/src/js/purchase_product_field.js:97` — override `_editProductConfiguration()` | `PurchaseOrderLineProductField._editProductConfiguration` (`purchase_product_matrix`) | **Rename** → `onEditConfiguration()` (dikonfirmasi langsung `odoo18/addons/purchase_product_matrix/static/src/js/purchase_product_field.js:59`) | **Sedang — regresi silent kalau tidak di-rename.** Method lama jadi dead code (base class tidak lagi memanggilnya) — alur "edit baris yang sudah dikonfigurasi" diam-diam jatuh ke behavior default grid, bukan membuka `ProductConfiguratorDialogPurchase` custom. Fix: rename ke `onEditConfiguration()`, isi method TIDAK berubah. | `knowledge/dependency-compat/purchase_product_matrix/17-to-18.md` poin 1, dikonfirmasi langsung `native-target` |
| DIFF-06 | `static/src/js/purchase_product_field.js:92` — `this._openGridConfigurator()` (tanpa argumen) | `PurchaseOrderLineProductField._openGridConfigurator(edit)` (`purchase_product_matrix`) | Base class 18.0 sekarang eksplisit `if (edit)` dan dipanggil dengan `false`/`true` eksplisit dari base (dikonfirmasi `odoo18/addons/purchase_product_matrix/...:65`) | **Rendah** — `undefined` (argumen tidak diberikan) falsy, behave sama seperti `false` secara sintaks. TETAP wajib diverifikasi di Checkpoint G2 (eksekusi nyata), jangan diasumsikan aman hanya dari baca kode (lesson `knowledge/dependency-compat/...` poin 2). | Sama seperti DIFF-05 |
| DIFF-07 | `static/src/js/product_configurator_dialog/product_configurator_dialog.js:46,211,225,232,245` — `this.rpc = useService("rpc")` + 4× `this.rpc(url, params)` | Owl service `rpc` | **Dihapus total sebagai service** — `@web/core/network/rpc.js` sekarang ekspor fungsi biasa `rpc(url, params)`, bukan service ter-registrasi | **Kritis — runtime crash.** `Error: Service rpc is not available` saat `setup()`, HANYA terdeteksi lewat eksekusi browser nyata (bukan review statis — sintaks tetap valid). Fix: ganti ke `import { rpc } from "@web/core/network/rpc"`, panggil `rpc(url, params)` langsung (bukan `this.rpc(...)`). | `knowledge/version-diffs/17-to-18.md` §1c, dikonfirmasi langsung baca kode modul 2026-08-24 |
| DIFF-08 | `models/product_template.py:26-29`, `controllers/main.py:288-293` — pemanggilan `res.currency._convert()` | `res.currency._convert(from_amount, to_currency, company=None, date=None, round=True)` | **Signature tidak berubah** 17.0→18.0 | Tidak ada risiko — `models/product_template.py` panggil tanpa `company`/`date` (aman, tetap optional); `controllers/main.py` sudah passing `company`/`date` eksplisit (lebih lengkap, tidak perlu diubah). | `knowledge/version-diffs/17-to-18.md` §1, baris `res.currency._convert()` |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada — kedua dependency non-core modul ini (`purchase_product_matrix`, `sale_product_configurator`) native Community, sudah dicakup §1 di atas. Tidak ada dependency OCA/vendor.

## 3. Temuan Baru — Migration Records

- **Koreksi presisi terhadap `knowledge/version-diffs/17-to-18.md` §1c** (kategori version-diff): narasi lama menyebut fungsi `sale_product_configurator` "pindah ke `product` (Community)" secara umum — presisinya, field `optional_product_ids` itu sendiri HANYA ada di `sale`, bukan `product` base. Dicatat sebagai kandidat klarifikasi di `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` (entry baru, dev sudah instruksikan abaikan isi LAMA file itu sebagai acuan keputusan — tapi menambah entry baru dengan tanggal jelas tetap konsisten prinsip "jangan hilangkan jejak audit").
- Promosi ke `knowledge/` menunggu sesi curation eksplisit terpisah — tidak dilakukan di step ini.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 `<tree>`→`<list>` | 🔴 Kritis | Install-blocking, wajib fix Fase A |
| DIFF-02 Hapus `sale_product_configurator` dari `depends` | 🔴 Kritis | Install-blocking, wajib fix Fase A |
| DIFF-03 Tambah `sale` eksplisit ke `depends` | 🟠 Tinggi | Silent `AttributeError` pasca-install kalau terlewat |
| DIFF-07 `useService("rpc")` dihapus | 🔴 Kritis (runtime) | Crash total saat buka dialog konfigurator — HANYA terdeteksi eksekusi nyata (G2) |
| DIFF-05 `_editProductConfiguration`→`onEditConfiguration` | 🟡 Sedang | Regresi silent alur edit baris terkonfigurasi |
| DIFF-06 `_openGridConfigurator()` tanpa argumen | 🟢 Rendah | Kemungkinan aman, verifikasi G2 |
| DIFF-04 `purchase_warning`/`mode` dead code | 🟢 Rendah/informational | Perilaku identik 17↔18, dipertahankan |
| DIFF-08 `_convert()` signature | ⚪ Tidak ada risiko | Konfirmasi stabil |
