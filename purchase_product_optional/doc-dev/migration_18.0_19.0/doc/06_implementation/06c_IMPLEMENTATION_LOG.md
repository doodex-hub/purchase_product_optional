# Implementation Log — purchase_product_optional (18.0 → 19.0)

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Applicability Check (dari `01a_MIGRATION_INTAKE.md` §2b)

| Fase | Relevan untuk modul ini? | Kalau TIDAK relevan |
|---|---|---|
| C1 — View Sederhana | ☑ Ya | `views/purchase_order_views.xml` ada, tapi sudah `<list>` (bukan `<tree>`), tanpa `attrs=`/`domain=`/`context=` dinamis — dikonfirmasi step 2, **tidak ada perubahan diperlukan** |
| B2 — Model Kompleks | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model creation (dikonfirmasi `01a` §2b) — declared N/A |
| C2 — Semantik XML & UX | ☐ Tidak | Tidak ada `attrs=`/`domain=`/`context=` dinamis (dikonfirmasi `01a` §2b) — declared N/A |
| D1 — Controllers | ☑ Ya | `controllers/main.py` ada — perubahan OPSIONAL saja (DIFF-06, `type='json'`→`'jsonrpc'`), tidak wajib |
| D2 — Assets & CSS | ☑ Ya (asset key ada) | Tidak ada perubahan struktural diperlukan — key `assets` manifest tidak berubah format 18→19 |
| E — JavaScript (Owl) | ☑ Ya | **Area kerja utama** — `purchase_product_field.js` (DIFF-01, DIFF-02) |
| F — Upgrade Template | ☐ Tidak | Dicek langsung sesi ini (2026-08-26): SEMUA 5 file `.xml` di `static/src/js/**` sudah pakai `t-out`/`t-on-click`/`t-att-*` modern, TIDAK ada `t-raw`/`t-esc`/pola Owl 1. Tidak ada perubahan template QWeb diperlukan untuk 19.0 (tidak ada di `knowledge/version-diffs/18-to-19.md` yang menyebut breaking change level template QWeb) — declared N/A |

---

## Fase A — Fondasi

### A1 — Manifest Bootstrap
**Aksi:** Bump `version: '18.0.1.0.0'` → `'19.0.1.0.0'` di `__manifest__.py`.
**Status:** ✅ Selesai.

### A2 — XML Tree → List
**Status:** N/A — sudah tuntas di migrasi 17→18 (dikonfirmasi grep bersih step 2/4).

### A3 — Security Hardening
**Status:** N/A — modul tidak punya folder `security/`, tidak ada TransientModel/wizard custom.

### A4 — Skeleton & Folder Integrity
**Status:** ✅ Dicek — struktur folder (`models/`, `views/`, `controllers/`, `static/`) konsisten, tidak ada perubahan diperlukan.

### A5 — Python API Compatibility
**Status:** ✅ Dicek (step 2, DIFF-07) — 0 match pola API lama (`_cr`/`_uid`/`_sql_constraints`/`groups_id`/`osv.expression`/dst). Tidak ada perubahan diperlukan.

### Checkpoint G1 — Install Test
**Status:** ⏳ Belum dijalankan — menunggu keputusan mode eksekusi dari dev (lihat "Riwayat Percobaan G1" di bawah).

| # | Kapan | Mode | Hasil |
|---|---|---|---|
| — | — | — | Belum dijalankan |

---

## Fase B — Python Models

**Status:** N/A untuk B2 (lihat Applicability Check). B1 tidak relevan juga secara praktik — dikonfirmasi step 2 tidak ada perubahan API Python yang diperlukan pada `models/*.py` (DIFF-04, DIFF-05, DIFF-07 semua "tidak berubah"/"bersih").

---

## Fase C — XML Views

### C1 — View Sederhana
**Status:** ✅ Dicek — `views/purchase_order_views.xml` tidak butuh perubahan (lihat Applicability Check).

### C2 — Semantik XML & Konsistensi UX
**Status:** N/A (lihat Applicability Check).

---

## Fase D — Controllers & Assets

### D1 — Controllers
**Aksi:** DIFF-06 (`type='json'`→`'jsonrpc'`) — **opsional, dikerjakan sesi ini** sebagai cleanup ringan (4 baris, non-breaking, tidak menambah risiko).
**Status:** ✅ Selesai.

### D2 — Assets & CSS Stabilization
**Status:** N/A — tidak ada perubahan diperlukan.

---

## Fase E — JavaScript (Owl versi baru)

### `static/src/js/purchase_product_field.js` — DIFF-01 + DIFF-02
**Aksi:**
1. Import `useMatrixConfigurator` dari `@product_matrix/js/matrix_configurator_hook` (baru).
2. `setup()`: tambahkan `this.matrixConfigurator = useMatrixConfigurator()` setelah `super.setup(...)`.
3. `_onProductTemplateUpdate()`: baca `this.props.record.data.product_template_id.id` (bukan `[0]`);
   tulis `product_id: {id: result.product_id, display_name: result.product_name}` (bukan tuple);
   ganti `this._openGridConfigurator()` → `this.matrixConfigurator.open(this.props.record, false)`.
4. `_openProductConfigurator()`: baca `product_template_id?.id` (bukan `?.[0]`), `product_uom?.id`,
   `company_id?.id`, `pricelist_id?.id`, `currency_id?.id` — semua many2one baca `.id`, bukan `[0]`.
   `custom_product_template_attribute_value_id?.[0]` (dari hasil `orm.read`, BUKAN dari `record.data`
   Odoo relational_model — tetap tuple, format `orm.read()` TIDAK berubah 18→19, ini bukan bagian
   DIFF-01) — **tidak diubah**, dikonfirmasi beda konteks data dari `record.data`.
5. `applyProductPurchase()` (function level, bukan method `PurchaseOrderLineProductField`): tulis
   `product_id: {id: product.id, display_name: product.display_name}` (bukan tuple) — fungsi ini
   memanggil `record.update()` pada `purchase.order.line` record (relational_model), sama kelas
   dengan DIFF-01. Juga `x2ManyCommands.create(undefined, {custom_product_template_attribute_value_id: [...]})` — field many2one di dalam command `create` x2many juga ikut diproses relational_model, jadi ikut format objek.
6. **Temuan tambahan saat implementasi (bukan dari step 2, ketemu waktu menulis kode):**
   `_openProductConfigurator()` punya percabangan `customAttributeValues` — cabang `isNew` (baris
   record belum tersimpan) sumbernya `record.data` (relational_model, format objek 19.0), cabang lain
   sumbernya `orm.read()` (RPC, TETAP format tuple `[id,name]` di 19.0 — format RPC tidak berubah).
   Downstream `.map()` yang membaca `data.custom_product_template_attribute_value_id?.[0]` dulunya
   AMAN dipakai untuk kedua cabang di 18.0 (dua-duanya tuple) — di 19.0 tidak aman lagi (dua format
   beda dari sumber beda). **Fix:** normalisasi kedua cabang ke `{custom_product_template_attribute_value_id: <id>, custom_value}` polos di titik ekstraksi (bukan di downstream `.map()`), supaya
   `.map()` akhir tetap format-agnostic. Ini murni migrasi wajib (bukan cleanup/refactor) — tanpa fix
   ini, custom attribute value untuk baris yang SUDAH tersimpan (bukan `isNew`) akan salah baca `ptavId`
   (baca `.id` dari tuple array, selalu `undefined`).
7. **Baris yang SENGAJA TIDAK diubah (preservasi bug, bukan lupa):** `this.props.record.data.product_id != result.product_id.id` (baris ~70) — perbandingan array/objek terhadap number selalu `true` lewat type coercion JS, baik format tuple (18.0) maupun objek (19.0). Perilaku `if` ini SELALU true di kedua versi — tidak ada regresi, TIDAK diperbaiki (preservasi bug-for-bug sesuai `CLAUDE.md`).
**Status:** ✅ Selesai — lihat diff aktual di bawah "Ringkasan Perubahan Kode".

### 5 komponen Owl lain (`product`, `product_list`, `product_template_attribute_line`,
`badge_extra_price`, `product_configurator_dialog`)
**Status:** ✅ Dicek ulang (step 2 DIFF-10 + baca langsung sesi ini) — tidak baca `record.data` Odoo
relational_model, kelola state sendiri via props/hasil RPC — **tidak ada perubahan kode**.

---

## Fase F — Upgrade Template

**Status:** N/A (lihat Applicability Check).

---

## Fase G2 — Validasi Akhir

**Status:** ⏳ Belum dijalankan — menunggu G1 pass dan keputusan mode eksekusi browser dari dev.

---

## Ringkasan Perubahan Kode (diff aktual — lihat commit step 6 untuk diff lengkap)

- `__manifest__.py`: `version` `'18.0.1.0.0'` → `'19.0.1.0.0'`
- `controllers/main.py`: 4× `type='json'` → `type='jsonrpc'`
- `static/src/js/purchase_product_field.js`: rewrite format many2one (tuple→objek) di 8 titik +
  penggantian `_openGridConfigurator()` → `this.matrixConfigurator.open(...)` + import & assign
  `useMatrixConfigurator` baru
