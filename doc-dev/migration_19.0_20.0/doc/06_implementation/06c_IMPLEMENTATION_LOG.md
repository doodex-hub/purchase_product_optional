# Implementation Log — purchase_product_optional

**Step:** 6 — Code Migration (19.0 → 20.0)
**Tanggal:** 2026-09-24
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `02_diff/02_DIFF_ANALYSIS.md`, template `06a_CODE_MIGRATION_PHASES.md`
**Environment:** Claude Code CLI, Mode C (AI jalankan Docker langsung) + Mode D (Tour headless Chrome).
Odoo 20.0 build-from-source: `docker-env/Dockerfile` (`python:3.12-slim-bookworm` + requirements
`odoo20` + `google-chrome-stable`), `odoo20` di-mount read-only `/opt/odoo`, Postgres 16, project name
`purchase_product_optional_migration_20`, port 8201. Runner: `docker-env/run-test.sh` (selalu
`down -v`, `MSYS_NO_PATHCONV=1`, sanity check jumlah test "Starting").

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (`01a` §2b) |
|---|---|---|
| A2 Tree→List | ☐ Tidak | Tidak ada `<tree>` (sudah `<list>` sejak 17→18) |
| A3 Security | ☐ Tidak | Modul tidak punya `security/`/ACL (tidak menambah model baru) |
| B2 | ☐ Tidak | Tidak ada JSON field/relasi berantai/`self.env[var]` |
| C1 | ☑ Ya | xpath list baris PO (DIFF-17) |
| C2 | ☐ Tidak | Tidak ada `attrs`/domain dinamis |
| D1 | ☑ Ya | `controllers/main.py` (DIFF-11) |
| D2 | ☐ Tidak | SCSS/glob aset tidak perlu berubah (DIFF-19) |
| E | ☑ Ya | 6 file `.js` (DIFF-01/02/04/05/06) |
| F | ☑ Ya | 5 file template `.xml` (DIFF-03) |

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ `version` → `20.0.1.0.0` | 2026-09-24 |
| A2 | N/A | |
| G1 #1 | ❌ Fail (diharapkan — DIFF-17 terbukti) | 2026-09-24 |
| A3 | N/A | |
| A4 | ✅ Struktur folder utuh (tidak ada perubahan) | 2026-09-24 |
| A5 | ✅ `get_param`/`set_param` → `get_int`/`set_int` | 2026-09-24 |
| B1 | ✅ `purchase_order_line.py` dicek — tidak perlu perubahan | 2026-09-24 |
| B2 | N/A | |
| C1 | ✅ xpath `<column>` | 2026-09-24 |
| C2 | N/A | |
| D1 | ✅ `parent_combination` dihapus dari 3 panggilan native, `parent_exclusions={}` | 2026-09-24 |
| G1 #2 | ✅ Pass | 2026-09-24 |
| D2 | N/A | |
| E | ✅ Selesai penuh sebelum F | 2026-09-24 |
| F | ✅ | 2026-09-24 |
| G2 | ✅ 21/21 test, Tour 15/15 `tour succeeded` (Owl dev mode) | 2026-09-24 |

## Riwayat Percobaan G1 (Install Test)

| # | Setelah fase | Mode | Hasil | Error | Log |
|---|---|---|---|---|---|
| 1 | A1 (A2/A3 N/A) | C | ❌ Fail (expected) | `Element '<xpath expr="//list/field[@name='product_template_id']">' cannot be located in parent view` | `docker-env/logs/g1-a1.log` (gitignored) |
| 2 | A5 + B1 + C1 + D1 | C | ✅ Pass | — (warning baseline saja: `unknown parameter 'product_add_mode'` BSL-009, `Two fields (id_vendor, id) ... same label: ID` BSL-017 — identik 19.0) | `docker-env/logs/g1-cd.log` |

> Catatan disiplin fase: G1 setelah A2/A3 tidak bermakna terpisah karena keduanya N/A; blocker install
> modul ini ada di C1 (view), jadi G1 kedua dijalankan setelah C1/D1.

---

## Entri

### [A1] Manifest
- `__manifest__.py`: `'version': '19.0.1.0.0'` → `'20.0.1.0.0'`. Key lain (termasuk `images`) tidak
  disentuh (MF-01).

### [A5] Python API — `ir.config_parameter` (DIFF-10)
- `models/purchase_order.py` `onchange_partner_id`: 3× `.sudo().set_param` → `.sudo().set_int`
  (nama variabel lokal `set_param` dibiarkan — minimal diff). Tidak ada `super()` ditambahkan (BSL-005).
- `models/product_template.py` `convert_price`: `.sudo().get_param` → `.sudo().get_int`,
  `int(get_param('currency_id'))` → `get_param('currency_id')` (get_int sudah mengembalikan int,
  default 0 = setara `int(False)`).

### [C1] View (DIFF-17)
- `//list/field[@name='product_template_id']` (attributes) → `//list//field[...]`.
- Field tersembunyi (4 + subview) dipindah dari "after `product_template_id`" ke
  `//list/column[@name='product_and_description']` `position="after"` — `<column>` merender semua
  field anaknya dalam satu sel dan mengabaikan `column_invisible` per field (list_arch_parser.js 20.0).
- `//list/field[@name='product_id']` → `//list//field[@name='product_id']`.
- `currency_id` / `form` xpath tidak diubah.

### [D1] Controller (DIFF-11, MF-03)
- `get_values_purchase` & `get_optional_products`: `_get_first_possible_combination(parent_combination=…)`
  → `_get_first_possible_combination()`.
- `_get_product_information_purchase`: `_get_attribute_exclusions(parent_combination=…,
  combination_ids=…)` → `_get_attribute_exclusions(combination_ids=…)`; `parent_exclusions={}`.
- Parameter/argumen `parent_combination` di route & helper dipertahankan (payload JS tidak berubah).

### [E] JavaScript (Owl 3)
- `purchase_product_field.js`: import `x2ManyCommands` dari `@web/core/orm_plugin` (DIFF-06).
- `product_configurator_dialog.js`: `useSubEnv` dari `@web/owl2/utils`; `useState` → `proxy`;
  `static props` + `static defaultProps` → `props = useProps({... edit: t.boolean().optional(false) ...})`.
- `product_list.js`: `useProps({products: t.array(), areProductsOptional: t.boolean().optional(false)})`.
- `product.js`, `product_template_attribute_line.js`, `badge_extra_price.js`: `static props` →
  `props = useProps({...})` setara 1:1 (tipe `Object` yang faktanya array → `t.array()`; validator
  `display_type`/`create_variant` → `t.customValidator`, daftar nilai tidak diubah).
- Tidak ada perubahan logika method.

### [F] Template (DIFF-03)
- Prefix `this.` untuk semua member komponen di 5 template (daftar lengkap di diff commit). Quirk
  dipertahankan: `this.hasPTAVCustom && …` (tanpa `()`), `size="this.size"` (tetap `undefined`).
- Audit akhir: semua ekspresi `t-*` & prop komponen tersisa hanya merujuk `this.*`, variabel loop
  (`ptal`, `ptav`, `product`) atau `t-set` lokal.

### [G2] Validasi akhir — test yang disesuaikan/ditambah
- Tour: hapus `test: true` (registry strict, DIFF-09); tombol tambah baris `.o_field_x2many_list_row_add >
  button:contains("Add a product")` (20.0 render `<button>`).
- `TestConvertPrice`: `set_param(..., str(id))` → `set_int(..., id)` (asersi tidak diubah).
- Test baru (menutup jalur breaking & gap lama): `test_onchange_stores_currency_param`,
  `test_id_vendor_label`, `test_simple_product_single_variant_no_configurator`,
  `test_get_optional_products_route`, `test_update_combination_route`,
  `test_get_values_purchase_same_template_exclusions`; asersi `parent_exclusions == {}` di
  `test_get_values_purchase_returns_optional_product`.
- Hasil: `0 failed, 0 error(s) of 21 tests`; Tour `purchase_product_optional_configurator_tour`
  15/15 `tour succeeded`, log browser "Owl is running in 'dev' mode" (validasi schema `useProps` aktif
  dan lolos). Log: `docker-env/logs/g2-run1.out`.

## Temuan di Luar Spec

- `matrixConfigurator.open(record, false)` native menghapus baris PO baru (`order_line.delete(record)`)
  — relevan untuk CAND-08 (dua dialog, template configurable): dialog modul lalu bekerja atas record
  yang sudah dihapus. Perilaku warisan (identik 19.0 secara kode), karakterisasi live dijadwalkan
  Step 10 (skenario "hanya satu dialog disentuh"). Dicatat `FINDINGS.md` MF-04.

## Kontribusi ke Knowledge Base

Kandidat CAND-01..06 di `migration-tool/migration-records/purchase_product_optional_19.0_20.0/SUMMARY.md`.
