# Business Flow — Migrasi purchase_product_optional

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `../CROSS_VERSION_COMPARE.md`
**Tanggal:** 2026-09-24

> Port kode saja (tanpa data produksi) → install bersih + data seed identik di 19.0 dan 20.0.
> **Mode eksekusi:** AI-interaktif via **Playwright MCP headless** (CLI default) terhadap dua server
> hidup berdampingan — 20.0 `http://127.0.0.1:8201` (branch `migration/20.0`, Odoo 20 from source +
> Enterprise 20) dan 19.0 `http://localhost:8202` (worktree `migration/19.0`, image 19.0 + Enterprise 19).
> Keduanya meng-install `purchase_product_optional, account_budget_purchase, purchase_quality_control`
> (MF-05: instance produksi bisa Enterprise). Seed: `QA Vendor A/B`, `QA Main Product` (supplierinfo A=80,
> B=90, std 100) dengan optional `QA Optional Product` (A=40, std 50), `QA Exclusion Product` (Small ⟂
> Matte), `QA Types Product` (select/pills(+5)/color/multi/custom); `QA Configurable Product` (2 varian).
> Semua langkah dijalankan dengan skrip Playwright yang SAMA di kedua versi. Screenshot:
> `screenshots/{19,20}/`.

---

## Skenario

- [x] Skenario dari AC risiko tinggi — S-01..S-09.
- [x] **Cross-Version Compare** — WAJIB (dependency Enterprise di produksi + area risiko tinggi Owl 3);
      dijalankan, lihat `../CROSS_VERSION_COMPARE.md` (RMV-01..05).
- [ ] Spot-check integritas data — N/A (Step 7 N/A, port kode saja).
- [x] **Multi-dialog dari satu aksi** — ada (template configurable → grid matrix + configurator): S-06.

### S-01: Dialog configurator terbuka otomatis
**Level:** Smoke
**Precondition:** PO baru, vendor QA Vendor A.
**Mode eksekusi:** AI-interaktif (Playwright) + Tour Step 9.
**Steps:** Add a product → ketik & pilih "QA Main Product".
**Expected:** dialog "Configure your product" dengan produk utama + "Add optional products" (3 optional).
**Actual:** 19 dan 20 identik; tanpa error console.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-02: Harga per vendor di dialog
**Level:** Main Flow
**Precondition:** seed harga di atas.
**Mode eksekusi:** AI-interaktif.
**Steps:** S-01 dengan Vendor A, lalu ulang dengan Vendor B; baca harga produk utama & optional.
**Expected (19.0):** A: main 80, optional 40; B: main 90, optional 50 (fallback `standard_price`).
**Actual:** 20 = 19 (A: $80/$40, B: $90/$50; QA Exclusion Product $0.00 di keduanya — RMV-05).
Visual pass menemukan ikon −/+ dan "+ Add" KOSONG di 20.0 → **RMV-02 REGRESI, sudah difix**
(`screenshots/20/s02_vendorA.png` sebelum, `s02_icons_fixed.png` sesudah).
**Status:** [x] Pass (setelah fix RMV-02)
**Provenance:** [DIKONFIRMASI]

### S-03: Tambah optional, Confirm, Save
**Level:** Main Flow
**Mode eksekusi:** AI-interaktif + Tour Step 9.
**Steps:** S-01 → Add "QA Optional Product" → Confirm → Save.
**Expected:** Total dialog $120; 2 baris PO (main $80, optional $40, qty 1); PO tersimpan (nomor P000xx).
**Actual:** 20 = 19.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-04: Eksklusi atribut dalam satu produk
**Level:** Detail
**Steps:** di baris "QA Exclusion Product" (default Small, Glossy) pilih Matte, lalu Large.
**Expected (19.0):** awal Matte tidak tersedia; pilih Matte → Small+Matte tidak tersedia, pesan "This
option or combination of options is not available", tombol Add disabled; pilih Large → valid, judul
"(Large, Matte)".
**Actual:** 20 = 19 persis.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-05: Harga tertimpa `standard_price` setelah ganti atribut (quirk BSL-028)
**Level:** Detail
**Steps:** —
**Expected:** harga baris jadi `standard_price` variant.
**Actual:** tidak teramati visual (variant seed ber-`standard_price` 0 → $0.00 sebelum & sesudah, sama
di 19/20). Jalur server dibuktikan `test_update_combination_route` (price = standard_price).
**Status:** [x] Pass
**Provenance:** [HASIL-BACA — ref: Step 9, AC-02-03 `test_update_combination_route`]

### S-06: Template configurable — dua dialog, user hanya menyentuh satu
**Level:** Negative
**Steps:** pilih "QA Configurable Product" → amati → isi grid matrix (qty) → Confirm → lalu dialog
configurator tersisa: (a) Cancel, (b) ✕, (c) Confirm → Save.
**Expected (19.0):** dua dialog (configurator di BELAKANG grid, tidak bisa diklik); baris baru dihapus
native matrix; setelah grid Confirm baris dari grid muncul; (a) Cancel → Save gagal "Oops!" (id
`virtual_NN`); (b)/(c) → Save sukses, satu baris.
**Actual:** 20 = 19 untuk semua sub-kasus (19: `virtual_26`, 20: `virtual_34`). Beda hanya judul dialog
grid (19 "Choose Product Variants", 20 nama produk — native) dan 2 `console.error` "Component is
destroyed" di 20 (RMV-01, tanpa dampak fungsional).
**Status:** [x] Pass (paritas dengan 19.0 — bug (a) adalah GAP-LAMA RMV-03, dipertahankan)
**Provenance:** [DIKONFIRMASI]

### S-07: Edit ulang baris configurable tersimpan (T-03)
**Level:** Detail
**Steps:** buka PO tersimpan dengan baris configurable → klik sel produk → tombol edit → amati →
tutup grid (✕) → Cancel configurator → Save.
**Expected (19.0):** grid (mode edit) + configurator mode edit dengan nilai tersimpan (Red) terpilih;
Cancel hanya menutup; baris tetap; Save sukses.
**Actual:** 20 = 19; 0 error console. **Menutup gap T-03 yang tidak pernah punya evidence sejak 18→19.**
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-08: Cancel dialog baru menghapus baris
**Level:** Negative
**Steps:** S-01 (Vendor B) → Cancel.
**Expected:** dialog tertutup, baris PO baru hilang (0 baris).
**Actual:** 20 = 19.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-09: Semua tipe atribut + custom value
**Level:** Detail
**Steps:** S-01 → Add "QA Types Product" → select "Sel Two", pills "Pill B" (+$5 badge), color Green,
multi X+Y, radio "Custom" + isi "Hello QA" → Confirm → Save; baca baris via ORM.
**Expected (19.0):** semua tipe ter-render & bisa dipilih, badge "+$ 5.00"; baris optional $20, 1 custom
value tersimpan, 0 no-variant value tersimpan.
**Actual:** render & data 20 = 19 (termasuk 0 no-variant — RMV-05 GAP-LAMA). Beda: `purchase.order.line.name`
kosong di 20 vs nama produk di 19 — model native 20 (`name` = deskripsi tambahan, nama tampil via `label`),
RMV-04 NATIVE-DIFF.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03 | 2 |
| Detail | S-04, S-05, S-07, S-09 | 4 |
| Negative | S-06, S-08 | 2 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 8 | S-01, S-02, S-03, S-04, S-06, S-07, S-08, S-09 |
| `[HASIL-BACA]` | 1 | S-05 (ref Step 9) |
| `[HASIL-BACA-MURNI]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Human QA Checklists

Digenerate di `human_qa/` (00_README + 4 level).

## Loop-back

- RMV-02 (ikon Font Awesome) → fix `static/src/js/product/product.xml` (`fa fa-*` → `oi` + `data-icon`),
  asersi ditambahkan ke Tour (`i.oi[data-icon="add"]`), Step 9 di-rerun Community + Enterprise (lihat
  `09_DEV_TESTING.md` §Rerun Step 10).
- Perubahan tour sebelumnya (Enterprise home menu → `stepUtils.showAppsMenuItem()`), rerun sama.

## Verdict

- [x] ✅ Lulus — semua skenario `[DIKONFIRMASI]`/`[HASIL-BACA]`, 1 regresi ditemukan & difix (RMV-02),
  sisa perbedaan = NATIVE-DIFF atau GAP-LAMA yang identik dengan 19.0.
