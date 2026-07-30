# Migration Intake — purchase_product_optional

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-07-29
**Status:** 🔄 Draft — menunggu review user

---

## Ringkasan untuk Review — Perlu Konfirmasi User

> Ini satu-satunya bagian yang perlu benar-benar dibaca sebelum gate step 1 ditutup.

1. **Sumber baseline bukan `FUNCTIONAL_SPEC.md` konvensional, tapi hasil project BACKFILL sebelumnya**
   (`doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` + `FINDINGS.md`,
   ditulis 2026-07-28, semua klaim sudah dikonfirmasi lewat eksekusi nyata Mode B + AI-Browser).
   Dipakai sebagai "spec lama" per §4 di bawah — cross-check terhadap kode langsung sudah dilakukan,
   **semua klaim cocok** (tag `[MATCH]` di `01b_BASELINE_SPEC.md`). Konfirmasi: setuju dokumen ini
   dipakai sebagai dasar baseline, bukan direkonstruksi dari nol?
2. **6 bug/quirk terdokumentasi (F-01..F-06) WAJIB dipertahankan identik di 18.0** — bukan diperbaiki.
   Yang paling berisiko kalau salah paham: **F-06** (dua dialog "Configure your product" vs "Choose
   Product Variants" tumpang tindih, bisa menghilangkan baris produk utama tanpa error) dan **F-03**
   (currency PO disimpan ke `ir.config_parameter` GLOBAL, rawan race condition multi-user). Konfirmasi:
   setuju SEMUA F-01..F-06 dipertahankan apa adanya (bukan kesempatan untuk sekalian diperbaiki)?
3. **Blocker install kritis sudah ditemukan sejak step 1:** `views/purchase_order_views.xml` pakai
   `<tree>` (2× xpath target, 1× inner tree) — ini **install-breaking** di 18.0 per
   `knowledge/version-diffs/17-to-18.md` §1 (`ParseError: Invalid view type: 'tree'`). Akan jadi fokus
   Fase A2 di step 6, tidak perlu keputusan sekarang, cuma diberitahukan supaya tidak jadi kejutan.
4. **Owl/JS modul ini sudah dalam bentuk modern** (ES6 class, `@odoo-module`, flat import dari
   `@odoo/owl`, `t-on-click`) — BUKAN pola classic (`Component.extend()`, `odoo.define`) yang jadi
   fokus utama gotcha di `knowledge/version-diffs/17-to-18.md` §1b. Migrasi Fase E/F kemungkinan lebih
   ringan dari worst-case yang terdokumentasi, tapi tetap dikerjakan penuh di step 6 (tujuan utama
   Test 2b) — bukan diasumsikan "sudah beres" tanpa verifikasi. Tidak butuh keputusan, sekadar
   ekspektasi awal.
5. **Dependency (`purchase`, `purchase_product_matrix`, `sale_product_configurator`) semuanya native/Enterprise Odoo, tidak ada OCA/third-party** — `third-party-source`/`third-party-target` tidak perlu di-connect. Setuju?
6. **Constraint (deadline, owner per step) belum ada nilainya** — belum relevan/tidak urgent untuk test project ini (Test 2b, tujuan validasi tool), dilewati kecuali user ingin isi.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `purchase_product_optional` (single module, tidak multi-module)
- Deskripsi singkat fungsi modul: menambahkan Product Configurator (dialog pilih atribut + optional
  products, meminjam konsep `sale_product_configurator`) ke form Purchase Order — memungkinkan staff
  purchasing memilih varian/atribut produk dan optional products langsung dari baris PO, dengan harga
  mengikuti vendor yang dipilih (`product.supplierinfo`) dan konversi currency ke currency PO.
- Apakah modul ini depend ke modul custom lain: Tidak — semua dependency adalah modul native/Enterprise
  Odoo stok (`purchase`, `purchase_product_matrix`, `sale_product_configurator`).

## 2. Dependency Map (auto-scan dari `__manifest__.py`)

| Dependency | Tipe (native/OCA/custom) | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `purchase` | Native (Community) | Asumsi ya (core Odoo 18.0) | Belum dikonfirmasi lewat `native-target` — belum di-connect, minta kalau step 2 butuh cross-check API detail |
| `purchase_product_matrix` | Native, **Community (LGPL-3)** — dikoreksi Step 2, bukan Enterprise seperti dugaan awal | Ya, ada di 18.0 (dikonfirmasi `native-target`) | Modul ini di-patch (`purchase_product_field.js` patch `PurchaseOrderLineProductField`) — **perubahan struktur besar di 18.0**, lihat `02_DIFF_ANALYSIS.md` DIFF-04/DIFF-05 |
| `sale_product_configurator` | Native/Enterprise (17.0) | **TIDAK ADA di 18.0** — modul dihapus total, fungsinya pindah ke `product`/`sale` Community (dikonfirmasi `native-target`) | **Install-breaking**, lihat `02_DIFF_ANALYSIS.md` DIFF-02/DIFF-03 — wajib diubah di manifest Fase A1 |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak ditemukan, digrep
seluruh modul: tidak ada pengecekan model optional runtime.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 yang jadi relevan |
|---|---|---|---|
| Controllers (route custom) | ☑ Ya | `controllers/main.py` (342 baris, 4 route JSON: `get_values_purchase`, `create_product`, `update_combination`, `get_optional_products`) | D1 |
| Assets/CSS/JS custom | ☑ Ya | `static/src/**` (6 folder JS + 2 `.scss`), key `assets` di manifest (`web.assets_backend` + `web.qunit_suite_tests`/`web.assets_tests` hasil BACKFILL) | D2, E, F |
| Komponen Owl/JavaScript custom | ☑ Ya | 5 komponen: `Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice` (`static/src/js/`), `ProductConfiguratorDialogPurchase` (567 baris, terbesar) + patch `PurchaseOrderLineProductField` (`purchase_product_field.js`, 154 baris) | E, F |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Relasi yang ada (`product_custom_attribute_value_ids` One2many, `product_no_variant_attribute_value_ids` Many2many) semuanya 1 level, tidak ada field JSON, tidak ada `self.env[var]` digrep di seluruh modul | B2 → **N/A** |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ Tidak | `views/purchase_order_views.xml` (40 baris) cuma pakai atribut statis (`column_invisible="0"/"1"`, `optional="hide"`) — tidak ada domain/context/attrs berbasis ekspresi Python | C2 → **N/A** |

**Catatan tambahan (bukan bagian tabel wajib, tapi penting untuk step 6):** `views/purchase_order_views.xml`
memakai tag `<tree>` (xpath target `//tree/field[...]` 2×, inner `<tree>` untuk
`product_custom_attribute_value_ids` 1×) — ini bukan soal "attrs/domain dinamis" (C2, tetap N/A), tapi
soal tipe view lama (**A2 — Tree→List, mekanis**), sudah dikonfirmasi jadi blocker install kritis di
18.0 per `knowledge/version-diffs/17-to-18.md` §1.

Kalau §Applicability Check step 6 (`06a_CODE_MIGRATION_PHASES.md`) dijalankan: **B2 dan C2 langsung
N/A** (declared, tidak perlu entry penuh). **D1, D2, E, F semuanya relevan** — ini modul kandidat
utama Test 2b, wajib dikerjakan penuh, bukan di-skip.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi — step 7 Data Migration Scripts wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Tidak dalam
  bentuk konvensional**, TAPI ada padanan yang setara/lebih kuat: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`
  + `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md` + `doc-dev/backfill/FINDINGS.md`, hasil project
  BACKFILL retroaktif terpisah (2026-07-28) yang SUDAH divalidasi lewat eksekusi nyata (Mode B: 11/11
  test Python pass; AI-Browser: 5 skenario live). Lokasi: `doc-dev/backfill/spec/` (di root
  `target-codebase`, karena `target-codebase` ternyata clone dari commit yang sama dengan
  `source-codebase` — lihat catatan struktural di
  `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`).
  - **Proses yang dilakukan** (sesuai §4 ini): (1) baca `01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md`
    sebagai draft awal, (2) cross-check tiap klaim (BR-01..BR-09, AC-01..AC-09) terhadap kode aktual
    di `purchase-product-optional/purchase_product_optional/` (models, controllers, 6 file JS, view)
    dibaca langsung baris per baris, (3) **semua klaim cocok** — tidak ditemukan penyimpangan antara
    spec BACKFILL dan kode aktual. Hasil: `01b_BASELINE_SPEC.md` diisi dengan tag `[MATCH]` di semua
    `BSL-NNN`, mereferensikan `BR-NNN`/`AC-NN-NN` asal.
- [x] `01b_BASELINE_SPEC.md` sudah diisi (baca kode source module langsung — model, field, workflow,
  side effect, client behavior), termasuk section "Ringkasan untuk Review" dan ID `BSL-NNN` di tiap
  klaim behavior.

**Tidak boleh lanjut ke step 2 sebelum `01b_BASELINE_SPEC.md` terisi.** ✅ Terisi — lihat file terpisah.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module (`purchase-product-optional`) dibekukan selama migrasi berjalan
  (dikonfirmasi user 2026-07-29). `SYNC_POLICY.md`/`SYNC_LOG.md` tidak dibuat.
- [ ] Ya — source module terus menerima perubahan/fitur baru selama migrasi.

## 5. Scope Boundary

- **Yang harus tetap identik pasca migrasi:**
  - Seluruh business rule BR-01..BR-09 (lihat `01b_BASELINE_SPEC.md`), termasuk 6 bug/quirk F-01..F-06
    yang SUDAH terdokumentasi (`doc-dev/backfill/FINDINGS.md`) — dipertahankan apa adanya, bukan
    diperbaiki sebagai bagian migrasi ini.
  - Seluruh 4 endpoint controller (`get_values_purchase`, `create_product`, `update_combination`,
    `get_optional_products`) — signature & response shape sama persis.
  - Seluruh 5 komponen Owl (behavior, props, state) — rewrite ke Owl 18.0 kalau memang ada breaking
    change API, tapi HASIL AKHIR (apa yang user lihat & lakukan) harus identik.
  - View form PO: kolom `product_template_id` selalu terlihat, `product_id` disembunyikan default +
    label "Product Variant", field `id_vendor` tersembunyi visual (CSS) tapi tetap ada di DOM (dipakai
    F-04, dipertahankan meski rapuh).
- **Yang sengaja diubah/di-drop selama migrasi:**
  - `<tree>` → `<list>` di `views/purchase_order_views.xml` (WAJIB untuk instalasi 18.0, bukan pilihan
    — lihat `knowledge/version-diffs/17-to-18.md` §1). Ini perubahan MEKANIS (tag/xpath saja), TIDAK
    mengubah field/domain/context/business logic apapun di dalamnya.
  - Kalau ada breaking change Owl API 18.0 yang memaksa perubahan sintaks (bukan behavior) — akan
    dicatat eksplisit satu per satu di step 6, bukan diam-diam.
  - Tidak ada fitur yang sengaja di-drop.

## 6. Constraint

- Deadline: belum relevan — project ini (Test 2b) bertujuan validasi tool `migration-tool`, bukan
  deliverable produksi dengan tenggat.
- Owner tiap step (Dev/QA/PM/FA): belum relevan — dikerjakan single-person (Kuncoro) sebagai bagian
  validasi Fase 3 `migration-tool/ai-doc/ROADMAP.md`.
