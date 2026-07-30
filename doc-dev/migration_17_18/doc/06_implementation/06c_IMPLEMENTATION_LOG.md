# Implementation Log — purchase_product_optional

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-07-29

> Jejak per FASE (A1→G2), bukan cuma per item spec. Kalau ketemu sesuatu di luar spec — STOP,
> jangan improvisasi. Balik ke step 3/4 dulu.

---

## Aturan

1. **Append only** — jangan edit entry lama.
2. **Satu bagian per fase.**
3. **Faktual** — deskripsikan apa yang dilakukan, bukan kenapa (kecuali merujuk aturan/spec).
4. **Tertelusuri** — rujuk `03_MIGRATION_SPEC.md` atau `06a_CODE_MIGRATION_PHASES.md` kalau relevan.
5. **Pengecualian eksplisit** — WAJIB sebutkan apa yang SENGAJA TIDAK diubah di tiap entry.

---

## Applicability Check

> Diambil dari `01_intake/01a_MIGRATION_INTAKE.md` §2b (sudah dikonfirmasi di step 1, bukan tebakan
> baru).

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 | ☐ Ya / ☑ Tidak | Tidak ada field JSON, relasi berantai >2 level, atau `self.env[var]` dynamic — semua relasi 1 level (`product_custom_attribute_value_ids`, `product_no_variant_attribute_value_ids`) |
| C2 | ☐ Ya / ☑ Tidak | `views/purchase_order_views.xml` cuma pakai atribut statis (`column_invisible="0"/"1"`, `optional="hide"`) — tidak ada domain/context/attrs dinamis |
| D1 | ☑ Ya / ☐ Tidak | `controllers/main.py`, 4 route JSON (`get_values_purchase`, `create_product`, `update_combination`, `get_optional_products`) |
| D2 | ☑ Ya / ☐ Tidak | `static/src/**` — 6 folder JS + 2 `.scss`, key `assets` manifest (`web.assets_backend` + test bundles) |
| E | ☑ Ya / ☐ Tidak | 5 komponen Owl + patch `PurchaseOrderLineProductField` (`purchase_product_field.js`) — modul kandidat utama Test 2b |
| F | ☑ Ya / ☐ Tidak | Menyusul E (template Owl dari 5 komponen + patch di atas) |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-07-29 |
| A2 | ✅ | 2026-07-29 |
| G1 (checkpoint Fase A — lihat tabel "Riwayat Percobaan G1" di bawah) | ✅ Pass | 2026-07-29 |
| A3 | N/A — dikonfirmasi Applicability Check (modul tidak punya folder `security/`, tidak mendefinisikan model/TransientModel baru — lihat `04_SPEC_COMPLETENESS_REVIEW.md`) | 2026-07-29 |
| A4 | ✅ | 2026-07-29 |
| A5 | ✅ | 2026-07-29 |
| B1 | ✅ | 2026-07-29 |
| B2 | N/A — dikonfirmasi Applicability Check | 2026-07-29 |
| C1 | ✅ | 2026-07-29 |
| C2 | N/A — dikonfirmasi Applicability Check | 2026-07-29 |
| D1 | ✅ (struktural; verifikasi signature runtime dilimpahkan ke G2/step 9) | 2026-07-29 |
| D2 | ✅ (struktural; verifikasi compile SCSS runtime dilimpahkan ke G2) | 2026-07-29 |
| E | ✅ (JS bundling/browser-load dilimpahkan ke G2 — G2 menemukan 1 bug tambahan, MF-13, sudah diperbaiki) | 2026-07-29 |
| F | ✅ | 2026-07-29 |
| A1 (revisi) | ✅ — `depends` ditambah `'sale'` (MF-14, eskalasi user) | 2026-07-29 |
| G2 (validasi akhir/runtime) | ✅ Selesai — MF-13/MF-14 resolved & terverifikasi; F-06/MF-06 dikonfirmasi identik | 2026-07-29 |

## Riwayat Percobaan G1 (Install Test)

> **Mode eksekusi:** A = manual dev sendiri, B = container disiapkan AI/dev jalankan, C = AI
> jalankan langsung (hanya environment shell persisten, BUKAN Cowork).
>
> **Mode B dipilih user (2026-07-29).** `docker-env/docker-compose.yml` + `docker-env/Dockerfile`
> sudah di-rework untuk 18.0 (instance BARU, terpisah dari instance BACKFILL 17.0 — lihat komentar
> di kedua file). Penamaan unik disengaja (permintaan eksplisit user, khawatir konflik dengan task
> lain): `name: purchase_product_optional_18`, port host `8081` (beda dari instance 17.0 di 8079),
> database `purchase_product_optional_18_install`. **Belum dieksekusi** — menunggu dev jalankan
> command di bawah.

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A2 | B | ✅ Pass | — (3 percobaan build gagal duluan sebelum run ini, lihat catatan di bawah) | 2026-07-29 |
| 2 | A3 | — | N/A — A3 tidak relevan (lihat Applicability/tabel status), run #1 sudah representasikan install bersih total | | 2026-07-29 |

**Detail run #1 (PASS):**
- `51 modules loaded in 32.03s ... Modules loaded.` — tidak ada `CRITICAL`/`ERROR`/`Traceback`.
- 2 percobaan build sebelumnya GAGAL sebelum sampai ke run install (bukan kegagalan modul, murni
  environment Docker): (a) `pip3 install websocket-client` exit code 1 di image `odoo:18.0` — beda
  dari `odoo:17.0` (BACKFILL), base image 18.0 kemungkinan menegakkan PEP 668
  `externally-managed-environment`; fix: `--break-system-packages` dengan fallback (lihat
  `Dockerfile`). (b) Port host `8081` sudah dipakai proses lain di komputer dev; fix: pindah ke
  `8082` (lihat `docker-compose.yml`).
- 3 WARNING muncul, semua expected/non-fatal:
  1. `product_no_variant_attribute_value_ids: unknown parameter 'product_add_mode'` — **konfirmasi
     langsung MF-01/BSL-008 tetap identik di 18.0** (bug warisan, bukan regresi).
  2. Sama seperti #1, muncul 2× (saat load + saat compute ulang).
  3. `Two fields (id_vendor, id) ... same label: ID` — **temuan BARU**, dicatat `MF-12` di
     `FINDINGS.md` (kosmetik, bukan regresi — `string='ID'` sudah ada di source 17.0).
- Mode: **B** (docker-env disiapkan AI — `Dockerfile`/`docker-compose.yml` di-rework untuk 18.0,
  instance terpisah dari BACKFILL 17.0, penamaan unik atas permintaan dev — lihat komentar di kedua
  file; dev yang menjalankan `docker compose up --build`).

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `purchase_product_optional/__manifest__.py` saja
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `__manifest__.py` (DIFF-02)
- **Aksi:**
  - `__manifest__.py`: hapus `'sale_product_configurator'` dari `depends` (modul dihapus total di
    18.0 — DIFF-02). `depends` jadi `['purchase', 'purchase_product_matrix']`.
  - `__manifest__.py`: `version` dari `'17.0.1.0.0'` → `'18.0.1.0.0'`.
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak menghapus/mengubah `data` (tetap `views/purchase_order_views.xml`).
  - Tidak menyentuh `assets` (key `web.assets_backend`/`web.qunit_suite_tests`/`web.assets_tests`
    dipertahankan apa adanya — verifikasi validitas key ini di 18.0 ditunda ke Checkpoint G1, bukan
    diasumsikan sekarang).
  - Tidak menyentuh `auto_install`, `license`, `category`, `summary`, `description`, `images`.
  - Tidak menyentuh file lain (XML, Python, JS) — itu scope A2/A3/A5/dst.
- **Risiko:** LOW (mekanis, sesuai `03_MIGRATION_SPEC.md` — tapi WAJIB, install-breaking kalau
  terlewat).
- **Status:** ✅ Selesai

**Revisi 2026-07-29 (setelah G2, eskalasi MF-14):** `depends` diubah lagi jadi
`['purchase', 'purchase_product_matrix', 'sale']` — G2 menemukan `optional_product_ids`/
`has_optional_products` (field inti fitur "optional products") hanya ada di modul `sale`, yang
sebelumnya tertarik transitif lewat `sale_product_configurator` (sekarang dihapus, DIFF-02). User
memilih tambah `'sale'` eksplisit setelah diberi 2 opsi (eskalasi penuh). Net footprint SAMA seperti
17.0. Detail lengkap: `FINDINGS.md` MF-14.

## [Fase A2] XML Tree → List

- **Scope:** `purchase_product_optional/views/purchase_order_views.xml` saja
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris view + §2b "View List Checklist" (DIFF-06)
- **Aksi:**
  - `views/purchase_order_views.xml`: 4 titik diganti `//tree`/`<tree>` → `//list`/`<list>`:
    1. `xpath expr="//tree/field[@name='product_template_id']" position="attributes"` → `//list/...`
    2. `xpath expr="//tree/field[@name='product_template_id']" position="after"` → `//list/...`
    3. `xpath expr="//tree/field[@name='product_id']" position="attributes"` → `//list/...`
    4. Inner `<tree>...</tree>` (sub-view field `product_custom_attribute_value_ids`) → `<list>...</list>`
- **Konfirmasi vs `03_MIGRATION_SPEC.md`:** §2b "View List Checklist" sudah mencatat 4 titik dengan
  benar (baris 1 eksplisit menyebut "2 xpath terpisah" untuk target `product_template_id` — total
  2+1+1=4), konsisten dengan yang dieksekusi di sini. Tidak ada gap.
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak ada perubahan field, widget, atribut (`column_invisible`, `optional`, `string`, dst),
    domain, atau context — HANYA tag `tree`/`list` yang diganti.
  - Tidak menyentuh XML-ID (`purchase_order_view_form` tetap sama).
  - Tidak menyentuh file lain (manifest sudah selesai di A1, model/JS/controller belum disentuh).
- **Risiko:** LOW (mekanis, sesuai `03_MIGRATION_SPEC.md`) — tapi WAJIB, install-breaking (`ParseError:
  Invalid view type: 'tree'`) kalau terlewat.
- **Status:** ✅ Selesai

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** Struktur folder + seluruh `__init__.py` (`purchase_product_optional/`)
- **Item spec (ref):** `06a_CODE_MIGRATION_PHASES.md` Fase A4 (validasi struktural, bukan blocker install)
- **Aksi:**
  - Verifikasi struktur folder: `controllers/`, `i18n/`, `models/`, `static/` (`description/`, `src/js/`
    5 subfolder komponen + patch, `tests/` + `tests/tours/`), `tests/`, `views/` — semua konsisten
    dengan `04_SPEC_COMPLETENESS_REVIEW.md` (tidak ada `security/`/`data/`/`report/`/`wizard/`, sudah
    dikonfirmasi N/A sejak step 4).
  - Verifikasi isi tiap `__init__.py`:
    - Root: `from . import controllers` + `from . import models` — cocok, kedua folder ada.
    - `controllers/__init__.py`: `from . import main` — cocok, `main.py` ada.
    - `models/__init__.py`: `from . import purchase_order_line/product_template/purchase_order` —
      cocok, ketiga file ada.
    - `tests/__init__.py`: mengimpor 5 file test (`test_purchase_order_currency`,
      `test_purchase_order_line_fields`, `test_controllers`, `test_tours`, `test_qunit`) — cocok,
      semua ada.
  - Tidak ditemukan folder yatim, file tanpa entry `__init__.py`, atau entry `__init__.py` yang
    menunjuk file tidak ada.
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak ada folder dibuat (tidak ada yang hilang).
  - Tidak ada `__init__.py` dinormalisasi (semua sudah konsisten, tidak perlu diedit).
  - Tidak ada perubahan business logic, XML, security, dependency.
- **Risiko:** LOW (validasi struktural murni, zero perubahan).
- **Status:** ✅ Selesai TANPA perubahan logic/behavior — struktur sudah bersih dari awal (warisan
  BACKFILL yang rapi).

## [Fase A5] Python API Compatibility (Models Only)

- **Scope:** `models/purchase_order.py`, `models/purchase_order_line.py`, `models/product_template.py`
- **Item spec (ref):** `knowledge/version-diffs/17-to-18.md` §1b (gotcha API Python 17→18)
- **Aksi:** Cek ketiga file terhadap daftar gotcha di knowledge base:
  - `create()` — tidak ada override di modul ini → `@api.model_create_multi` tidak relevan.
  - `ir.config_parameter.get_param()`/`set_param()` — sudah pakai `.sudo()` di kedua tempat
    (`purchase_order.py` 3×, `product_template.py` 1×) — sudah sesuai rekomendasi 18.0 tanpa perlu
    diubah.
  - `@api.depends` — `_compute_custom_attribute_values`/`_compute_no_variant_attribute_values`
    (`purchase_order_line.py`) depends `product_id` saja, membaca `product_id.product_tmpl_id...` —
    traversal dari field yang terdaftar di depends, bukan gap dependency. Tidak diubah (behavior
    warisan BSL-021/022, sudah dikonfirmasi identik lewat G1 barusan).
  - `user_has_groups`, `_name_search`, `_check_recursion`, `fields.function`, `copy`/`copy_data`
    override, `group_operator` — tidak ada satupun dipakai di 3 file ini.
  - `onchange_partner_id`/`onchange_id_vendor` — pakai implicit assignment (`self.field = ...`),
    bukan return dict eksplisit. Ini "masih ditoleransi" per knowledge base (bukan breaking), DAN
    ini persis bug warisan MF-02 (`BSL-010`..`012`) yang WAJIB dipertahankan identik — tidak diubah
    jadi return dict eksplisit meski itu pola lebih modern (akan mengubah behavior observability,
    di luar scope port kode).
- **Secara eksplisit TIDAK dilakukan:**
  - **TIDAK ADA PERUBAHAN KODE SAMA SEKALI di Fase A5** — ketiga file sudah kompatibel API 18.0 dari
    awal. Ini dikonfirmasi lebih lanjut oleh Checkpoint G1 (sudah PASS sebelum A5 ini dikerjakan,
    memakai file yang sama persis) — tidak ada `AttributeError`/`TypeError` runtime dari model-model
    ini saat load.
  - Tidak menyentuh XML/JS/controller/manifest (sudah selesai fase sebelumnya).
- **Risiko:** LOW (murni audit, zero perubahan).
- **Status:** ✅ Selesai — **DITINJAU, TIDAK ADA PERUBAHAN** (sesuai opsi valid di
  `06b_PROMPTS_BY_PHASE.md` B1: "atau 'DITINJAU — TIDAK ADA PERUBAHAN'").

## [Fase B1] Python Model Semantics (Risiko Rendah)

- **Scope:** `models/*.py` (sama 3 file seperti A5, fokus beda: semantik bukan cuma API compat)
- **Aksi:** Cek kelengkapan `@api.depends`, keamanan relasi (`-=` operator recordset), semantik
  onchange, constraint & default — semuanya konsisten dengan behavior warisan (BSL-021/022 untuk
  compute, BSL-010..012 untuk onchange). Tidak ada relasi berantai/mutasi input dict berbahaya (scope
  itu ada di B2, N/A untuk modul ini).
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan business logic/field baru.
- **Risiko:** LOW. **Status:** ✅ Selesai — **DITINJAU, TIDAK ADA PERUBAHAN**.

## [Fase C1] XML Views Non-OWL, Mekanis

- **Scope:** `views/purchase_order_views.xml` (satu-satunya file XML non-Owl di modul ini)
- **Aksi:** Tree→List sudah tuntas di A2 (4 titik). Dicek ulang: tidak ada elemen non-Owl lain yang
  butuh perubahan mekanis (tidak ada `attrs=`/`states=` deprecated syntax — modul ini memang tidak
  pernah pakai pola itu, sudah dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b).
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan field/domain/redesign.
- **Risiko:** LOW. **Status:** ✅ Selesai — sudah tercakup penuh oleh A2, tidak ada tambahan.

## [Fase D1] Controllers

- **Scope:** `controllers/main.py` (4 route JSON)
- **Aksi:** Import `from odoo.http import Controller, request, route` + decorator `@route(...)` —
  pola modern, tidak ada perubahan konvensi routing yang ditemukan di knowledge base untuk pola ini.
  Tidak ada `website=True`, tidak ada session handling custom. Method core yang dipanggil
  (`_get_first_possible_combination`, `_create_product_variant`, `_get_variant_for_combination`,
  `_get_attribute_exclusions`) sudah dikonfirmasi ADA di `product.template` 18.0 (step 2, DIFF-02) —
  signature terlihat kompatibel dari pembacaan kode `native-target`.
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan URL route, auth, business logic. **Tidak
  ada verifikasi RUNTIME nyata di fase ini** (baca kode saja) — dikonfirmasi eksekusi nyata baru di
  G2/step 9 (AC-09-01, `03_MIGRATION_SPEC.md` §2b "Controller & Route").
- **Risiko:** MEDIUM (baca-kode-saja, belum runtime) — sesuai `03_MIGRATION_SPEC.md`.
- **Status:** ✅ Selesai (struktural) — runtime pending G2/step 9.

## [Fase D2] Assets & CSS Stabilization

- **Scope:** `__manifest__.py` (assets, sudah diverifikasi G1 tidak error), `product.scss`,
  `product_template_attribute_line.scss`
- **Aksi:** Cek 2 file SCSS — tidak ada `@import` custom, tidak ada pembagian `/` sebagai operator
  matematika (cuma dipakai di path URL, bukan sass division) yang berisiko kena dart-sass strict mode
  (`knowledge/version-diffs/17-to-18.md` §2, confidence rendah tapi dicek tetap aman). Variabel/mixin
  Odoo core yang dipakai (`$border-color`, `$theme-colors`, `o-field-pointer`, `o-position-absolute`,
  `$o-view-background-color`, `$o-btns-bs-override`, `str-replace`) — belum diverifikasi eksplisit
  masih ada persis di bundle SCSS 18.0 (perlu compile nyata untuk pastikan, bukan cuma baca kode).
- **Secara eksplisit TIDAK dilakukan:** Tidak ada redesign visual, tidak ada asset baru. **Tidak ada
  verifikasi compile SCSS nyata di fase ini** — dilimpahkan ke G2 (kalau CSS gagal compile, akan
  terlihat sebagai warning/error asset saat server start atau tampilan visual rusak).
- **Risiko:** LOW-MEDIUM (baca-kode-saja untuk variabel/mixin, belum compile nyata).
- **Status:** ✅ Selesai (struktural) — runtime pending G2.

## [Fase E] JavaScript (Owl versi baru)

- **Scope:** `static/src/js/**/*.js` — patch (`purchase_product_field.js`) + 5 komponen Owl (`Product`,
  `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`, `ProductConfiguratorDialogPurchase`)
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 (DIFF-04, DIFF-05), §2b "OWL Widget yang Butuh
  Rewrite/Review"
- **Aksi:**
  - `purchase_product_field.js`:
    1. **DIFF-04 (WAJIB):** rename method `_editProductConfiguration()` → `onEditConfiguration()`
       (termasuk `super._editProductConfiguration(...arguments)` → `super.onEditConfiguration(...arguments)`
       di baris pertama). Isi/behavior method TIDAK diubah — verifikasi cross-reference ke base class
       18.0 (`purchase_product_matrix/static/src/js/purchase_product_field.js`, native-target):
       method baru bernama persis `onEditConfiguration()`, tanpa argumen, isinya
       `if (is_configurable_product) this._openGridConfigurator(true)` — pola unconditional-super-call
       yang sama persis DIPERTAHANKAN (bukan hal baru, konsisten dengan BSL-009/BSL-020 warisan).
    2. **DIFF-05:** `this._openGridConfigurator();` (tanpa argumen, di cabang `result.mode` bukan
       `'configurator'`) → `this._openGridConfigurator(false);` (argumen eksplisit). `false` dipilih
       karena cabang ini adalah first-time product selection (bukan re-edit), sama persis dengan
       pola base class sendiri (`this._openGridConfigurator(false)` di `_onProductTemplateUpdate`
       base 18.0) — bukan behavior baru, cuma bikin implicit-`undefined` jadi eksplisit-`false`
       (keduanya falsy, hasil `if(edit)` identik).
    3. Verifikasi seluruh import lain (`x2ManyCommands` dari `@web/core/orm_service`,
       `serializeDateTime` dari `@web/core/l10n/dates`, `WarningDialog` dari
       `@web/core/errors/error_dialogs`, `useService` dari `@web/core/utils/hooks`,
       `useRecordObserver` dari `@web/model/relational_model/utils`, signature `patch(obj, ext)` dari
       `@web/core/utils/patch`) — SEMUA dicek langsung ke source `native-target`, tidak ada yang
       pindah path/berubah signature. Tidak ada perubahan.
  - 5 komponen Owl lain: dibaca penuh, tidak ditemukan pola classic/deprecated (`Component.extend()`,
    `odoo.define`, `owl.hooks.*`, `willStart()`/`mounted()` lama). Semua `import { Component,
    onWillStart, useState, useSubEnv } from "@odoo/owl"` dan lifecycle Owl 2 modern. **Tidak ada
    perubahan kode.**
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak ada perubahan behavior/business logic — kedua fix DIFF-04/DIFF-05 murni mekanis
    (rename + argumen eksplisit yang falsy-equivalent).
  - 3 `console.log` debug (BSL-028) TIDAK dihapus/dibersihkan — dipertahankan apa adanya.
  - Pola unconditional `super.onEditConfiguration(...arguments)`/`super._onProductTemplateUpdate(...)`
    yang jadi akar F-06/BSL-020 (dua dialog tumpang tindih) TIDAK "diperbaiki" — dipertahankan identik
    sesuai prinsip Source of Truth.
  - **Belum diverifikasi runtime nyata (bundling JS di browser)** — G1 (`--stop-after-init`) TIDAK
    memvalidasi JS bundling/webclient rendering, cuma instalasi Python/XML. Verifikasi visual
    JS/Owl sungguhan (dialog terbuka, tidak ada `OwlError`/console error) dilimpahkan ke G2.
- **Risiko:** MEDIUM (2 fix mekanis WAJIB sudah dieksekusi, tapi belum ada bukti runtime browser).
- **Status:** ✅ Selesai (kode) — verifikasi runtime pending G2.

## [Fase F] Upgrade Template (Syntax Owl Baru)

- **Scope:** 5 file XML template (`product.xml`, `product_list.xml`,
  `product_template_attribute_line.xml` [6 sub-template: ptal + 5 varian ptav], `badge_extra_price.xml`,
  `product_configurator_dialog.xml`)
- **Prasyarat:** Fase E selesai penuh (dikonfirmasi di atas) — dikerjakan SETELAH, sesuai urutan wajib.
- **Aksi:** Dibaca penuh kelima file. SEMUA sudah pakai syntax Owl 2/QWeb modern dari awal:
  `t-on-click` (bukan `t-att-on-click`), `t-att-*` untuk atribut HTML native, props komponen custom
  tanpa prefix (`products="..."`, `t-props="..."`), `t-out`, `t-set-slot`. Tidak ditemukan satupun
  pola lama yang perlu diupgrade.
- **Secara eksplisit TIDAK dilakukan:**
  - **TIDAK ADA PERUBAHAN sama sekali** — kelima file sudah kompatibel Owl 18.0 dari awal.
  - `Dialog size="size"` (quirk warisan — `this.size` tidak pernah di-set di JS, jadi `undefined`)
    TIDAK diperbaiki/dilengkapi — port apa adanya sesuai Source of Truth.
- **Risiko:** LOW (zero perubahan, tapi rendering Owl sungguhan tetap perlu dibuktikan G2 — parsing
  QWeb valid secara statis tidak sama dengan terbukti render benar di browser).
- **Status:** ✅ Selesai — **DITINJAU, TIDAK ADA PERUBAHAN**. Ini mengonfirmasi ekspektasi awal
  `01a_MIGRATION_INTAKE.md` §4: modul dengan Owl modern (bukan pola classic) migrasi Fase E/F jauh
  lebih ringan dari worst-case yang didokumentasikan `knowledge/version-diffs/17-to-18.md` §1b.

---

## [Fase G2] Validasi Runtime via Browser (Checkpoint)

- **Scope:** Server hidup (Mode B, `docker-env/` instance 18.0, db `purchase_product_optional_18_demo`),
  interaksi nyata via Claude in Chrome — bukan sekadar baca kode.
- **Setup data test:** attribute dynamic + supplierinfo vendor baru dibuat manual via UI pada produk
  demo "Customizable Desk" (mengikuti pola yang sama seperti Step 07 BACKFILL 17.0, supaya skenario
  bisa dibandingkan apple-to-apple).
- **Bug #1 ditemukan — MF-13 (`useService("rpc")` dihapus di 18.0):**
  - Gejala: dialog crash instan, `Error: Service rpc is not available` di
    `ProductConfiguratorDialogPurchase.setup`.
  - **TIDAK terdeteksi Fase E** (review statis) — sintaks tetap valid, hanya rusak di runtime karena
    service tidak lagi terdaftar di registry 18.0.
  - Fix: `product_configurator_dialog.js` — `import { rpc } from "@web/core/network/rpc"` + ganti 4
    call site (`_loadData`, `_createProduct`, `_updateCombination`, `_getOptionalProducts`) dari
    `this.rpc(...)` → `rpc(...)`, hapus `this.rpc = useService("rpc")`. Pola dikonfirmasi identik
    dengan idiom native `sale/product_configurator_dialog.js` 18.0.
  - Verifikasi: restart container, retest — error hilang, dialog lanjut ke titik berikutnya.
  - Detail: `FINDINGS.md` MF-13.
- **Bug #2 ditemukan — MF-14 (`optional_product_ids` hilang tanpa `sale`):**
  - Gejala: setelah MF-13 diperbaiki, dialog crash lagi di titik berbeda —
    `AttributeError: 'product.template' object has no attribute 'optional_product_ids'` di
    `controllers/main.py:90`.
  - Root cause dikonfirmasi via baca langsung `odoo18/addons/sale/models/product_template.py` (field
    didefinisikan di sana, bukan di `product`/`purchase`) + perbandingan log historis (17.0 load
    `sale` transitif via `sale_product_configurator`, 18.0 tidak lagi sejak DIFF-02 fix).
  - **Eskalasi ke user** (format ESCALATION penuh, 2 opsi) — user pilih: tambah `'sale'` ke `depends`.
  - Fix: `__manifest__.py` `depends` → `+ 'sale'` (lihat revisi Fase A1 di atas).
  - Verifikasi: **belum dieksekusi ulang** — perlu restart container (module `sale` belum pernah
    terinstall di db `_demo` yang sedang jalan, jadi butuh `-u purchase_product_optional` supaya Odoo
    mendeteksi dependency baru dan install `sale` otomatis, bukan cuma restart biasa).
  - Detail: `FINDINGS.md` MF-14.
- **Update (2026-07-29, lanjutan sesi sama) — restart+retest setelah fix MF-14:**
  - Container direstart dengan `-u purchase_product_optional` (bukan `-i`) — log konfirmasi `sale`
    berhasil terinstall (58→59 modul), tanpa error/CRITICAL.
  - Retest live browser (PO baru, "Customizable Desk" + vendor "Azure Interior"): dialog "Configure
    your product" terbuka BERSIH — Legs, Color, DAN section "Add optional products" (fitur inti yang
    tadi mati karena MF-14) semua render & berfungsi (tombol "+Add" berhasil menambah "Conference
    Chair"). **MF-13 dan MF-14 KONFIRMASI RESOLVED lewat eksekusi nyata**, bukan cuma baca kode.
  - **Efek samping bernilai:** begitu dialog custom terbuka bersih, grid "Choose Product Variants"
    (`purchase_product_matrix`) ikut terbuka BERSAMAAN — mereproduksi **F-06/MF-06 identik** dengan
    17.0. Skenario penuh dijalankan (pilih Legs/Color → tambah optional product → Confirm dialog
    custom TANPA menyelesaikan grid di belakangnya) → **baris produk utama "Customizable Desk" hilang
    TOTAL dari PO**, hanya "Conference Chair" (optional product) tersisa — silent, tanpa error toast,
    persis seperti dideskripsikan BACKFILL F-06. **Bug warisan dikonfirmasi TETAP IDENTIK di 18.0**,
    sesuai prinsip Source of Truth (tidak diperbaiki).
  - Detail baru (bukan regresi, cuma observasi): console browser menunjukkan 3× `Error: Component is
    destroyed` (ORM calls di `ProductConfiguratorDialogPurchase` yang resolve setelah component
    di-destroy oleh dialog grid) — kemungkinan Owl 2 (18.0) lebih strict soal lifecycle dibanding Owl
    1 (17.0). Dicatat sebagai detail tambahan Step 9/10, bukan item perbaikan.
  - Harga tampil `$0.00` untuk kedua produk — kemungkinan besar karena db demo 18.0 baru belum ada
    `supplierinfo` custom (setup itu spesifik ke db BACKFILL 17.0) — dicatat sebagai catatan terpisah
    untuk Step 10, BUKAN diasumsikan regresi MF-04.
- **Status:** ✅ **G2 selesai untuk tujuan migrasi** — kedua bug migrasi (MF-13, MF-14) resolved &
  terverifikasi eksekusi nyata. F-06/MF-06 (bug warisan) dikonfirmasi direproduksi identik, sesuai
  ekspektasi (bukan diperbaiki). Verifikasi harga per-vendor (AC-05-01) dan reproduksi F-06 yang lebih
  sistematis dilimpahkan ke Step 10 (QA Testing) dengan setup data test yang sepadan dengan BACKFILL.

---

## Temuan di Luar Spec (kalau ada)

- [x] **MF-13** — `useService("rpc")` dihapus di 18.0 (lihat `FINDINGS.md`) — ditemukan G2, sudah
  diperbaiki & diverifikasi.
- [x] **MF-14** — `optional_product_ids`/`sale` dependency hilang (lihat `FINDINGS.md`) — ditemukan
  G2, eskalasi user, sudah diputuskan & diperbaiki di kode, verifikasi ulang pending restart.

## Kontribusi ke Knowledge Base

- [ ] **Kandidat baru (belum dipromosikan, tunggu curation eksplisit):** kelas risiko "menghapus 1
  dependency (fix install-blocking) bisa diam-diam menghilangkan dependency LAIN yang ditarik
  transitif olehnya" — relevan untuk `knowledge/version-diffs/17-to-18.md` sebagai general gotcha,
  bukan cuma spesifik modul ini. Dicatat dulu di `migration-records/.../SUMMARY.md`.
