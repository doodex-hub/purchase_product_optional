# Implementation Log — purchase_product_optional (17.0 → 18.0)

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check (sebelum Fase A)

| Fase | Relevan untuk modul ini? | Sumber |
|---|---|---|
| C1 — View Sederhana | ✅ Ya | `views/purchase_order_views.xml` ada |
| B2 — Model Kompleks | ⬜ Tidak | `01a_MIGRATION_INTAKE.md` §2b — tidak ada dynamic model creation/field JSON/relasi >2 level |
| C2 — Semantik XML & UX | ⬜ Tidak | `01a` §2b — tidak ada `attrs`/`states`/`domain`/`context` dinamis |
| D1 — Controllers | ✅ Ya | `controllers/main.py` ada, 4 route |
| D2 — Assets & CSS | ✅ Ya | `static/src/**` ada |
| E — JavaScript (Owl) | ✅ Ya | 5 komponen Owl |
| F — Upgrade Template | ✅ Ya (karena E relevan) — tapi lihat catatan Fase F di bawah, kemungkinan besar N/A murni setelah dicek |

**A1-A5 dan B1** berlaku tanpa syarat (semua modul punya manifest & model).

---

## Fase A — Fondasi

### A1 — Manifest Bootstrap
- **Aksi:** `__manifest__.py` — hapus `'sale_product_configurator'` dari `depends`, tambah `'sale'` (DIFF-02, DIFF-03); bump `version` ke `18.0.1.0.0`.
- **Status:** ✅ Selesai — lihat diff di bawah.

### A2 — XML Tree → List
- **Aksi:** `views/purchase_order_views.xml` — 3× `<tree>`/`//tree/` → `<list>`/`//list/` (DIFF-01).
- **Status:** ✅ Selesai.

### A3 — Security Hardening
- **Status:** ✅ N/A — dikonfirmasi Step 4, tidak ada `security/` di source module (tidak ada model baru/TransientModel).

### Checkpoint G1 — Install Test #1 (setelah A2)
- **Mode:** C (AI jalankan langsung, Docker tersedia di sesi Claude Code CLI ini).
- Lihat tabel "Riwayat Percobaan G1" di bawah untuk hasil.

### A4 — Skeleton & Folder Integrity
- **Status:** ✅ N/A — struktur folder sudah konsisten (`target-codebase` = full copy dari `source-codebase`, tidak ada file hilang, `__init__.py` semua ada).

### A5 — Python API Compatibility (Models)
- **Status:** ✅ N/A — dikonfirmasi `03_MIGRATION_SPEC.md` §2: tidak ada pemakaian `user_has_groups`/`check_access_rights`/`_name_search`/`_check_recursion`/`group_operator`/override `create`/`copy` custom.

### Checkpoint G1 — Install Test #2 (setelah A3)
- Lihat tabel "Riwayat Percobaan G1" di bawah.

---

## Fase B — Python Models

### B1 — Model Risiko Rendah
- **Aksi:** Review `purchase_order.py`, `purchase_order_line.py`, `product_template.py` — tidak ada perubahan dependency compute/relasi/onchange yang wajib untuk 18.0 (semua behavior dipertahankan apa adanya termasuk F-01..F-08).
- **Status:** ✅ Reviewed, tidak ada perubahan.

### B2 — Model Kompleks
- **Status:** ✅ N/A — dikonfirmasi Applicability Check.

---

## Fase C — XML Views (Non-OWL)

### C1 — View Sederhana
- **Status:** ✅ Selesai — sudah tercakup A2 (tree→list adalah satu-satunya perubahan mekanis yang dibutuhkan file ini).

### C2 — Semantik XML & UX
- **Status:** ✅ N/A — dikonfirmasi Applicability Check.

---

## Fase D — Controllers & Assets

### D1 — Controllers
- **Aksi:** Review `controllers/main.py` — route decorator (`@route(..., type='json', auth='user')`) tetap valid, tidak ada perubahan API yang mempengaruhi controller ini.
- **Status:** ✅ Reviewed, tidak ada perubahan.

### D2 — Assets & CSS Stabilization
- **Aksi:** Review key `assets` di `__manifest__.py` — sudah pola modern (`web.assets_backend`/`web.assets_tests`), tidak perlu diubah. SCSS (`product.scss`, `product_template_attribute_line.scss`) tidak pakai syntax yang berubah antar versi.
- **Status:** ✅ Reviewed, tidak ada perubahan.

---

## Fase E — JavaScript (Owl versi baru)

### E — Aksi
1. `static/src/js/purchase_product_field.js` — rename `_editProductConfiguration()` → `onEditConfiguration()` (DIFF-05). Body method tidak berubah.
2. `static/src/js/product_configurator_dialog/product_configurator_dialog.js` — hapus `this.rpc = useService("rpc")` dari `setup()`; tambah `import { rpc } from "@web/core/network/rpc"`; ganti 4× `this.rpc(url, params)` → `rpc(url, params)` (DIFF-07).
3. `_openGridConfigurator()` (DIFF-06) — **tidak diubah**, dikonfirmasi cukup port apa adanya (undefined tetap falsy), diverifikasi eksplisit di G2.
4. Komponen lain (`Product`, `ProductList`, `ProductTemplateAttributeLine`, `BadgeExtraPrice`) — tidak ada perubahan, sudah Owl 2 modern.

- **Status:** ✅ Selesai — lihat diff di bawah.

---

## Fase F — Upgrade Template

- **Aksi:** Cek ulang seluruh `.xml` di `static/src/js/**` untuk pola Owl lama (`t-att-on-click`, dst.) — **tidak ditemukan** (dikonfirmasi `grep` sebelum & sesudah Fase E).
- **Status:** ✅ N/A murni — tidak ada template yang perlu diubah.

---

## Riwayat Percobaan G1 (Install Test)

| # | Kapan | Mode | Hasil | Catatan |
|---|---|---|---|---|
| 1 | 2026-08-24, setelah A1+A2 (A3 N/A) | **C — AI jalankan langsung** (Docker tersedia, Claude Code CLI) | ✅ **PASS** | `docker-env/logs/odoo_g1.log` — 59 modul (termasuk `sale` baru) loaded bersih, `Registry loaded in 42.118s`, exit code 0. Tidak ada `ParseError`/`AttributeError`. Kedua warning bug dipertahankan muncul identik: F-01 (`unknown parameter 'product_add_mode'`) dan F-08 (`Two fields (id_vendor, id)... same label: ID`) — bug-for-bug parity terkonfirmasi runtime, bukan cuma baca kode. View `purchase_order_views.xml` (xpath `//list/...` pasca DIFF-01 fix) ter-load tanpa error, mengonfirmasi DIFF-09 (dependency ke view `purchase_product_matrix`) tetap valid. |

**Kesimpulan G1:** SATU percobaan sudah cukup (A3 N/A, tidak ada blocker kedua untuk diuji terpisah) — kedua checkpoint G1 (setelah A2, setelah A3) efektif tergabung di run ini.

## Fase G2 — Validasi Akhir

> Digabung dengan Step 9 (Dev Testing, `--test-enable --test-tags`) — Tour test (`HttpCase.start_tour`)
> yang jalan di Step 9 SEKALIGUS jadi bukti runtime G2 untuk DIFF-07 (dialog benar-benar terbuka
> tanpa crash `Service rpc is not available`) dan DIFF-05 (edit configuration). Lihat
> `09_devtest/09_DEV_TESTING.md` untuk hasil detail.

| Kriteria | Hasil |
|---|---|
| Tidak ada warning server saat start | ✅ Lihat `odoo_g1.log` — tidak ada warning start selain 2 bug yang dipertahankan (F-01, F-08) |
| Tidak ada error console saat buka halaman terkait diff | ✅ Tour 15/15 langkah PASS, `TOUR ... SUCCEEDED` — tidak ada JS error |
| DIFF-01/02/03/05/07 terkonfirmasi valid di runtime | ✅ Semua terkonfirmasi — lihat `09_devtest/09_DEV_TESTING.md` |

**Temuan tambahan selama Fase G2/Step 9 (tidak terduga dari Step 2/3 awal):**
- **DIFF-10** — core `purchase` 18.0 ternyata sudah mendefinisikan `product_no_variant_attribute_value_ids` sendiri (tidak ada di 17.0) — ditemukan saat review Arah 2 Step 8, tidak breaking (field kita dengan `compute=` menang di merge, dikonfirmasi G1+test).
- **DIFF-11** — Tour test gagal percobaan #1 karena `run: "text ..."` tidak dikenali 18.0, fix ke `run: "edit ..."` — percobaan #2 PASS penuh 15/15.
