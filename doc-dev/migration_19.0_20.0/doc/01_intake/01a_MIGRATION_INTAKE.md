# Migration Intake — purchase_product_optional

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** Draft selesai — dilanjutkan tanpa gate interaktif atas instruksi eksplisit user
("jalan terus tanpa henti SAMPAI Step 9"), semua asumsi terbuka dicatat di "Ringkasan untuk Review"
dan `FINDINGS.md` untuk direview retroaktif.

---

## 0. Folder Referensi

**Checklist (sumber jawaban: pesan kickoff user sesi ini, 2026-09-24, + CLAUDE.md conditioning):**

- [x] `native-target` (Community 20.0) — `D:\Kuncoro\doodex\repo\odoo20` (disebut eksplisit user di
      pesan kickoff). Dicek `odoo/release.py`: `version_info = (20, 0, 0, FINAL, 0, '')`.
- [x] `native-source` (Community 19.0) — `D:\Kuncoro\doodex\repo\odoo19` (CLAUDE.md conditioning).
- [x] `native-target-enterprise` (Enterprise 20.0) — `D:\Kuncoro\doodex\repo\enterprise20` (disebut
      eksplisit user). Struktur dicek `ls`: addons-only (bukan folder gabungan). §2 auto-scan TIDAK
      menemukan dependency Enterprise; grep `enterprise20` untuk modul purchase/configurator: tidak
      ada modul yang menyentuh `purchase_product_matrix`/`PurchaseOrderLineProductField`/form PO baris
      (hanya `ai_purchase` baru di 20.0 — tidak relevan). `native-source-enterprise`:
      `D:\Kuncoro\doodex\repo\enterprise19`.
- [x] `third-party-*` — tidak ada. Scan manifest bersih; dikonfirmasi dev pada project 18→19
      (2026-08-26) dan tidak ada perubahan `depends` sejak itu (diff `migration/19.0` bersih).
      **Asumsi diwarisi** — lihat Ringkasan poin 5.

### 0a. Konfirmasi Branch/Versi

- [x] Source: branch `migration/19.0` (disebut eksplisit user: "Source branch: migration/19.0"),
      HEAD `4736c36`. Tidak ada folder `source-codebase` fisik — dibaca via `git show`/`git diff`
      (model single-repo dual-branch, CLAUDE.md §Folder).
- [x] Target: branch `migration/20.0` (disebut eksplisit user: "target branch: migration/20.0 (sudah
      dibuat saat conditioning)"), sudah checkout di folder ini. `git diff --stat migration/19.0
      migration/20.0 -- purchase_product_optional/` = kosong (kode modul identik 19.0 saat mulai).
- [x] Versi Odoo semantik: **19.0 → 20.0** — eksplisit dari user ("Lakukan migrasi 19→20").

### 0b. Gate Path Absolut `.claude/settings.json`

- [x] Tidak ada placeholder `{{ABS_PATH_...}}` literal tersisa (dicek isi file). Deny list sudah
      berisi path nyata `odoo19`, `enterprise19`, `odoo20`, `enterprise20`,
      `migration-tool/knowledge/**`, `migration-tool/templates/**`. `ABS_PATH_SOURCE_CODEBASE` N/A
      (tidak ada folder source fisik). Third-party: tidak dipakai, tidak ada barisnya.

### 0c. Pre-flight Mode Git

- [x] `.git/index.lock` tidak ada; working tree hanya berisi `.claude/skills/` (untracked, bukan
      bagian project — tidak akan di-stage).
- [ ] Pertanyaan "GUI git client sudah ditutup?" **tidak ditanyakan interaktif** (user minta tidak
      berhenti). Mitigasi: cek `index.lock` sebelum tiap commit, tidak pernah retry/unlink sendiri.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Sifat migrasi = port kode saja** (instalasi baru di 20.0, tanpa data produksi) — diwarisi dari
   17→18 dan 18→19. Step 7 N/A. *Asumsi, belum dikonfirmasi ulang di sesi ini.*
2. **Source beku** — `migration/19.0` adalah hasil akhir migrasi 18→19 yang sudah ditutup; tidak ada
   commit baru selama migrasi ini (`SYNC_POLICY.md` tidak dibuat). *Asumsi.*
3. **5 commit pasca-migrasi di branch rilis `19.0`/`staging/19.0` TIDAK di-port** (aset store:
   `banner.gif`, folder `assets`, hapus `img/`, `index.html`, fix key `images`, plus commit "cleaning"
   yang juga MENGHAPUS `tests/`). Alasan: source of truth migrasi ini adalah `migration/19.0`, dan
   commit "cleaning" bertentangan dengan kebutuhan test Step 6/9. Packaging rilis store tetap
   keputusan dev saat merge ke branch rilis 20.0. Dicatat `FINDINGS.md` MF-01.
4. **Semua bug/quirk 19.0 dipertahankan** (BSL-005 override `onchange_partner_id`, BSL-006 currency
   no-op, BSL-009 `product_add_mode`, BSL-010 multi-company, BSL-013/018 config param global, BSL-017,
   CAND-08 dua dialog) — konsisten keputusan dev 18→19.
5. **Tidak ada dependency Enterprise/OCA** — scan bersih; Enterprise 20 tetap di-connect sebagai
   referensi (sesuai CLAUDE.md). *Asumsi diwarisi.*
6. **Sudah terlihat dari riset awal: migrasi ini BUKAN port trivial** — Odoo 20.0 memakai Owl 3
   (`3.0.0-alpha.49`) + compat layer, `ir.config_parameter.get_param/set_param` dihapus, xpath list
   baris PO berubah (`<column>`), `product.template._get_attribute_exclusions`/
   `_get_first_possible_combination` kehilangan parameter `parent_combination`. Detail: Step 2.

## 1. Modul & Scope

- **Modul:** `purchase_product_optional` (satu-satunya modul di repo, subfolder `purchase_product_optional/`).
- **Fungsi:** Product Configurator (dialog "Configure your product", optional products, atribut
  no-variant/custom/dynamic, extra price) di baris Purchase Order, dengan harga per-vendor
  (`product.supplierinfo`) + konversi currency lewat `ir.config_parameter` global; override onchange
  partner/currency di PO.
- **Saling depend:** N/A (satu modul).

## 2. Dependency Map (auto-scan `__manifest__.py` 19.0)

| Dependency | Tipe | Tersedia di 20.0? | Catatan |
|---|---|---|---|
| `purchase` | Native Community | Ya — `odoo20/addons/purchase` | Form PO berubah struktur (`<column name="product_and_description">`), field UoM POL `uom_id` |
| `purchase_product_matrix` | Native Community (LGPL-3, dicek ulang manifest 20.0) | Ya — `odoo20/addons/purchase_product_matrix`, `depends: purchase, product_matrix` | `PurchaseOrderLineProductField` sekarang extends `AccountProductField`; view matrix pindah ke dalam `<column>` |
| `sale` | Native Community | Ya | Kembaran native configurator (`sale/static/src/js/product_configurator_dialog`) sudah di-port ke Owl 3 — dipakai sebagai referensi pola |

Dependency opsional runtime: grep `models/*.py` — tidak ada `'x' in self.env`/`self.env[var]`.
Dependency implisit ke `product_matrix` (JS `@product_matrix/js/matrix_configurator_hook`) —
terpenuhi transitif lewat `purchase_product_matrix`.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada? | Lokasi | Fase step 6 |
|---|---|---|---|
| Controllers | ☑ Ya | `controllers/main.py` (4 route `type='jsonrpc'`) | D1 |
| Assets/CSS/JS | ☑ Ya | `static/src/**` (`web.assets_backend`), `static/tests/tours/**` (`web.assets_tests`) | D2, E, F |
| Komponen Owl | ☑ Ya | 5 komponen + `patch()` `PurchaseOrderLineProductField` | E, F |
| Field JSON / relasi berantai / `self.env[var]` | ☐ Tidak | — | B2 → N/A |
| `attrs=`/`states=`/domain dinamis di view | ☐ Tidak | `views/purchase_order_views.xml` bersih | C2 → N/A |

Test suite: `tests/test_purchase_product_optional.py` (13 test Python: unit + HttpCase route),
`tests/test_purchase_product_optional_tour.py` + `static/tests/tours/purchase_product_optional_tour.js`
(Tour 15 langkah) — dibuat proses BACKFILL, lokasi SAMA dengan kode source (branch `migration/19.0`).

## 3. Sifat Migrasi

- [x] Port kode saja (asumsi diwarisi, lihat Ringkasan poin 1)
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test

- [x] Spec lama ada: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (17.0),
      `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (basis 18.0, dipakai sebagai
      draft) → cross-check ulang ke kode `migration/19.0` di `01b_BASELINE_SPEC.md` step ini.
- [x] Test lama: ADA, lokasi SAMA dengan source (`purchase_product_optional/tests/` di
      `migration/19.0`, asal BACKFILL). Hasil eksekusi terakhir di 19.0: 13/13 pass + Tour sukses
      (`migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md` §Metrik).
- [x] `01b_BASELINE_SPEC.md` diisi (lihat file itu).

### 4a. Dokumen Pelengkap

- [x] Dibaca: `doc-dev/backfill/FINDINGS.md` (F-01..F-08), migration record 17_18 (CAND-01..11) dan
      18.0_19.0 (CAND-01..04), `doc-dev/migration_18.0_19.0/doc/` (intake, baseline, diff, AC, UAT).
- [ ] Dokumen di luar repo (PRD/manual) — tidak ditanyakan interaktif; tidak ada yang pernah disebut
      di project 17→18/18→19. Dianggap tidak ada (asumsi).

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak (asumsi — lihat Ringkasan poin 2).

## 5. Scope Boundary

- **Harus identik:** seluruh perilaku 19.0 (`01b_BASELINE_SPEC.md` BSL-001..BSL-026), termasuk quirk.
- **Sengaja diubah/di-drop:** tidak ada yang disengaja. Satu perilaku yang **terpaksa hilang karena
  platform 20.0** (bukan pilihan): eksklusi atribut lintas-produk (parent exclusions, BSL-020) — model
  data `product.template.attribute.exclusion` dihapus di 20.0, lihat Step 2 DIFF-06 / MF-03.

## 6. Constraint

- Deadline/owner: belum disebut — belum relevan, dilewati.
- Constraint operasional dari user: **STOP wajib sebelum Step 10** (slot QA browser dibatasi, MF-46
  lintas repo); saat ini container `pos_margin_sale_migration_20` jalan di port 8078/8182 — project ini
  memakai project name & port berbeda (8201) untuk menghindari bentrok.
