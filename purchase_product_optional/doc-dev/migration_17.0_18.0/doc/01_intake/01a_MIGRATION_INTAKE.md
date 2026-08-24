# Migration Intake — purchase_product_optional

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** Draft — menunggu review user

---

## 0. Folder Referensi

- [x] `native-target` (Community, Odoo 18.0) — `D:\Kuncoro\doodex\repo\odoo18`. Dikonfirmasi dev 2026-08-24.
- [x] `native-source` (Community, Odoo 17.0) — `D:\Kuncoro\doodex\repo\odoo17`. Sudah ada di disk, dipakai untuk cross-check §2.
- [x] **`native-target-enterprise`** — `D:\Kuncoro\doodex\repo\enterprise18`. Dikonfirmasi dev 2026-08-24 (relevan karena `sale_product_configurator` sempat disangka Enterprise di catatan migrasi lama — lihat §2 untuk koreksi).
- [x] `native-source-enterprise` — `D:\Kuncoro\doodex\repo\enterprise17`. Sudah ada di disk, dicek langsung: **`sale_product_configurator` TIDAK ADA di sini** (lihat §2).
- [x] **`third-party-source`/`third-party-target`** — **Tidak diperlukan.** Kedua dependency non-core modul ini (`purchase_product_matrix`, `sale_product_configurator`) dikonfirmasi native Community (ada langsung di `odoo17/addons/` dan `odoo18/addons/`), bukan OCA/vendor.

### 0a. Konfirmasi Branch/Versi

- [x] Folder `source-codebase` (`purchase-product-optional-migration-18-source`) — branch `backfill/17.0`, dikonfirmasi dev 2026-08-24 (pilihan eksplisit: pakai branch backfill, bukan `17.0` polos, karena membawa `doc-dev/backfill/` — functional spec + FINDINGS yang sudah tervalidasi eksekusi nyata).
- [x] Folder `target-codebase` (repo ini) — branch `migration/18.0`, dibuat dari `origin/backfill/17.0` (nama dikonfirmasi verbatim oleh dev 2026-08-24).
- [x] Dikonfirmasi dua clone fisik terpisah (sibling folder berbeda, bukan symlink/alias satu folder yang sama) — diverifikasi lewat `ls` terpisah setelah clone.

### 0b. Gate — Path Absolut di `.claude/settings.json`

- [x] **Dipenuhi 2026-08-24.** Semua placeholder `{{ABS_PATH_...}}` sudah diisi path absolut nyata (`source-codebase`, `odoo18`, `enterprise18`, `odoo17`, `enterprise17`, `migration-tool/knowledge`, `migration-tool/templates`). Baris `ABS_PATH_THIRD_PARTY_SOURCE`/`ABS_PATH_THIRD_PARTY_TARGET` dihapus seluruhnya (tidak relevan — lihat §0 dan §2, kedua dependency non-core modul ini native Community, bukan OCA).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Koreksi terhadap catatan migrasi lama (2026-08-24):** `sale_product_configurator` yang di `migration-records/purchase_product_optional_17_18/SUMMARY.md` (project migrasi sebelumnya, DIABAIKAN per instruksi) disebut "Enterprise di 17.0" — **hasil cek langsung ke `native-source`/`native-source-enterprise` kali ini menunjukkan modul itu ada di `odoo17/addons/sale_product_configurator` (Community)**, bukan di `enterprise17`. Mohon konfirmasi: apakah instance produksi Doodex memang menjalankan `sale_product_configurator` versi Community (bukan varian Enterprise custom lain)? Kalau iya, `native-target-enterprise`/`native-source-enterprise` tetap dijaga terhubung untuk jaga-jaga tapi kemungkinan besar tidak akan dipakai di Step 2.
2. **Modul `sale_product_configurator` dihapus total di 18.0** — dicek langsung, tidak ada lagi di `odoo18/addons/` maupun `enterprise18/` (hanya tersisa `test_sale_product_configurators`, modul test). Fungsinya (variant generation, `optional_product_ids`, `has_optional_products`) sudah dipindah ke `product`/`sale` core. Ini dependency WAJIB dihapus dari `depends` di manifest 18.0 — akan dianalisis detail di Step 2.
3. **8 bug/quirk existing di 17.0 (F-01 s/d F-08, `source-codebase/doc-dev/backfill/FINDINGS.md`)** — semua sudah dikonfirmasi via eksekusi nyata Docker (bukan dugaan statis), termasuk satu yang **berpotensi Tinggi dampaknya**: `onchange_partner_id` di `purchase_order.py` menimpa TOTAL method core Odoo dengan nama sama (F-02, dikonfirmasi lewat inspeksi MRO langsung ke database live). Default migrasi ini: **dipertahankan apa adanya** (bug-for-bug parity), TIDAK diperbaiki — mohon konfirmasi ini sesuai keinginan, atau ada bug tertentu yang justru ingin sekalian diperbaiki di kesempatan migrasi ini (kalau ada, sebutkan yang mana, dicatat sebagai perubahan disengaja bukan efek samping migrasi).
4. **View `purchase_order_views.xml` pakai `<tree>`** (2× xpath target `//tree/...` + 1× `<tree>` inline untuk sub-view `product_custom_attribute_value_ids`) — berpotensi jadi migration blocker kalau 18.0 tidak lagi menerima tag `<tree>` untuk definisi view (akan dicek presisi terhadap `native-target` di Step 2, bukan diasumsikan dari nama tag saja).
5. **Sifat migrasi:** dikonfirmasi **port kode saja** — tidak ada data produksi yang perlu dimigrasikan, Step 7 di-skip (N/A).
6. **Deadline/owner:** belum disebutkan — dianggap belum relevan/tidak urgent untuk saat ini, dilewati.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `purchase_product_optional` (satu modul, tidak ada modul custom lain yang ikut).
- Deskripsi singkat: menambahkan **Product Configurator** (pola sama seperti `sale_product_configurator`, tapi untuk konteks Purchase) ke form Purchase Order — dialog konfigurasi atribut varian + optional products saat memilih produk di baris PO, dengan harga per-vendor dan konversi multi-currency.
- Modul-modul ini saling depend: tidak ada modul custom lain — hanya depend ke 3 modul native (`purchase`, `purchase_product_matrix`, `sale_product_configurator`).

## 2. Dependency Map (auto-scan, dikonfirmasi silang langsung ke native-source/native-target)

| Dependency | Tipe | Versi tersedia di target (18.0)? | Catatan |
|---|---|---|---|
| `purchase` | Native Community | Ya | Tidak ada perubahan struktural yang diketahui memengaruhi modul ini — detail di Step 2. |
| `purchase_product_matrix` | Native Community (`odoo18/addons/purchase_product_matrix`, dikonfirmasi ada) | Ya, tapi ada breaking change JS (`PurchaseOrderLineProductField` — lihat `migration-tool/knowledge/dependency-compat/purchase_product_matrix/17-to-18.md`, entry lama tetap dipakai karena ini knowledge base yang sudah dikurasi, BUKAN migration-records yang diabaikan). | Community di kedua versi — dikonfirmasi langsung `find odoo17/addons` & `odoo18/addons`, bukan diasumsikan dari catatan lama. |
| `sale_product_configurator` | **Native Community** di 17.0 (`odoo17/addons/sale_product_configurator`, dikonfirmasi langsung — BUKAN Enterprise, koreksi atas catatan migrasi lama) | **TIDAK ADA** di 18.0 (dicek `odoo18/addons/` dan `enterprise18/` — keduanya kosong untuk modul ini, hanya `test_sale_product_configurators` yang tersisa) | **Dependency ini harus dihapus dari `depends`** — fungsinya pindah ke `product`/`sale` core 18.0. Detail migrasi di Step 2/3. |

Dependency opsional yang dicek runtime — tidak ditemukan pola `'x' in self.env`/runtime-check serupa di kode modul ini (dicek `grep` ke seluruh `models/`, `controllers/`).

## 2b. Struktur & Fitur Modul (auto-scan, dikonfirmasi baca langsung tiap file)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 yang relevan |
|---|---|---|---|
| Controllers (route custom) | ✅ Ya | `controllers/main.py` — 4 route JSON-RPC (`get_values_purchase`, `create_product`, `update_combination`, `get_optional_products`) | D1 |
| Assets/CSS/JS custom | ✅ Ya | `static/src/**` (JS/SCSS/XML), key `assets` di `__manifest__.py` (`web.assets_backend` + `web.assets_tests` untuk Tour) | D2, E, F |
| Komponen Owl/JavaScript custom | ✅ Ya | 5 komponen: `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`, `ProductConfiguratorDialogPurchase` — semua sudah Owl 2 (ES6 `class extends Component`, `onWillStart`, flat import `@odoo/owl`), TIDAK ada pola Owl 1/`Component.extend()`/`odoo.define()` | E, F |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation | ⬜ Tidak ditemukan | — | B2 (kemungkinan N/A) |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ⬜ Tidak ditemukan di `purchase_order_views.xml` (hanya xpath + `optional="hide"`) | — | C2 (kemungkinan N/A, dikonfirmasi ulang di Step 6 Applicability Check) |

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek `FUNCTIONAL_SPEC.md` lama: **ADA**, di `source-codebase/purchase_product_optional/doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (hasil project doc-dev-backfill 2026-07-29, bukan dari project migrasi lama yang diabaikan — ini dokumen berbeda, levelnya "apa yang kode 17.0 lakukan", ditulis sebelum project migrasi manapun).
  - Proses: dibaca sebagai draft awal, cross-check ke kode `source-codebase` (model `.py`, controller, views) satu per satu — **semua BR-01 s/d BR-12 di spec lama cocok dengan kode aktual** (dikonfirmasi baca `models/purchase_order.py`, `purchase_order_line.py`, `product_template.py`, `controllers/main.py`, `views/purchase_order_views.xml` langsung, 2026-08-24). Tidak ada penyimpangan ditemukan → semua diberi tag `[MATCH]` di `01b_BASELINE_SPEC.md`.
  - Bonus: spec lama sudah execution-verified (Docker + Odoo Tour headless, lihat `FINDINGS.md` source), bukan cuma baca statis — confidence tinggi.
- [x] `01b_BASELINE_SPEC.md` sudah diisi — lihat dokumen terpisah.

### 4a. Dokumen Pelengkap Lain

- [x] **Ditanya ke dev 2026-08-24.** Jawaban: dokumen pelengkap ADA, yaitu persis `doc-dev/backfill/` di `source-codebase` (functional spec, acceptance criteria, findings, test plan hasil project doc-dev-backfill) — **sudah dibaca dan dipakai** sebagai dasar `01b_BASELINE_SPEC.md`. Tidak ada dokumen lain di luar itu (dikonfirmasi eksplisit oleh dev — "selain ini tidak ada").

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan.

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh BR-01 s/d BR-12 (`01b_BASELINE_SPEC.md`), termasuk 8 bug/quirk F-01..F-08 (dipertahankan, lihat poin 3 "Ringkasan untuk Review").
- Yang sengaja diubah/di-drop: dependency `sale_product_configurator` dihapus dari `depends` (dependency itu sendiri hilang di 18.0 — bukan pilihan, keharusan kompatibilitas). Detail penggantian mekanismenya di `03_MIGRATION_SPEC.md` (Step 3).

## 6. Constraint

- Deadline: belum disebutkan — dilewati, tidak urgent saat ini.
- Owner tiap step: belum ditunjuk — dev (Kuncoro) sejauh ini berperan sebagai reviewer/approver semua gate.
