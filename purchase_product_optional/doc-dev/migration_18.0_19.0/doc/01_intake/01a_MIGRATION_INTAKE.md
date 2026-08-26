# Migration Intake — purchase_product_optional

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** Disetujui — semua asumsi terbuka dikonfirmasi dev 2026-08-26

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist (dikonfirmasi dev, sesi ini, 2026-08-26):**

- [x] `native-target` (Community 19.0) — **Ya**, tersedia: `D:\Kuncoro\doodex\repo\enterprise19.0` (folder gabungan Community+Enterprise, lihat catatan struktur di bawah).
- [x] `native-source` (Community 18.0) — **Ya**, tersedia: `D:\Kuncoro\doodex\repo\odoo18`.
- [x] `native-target-enterprise` — **Dikonfirmasi dev: tetap di-connect sebagai referensi**, walau §2 auto-scan manifest TIDAK menemukan dependency Enterprise (`depends: purchase, purchase_product_matrix, sale` — semua Community). Dev eksplisit minta tetap merujuk ke Enterprise "meskipun belum pasti" (pola sama seperti project `advanced_sales_analysis` 18→19 — instance produksi kemungkinan jalan Enterprise walau modul ini sendiri Community-only). Path: `D:\Kuncoro\doodex\repo\enterprise19.0` (SATU folder gabungan, sama dengan `native-target` — lihat catatan struktur). `native-source-enterprise` (18.0): `D:\Kuncoro\doodex\repo\enterprise18`.
- [x] `third-party-source`/`third-party-target` — **Dikonfirmasi final dev (2026-08-26): tidak ada dependency OCA/third-party.** Konsisten dengan auto-scan §2 (`depends: purchase, purchase_product_matrix, sale` — semua modul core Odoo). Tidak ada folder third-party di-connect.

> **Catatan struktur folder gabungan (2026-08-26):** `D:\Kuncoro\doodex\repo\enterprise19.0` berisi `odoo/` (framework + `addons/` core) DENGAN modul Enterprise (`account_accountant`, dst) sudah digabung di `odoo/addons/` yang sama — SATU clone ini melayani DUA peran (`native-target` Community + `native-target-enterprise`). Dikonfirmasi lewat `ls` langsung (bukan diasumsikan), sama seperti pola yang sudah divalidasi di project `advanced_sales_analysis` 18→19. Folder ini BUKAN git repo (hasil extract, bukan clone) — tidak ada `git log`/`git diff` di situ.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` (`D:\Kuncoro\doodex\repo\purchase-product-optional-migration-19-source`) — branch `migration/18.0` (dikonfirmasi dev, verbatim di sesi ini; di-clone 2026-08-26 dari `origin/migration/18.0`, HEAD `105f9cd`).
- [x] Folder `target-codebase` (`D:\Kuncoro\doodex\repo\purchase-product-optional-migration-19`, folder ini) — branch `migration/19.0_target` (dikonfirmasi dev verbatim, dibuat 2026-08-26 dari `origin/migration/18.0` via `git checkout -b`).
- [x] Kedua folder dikonfirmasi BUKAN folder yang sama — dua clone fisik terpisah (sibling di `D:\Kuncoro\doodex\repo\`).
- [x] Versi Odoo semantik: **18.0 → 19.0**, dikonfirmasi eksplisit dev di percakapan yang meminta migrasi ini ("Lakukan migrasi 18 ke 19").

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` → `D:/Kuncoro/doodex/repo/purchase-product-optional-migration-19-source`
- [x] `ABS_PATH_MIGRATION_TOOL` → `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE` → `D:/Kuncoro/doodex/repo/enterprise19.0` (sama dengan native-target, folder gabungan)
- [x] `ABS_PATH_NATIVE_SOURCE_ENTERPRISE` → `D:/Kuncoro/doodex/repo/enterprise18`
- [ ] `ABS_PATH_THIRD_PARTY_SOURCE` / `ABS_PATH_THIRD_PARTY_TARGET` → dihapus dari `settings.json` (tidak dipakai, konsisten dengan §0 di atas — akan ditambahkan balik kalau konfirmasi final dev di step 2 ternyata menemukan dependency OCA).

Semua path sudah diisi nyata di `.claude/settings.json` (commit `7d327ec`) — tidak ada `{{ABS_PATH_...}}` literal tersisa.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Semua poin di bawah SUDAH dikonfirmasi dev (2026-08-26)** — tidak ada asumsi terbuka tersisa dari step 1.

1. **Third-party/OCA dependency** — **Dikonfirmasi: tidak ada.** Konsisten dengan scan manifest bersih.
2. **Source masih aktif dikembangkan?** — **Dikonfirmasi: Tidak (beku).** `migration/18.0` tidak menerima perubahan baru selama project 18→19 ini berjalan — `SYNC_POLICY.md` tidak relevan.
3. **BSL-005 / override total `onchange_partner_id` core** — **Dikonfirmasi: dipertahankan apa adanya** (bug-for-bug parity), tidak diperbaiki di migrasi ini.
4. **Finding CAND-08 (17→18, migration-tool SUMMARY)** — pola "dua dialog terbuka bersamaan tanpa koordinasi" (`_onProductTemplateUpdate`, `purchase_product_matrix` + custom Product Configurator), dikonfirmasi ADA di 17.0 dan 18.0. Termasuk kategori "bug/quirk lama" pada poin 3 di atas — **dipertahankan apa adanya**, tidak diperbaiki.
5. **Deadline/owner (§6)** — belum disebutkan dev, belum relevan/urgent, dilewati.

Tidak ada blocker faktual yang menghalangi lanjut ke Step 1b (Baseline Spec) — 3 poin di atas adalah asumsi terbuka yang didokumentasikan transparan, bukan hal yang menghalangi progres.

---

## 1. Modul & Scope

- **Modul yang dimigrasi:** purchase_product_optional (satu modul, tidak ada modul lain dalam repo ini)
- **Deskripsi singkat fungsi modul:** Override view `sale.order`/`purchase.order` untuk mengizinkan konfigurasi produk (product configurator) langsung di form Purchase Order — termasuk dialog "Choose Product Variants" (via `purchase_product_matrix`) dan dialog custom "Product Configurator" (optional products, no-variant attributes, extra price). Juga override onchange partner untuk currency handling di PO.
- **Apakah modul-modul ini saling depend satu sama lain:** N/A — hanya satu modul custom di repo ini.

## 2. Dependency Map (auto-scan)

Dibaca dari `__manifest__.py` di `source-codebase` (`purchase-product-optional-migration-19-source`, branch `migration/18.0`).

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target (19.0)? | Catatan |
|---|---|---|---|
| `purchase` | Native Community | Ya — dikonfirmasi `enterprise19.0/odoo/addons/purchase` ada | Core Purchase |
| `purchase_product_matrix` | Native Community (LGPL-3, dikonfirmasi ulang saat migrasi 17→18, CAND-02 — BUKAN Enterprise seperti dugaan awal) | Ya — dikonfirmasi `enterprise19.0/odoo/addons/purchase_product_matrix` ada | Method `_onProductTemplateUpdate`/`PurchaseOrderLineProductField` sudah pernah berubah struktur besar 17→18 (CAND-02) — kandidat breaking change lagi di 18→19, wajib dicek ulang step 2 |
| `sale` | Native Community | Ya — dikonfirmasi `enterprise19.0/odoo/addons/sale` ada | Field `tax_id`→`tax_ids` rename di `sale.order.line` (knowledge `18-to-19.md` §1a) — modul ini TIDAK terlihat baca `sale.order.line.tax_id` langsung dari scan awal, perlu dicek ulang di step 2 |

Dependency opsional yang dicek runtime — tidak ditemukan pola `'x' in self.env`/`self.env[var]` dinamis di `models/` (grep bersih, hanya `self.env['ir.config_parameter']`/`self.env['res.currency']` — literal string, bukan dependency opsional).

**Tidak ada dependency Enterprise maupun OCA/third-party** terdeteksi dari manifest — lihat §0 untuk status konfirmasi final dev soal third-party.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 yang jadi relevan |
|---|---|---|---|
| Controllers (route custom) | ☑ Ya | `controllers/main.py` | D1 |
| Assets/CSS/JS custom | ☑ Ya | `static/src/js/**/*.js`, `.scss`; key `assets` (`web.assets_backend`, `web.assets_tests`) di manifest | D2, E, F |
| Komponen Owl/JavaScript custom | ☑ Ya | 5 komponen: `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`, `ProductConfiguratorDialogPurchase` (`static/src/js/**`) — dikonfirmasi sudah Owl 2 modern (ES6 `class extends Component`, flat import `@odoo/owl`, `onWillStart()`) sejak migrasi 17→18 (SUMMARY.md 17_18, catatan Owl/JS) | E, F |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Grep `models/*.py` bersih — tidak ada `fields.Json`, tidak ada `self.env[<variabel>]` | B2 → kandidat N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ Tidak | Grep `views/purchase_order_views.xml` bersih (0 match `attrs=`/`domain=`/`context=`) | C2 → kandidat N/A |

Test suite: `tests/test_purchase_product_optional.py` (Python unit), `tests/test_purchase_product_optional_tour.py` + `static/tests/tours/purchase_product_optional_tour.js` (Tour/QUnit) — relevan untuk checkpoint G1/G2 dan Mode D (Tour headless) di step 6/9.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi — step 7 Data Migration Scripts wajib jalan)

Dikonfirmasi dev, 2026-08-26.

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Ya, ada** —
  `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (dari project BACKFILL, basis 17.0) DAN
  `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (basis 18.0, hasil migrasi
  17→18 — lebih relevan sebagai basis langsung karena sudah cross-check ke kode 18.0). Proses:
  (1) baca `01b_BASELINE_SPEC.md` (18.0) sebagai draft awal, (2) cross-check tiap klaim ke kode
  `source-codebase` (branch `migration/18.0`) aktual satu per satu di `01b_BASELINE_SPEC.md` step ini,
  (3) penyimpangan (kalau ada) dicatat eksplisit, bukan diam-diam "dikoreksi".
- [x] `01b_BASELINE_SPEC.md` — akan diisi setelah dokumen ini, sebelum step 2 mulai.

### 4a. Dokumen Pelengkap Lain

- [x] **Ditanyakan ke dev secara implisit lewat riset mandiri** (path `migration-tool-project` sudah diketahui dari konteks environment sesi ini) — ditemukan: `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md` (kandidat knowledge CAND-01..CAND-11 dari migrasi 17→18, termasuk 3 yang belum dikurasi: CAND-09/10/11) dan `MIGRATION_18_19_STATUS.md` (status lintas-repo, menyebut "finding MF-01 terbuka — dialog Choose Product Variants — perlu dicek ulang saat migrasi ke 19"; **catatan:** penomoran "MF-01" di status doc ini TIDAK ditemukan identik di `doc-dev/backfill/FINDINGS.md` (F-01..F-08) maupun `doc-dev/migration_17.0_18.0/` — kemungkinan besar merujuk ke CAND-08 di `SUMMARY.md` 17_18 (pola dua dialog terbuka bersamaan), akan dikonfirmasi ulang saat baseline spec disusun).
- [x] Kedua dokumen di atas dibaca sebelum menulis `01b_BASELINE_SPEC.md` — diperlakukan sama seperti `FUNCTIONAL_SPEC.md` (cross-check ke kode aktual, kode menang kalau menyimpang).
- [ ] **Perlu ditanya eksplisit ke dev:** ada dokumen pelengkap LAIN di luar repo (manual guide, PRD, spec Excel/Confluence/Notion, catatan requirement, dokumentasi vendor) yang sebaiknya AI baca? *(belum dijawab — dicatat sebagai pertanyaan terbuka, tidak menghalangi lanjut ke 01b karena source-of-truth utama tetap kode yang berjalan)*

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan (**dikonfirmasi eksplisit dev, 2026-08-26**)

## 5. Scope Boundary

- **Yang harus tetap identik pasca migrasi:** seluruh business logic PO (currency onchange, optional product configurator, badge harga, product list, dialog konfigurasi), termasuk bug/quirk yang sudah dikonfirmasi ada di 17.0/18.0 (F-01..F-08 backfill, CAND-08 dua-dialog).
- **Yang sengaja diubah/di-drop selama migrasi:** tidak ada yang disengaja saat ini — murni port kompatibilitas API 19.0.

## 6. Constraint

- **Deadline:** belum disebutkan dev — belum relevan/urgent, dilewati untuk sekarang.
- **Owner tiap step:** belum disebutkan dev — belum relevan/urgent, dilewati untuk sekarang.
