# Diff & Compatibility Analysis — purchase_product_optional

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya | §1 (OCA wiki, high confidence) + §1a (dari project nyata `advanced_sales_analysis`, `sale.order.line.tax_id`→`tax_ids`) |
| `dependency-compat/purchase_product_matrix/...` | Ya, tapi HANYA `17-to-18.md` — belum ada entry `18-to-19.md`. Ditemukan sendiri di step ini (lihat DIFF-01/02 di bawah), akan dicatat sebagai kandidat baru di `migration-records/`. | |
| `dependency-compat/sale_report`, `account_payment`, `auth_totp*` | Ya, tapi tidak relevan modul ini (tidak depend ke modul-modul itu) | |

## 0b. Gate Community vs Enterprise

- [x] Dicek ulang `01a_MIGRATION_INTAKE.md` §2 — **TIDAK ADA** baris bertipe "Native Enterprise" (`purchase`/`purchase_product_matrix`/`sale` semua Community).
- [x] Karena tidak ada dependency Enterprise, cukup `native-target` (Community, `enterprise19.0/odoo/addons/`) untuk analisis di bawah — `native-target-enterprise` tetap tersedia (folder sama, `enterprise19.0`) tapi tidak ada baris DIFF yang butuh dicek khusus di sana untuk modul ini.

## 0c. Gate Transitive Dependency

- [x] Tidak ada `depends` yang akan DIHAPUS di migrasi ini (`purchase`, `purchase_product_matrix`, `sale` — ketiganya masih ada di 19.0, dikonfirmasi §1 di bawah) — gate ini **N/A**, tidak perlu enumerasi transitive dependency.

---

## 1. Perubahan Native (Core/Enterprise)

> Dicek langsung `native-source` (`D:\Kuncoro\doodex\repo\odoo18`) vs `native-target`
> (`D:\Kuncoro\doodex\repo\enterprise19.0`) untuk tiap simbol yang benar-benar dipakai/di-inherit modul
> ini (bukan seluruh API `purchase`/`sale`/`purchase_product_matrix`).

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `static/src/js/purchase_product_field.js` (`patch(PurchaseOrderLineProductField.prototype, ...)`) | `purchase_product_matrix/static/src/js/purchase_product_field.js` — `PurchaseOrderLineProductField` | **Behavior berubah — BREAKING KRITIS** | Field many2one di `record.data` berubah representasi: 18.0 = tuple `[id, display_name]` (akses `data.product_template_id[0]`), 19.0 = objek `{id, display_name}` (akses `data.product_template_id.id`). Dikonfirmasi diff langsung `purchase_product_field.js` native 18.0 vs 19.0 — SEMUA akses `[0]` diganti `.id`, semua tulis `field: [id, name]` diganti `field: {id, display_name}`. Modul ini (`patch`) punya **8 titik** akses/tulis gaya tuple lama (`purchase_product_field.js:34,61,68,73,121,124,128,129,130,131` — lihat DIFF-01 detail di bawah) yang akan **crash/salah baca** di 19.0 kalau tidak diport. | `odoo18/addons/purchase_product_matrix/static/src/js/purchase_product_field.js` vs `enterprise19.0/odoo/addons/purchase_product_matrix/static/src/js/purchase_product_field.js` (diff langsung, 2026-08-26) |
| DIFF-02 | `static/src/js/purchase_product_field.js` — pemanggilan `this._openGridConfigurator()` (fallback non-configurator, baris 92) | `PurchaseOrderLineProductField._openGridConfigurator`/`_openMatrixConfigurator` (native) | **Dihapus total dari base class** | Native 19.0 MENGHAPUS method `_openGridConfigurator`/`_openMatrixConfigurator` dari `PurchaseOrderLineProductField` sepenuhnya — diganti pola hook `useMatrixConfigurator()` (`this.matrixConfigurator.open(record, edit)`, di-assign di `setup()`). Modul ini memanggil `this._openGridConfigurator()` (mengandalkan method warisan base class via `patch`) sebagai fallback saat `result.mode !== 'configurator'` — **akan throw `TypeError: this._openGridConfigurator is not a function`** di 19.0 kalau tidak diport ke `this.matrixConfigurator.open(...)`. Modul ini sendiri TIDAK meng-override `_openGridConfigurator` (beda dari `onEditConfiguration`/`_onProductTemplateUpdate` yang di-override via `super()`), jadi method ini murni bergantung pada base class native. | Sama seperti DIFF-01 |
| DIFF-03 | `static/src/js/purchase_product_field.js` (`import { PurchaseOrderLineProductField } from '@purchase_product_matrix/js/purchase_product_field'`, `patch(...prototype, {setup(){super.setup(...)}, onEditConfiguration(){super.onEditConfiguration(...)}, _onProductTemplateUpdate(){super._onProductTemplateUpdate(...)}})`) | `registry.category("fields").add("pol_product_many2one", {...})` — komposisi field registry | Signature berubah (non-breaking untuk `patch`) | Native 19.0 mengganti base object `many2OneField` → `productLabelSectionAndNoteField` di komposisi registry field, DAN menambah `get label()` baru serta constructor `this.orm = useService("orm")` langsung di `setup()` (18.0 tidak assign `this.orm` di base — hanya `this.dialog`). Modul ini sendiri sudah assign `this.orm`/`this.dialog`/`this.notification` sendiri di `patch(...).setup()`, jadi TIDAK bentrok (redundant assign, aman). `super.setup(...)`/`super.onEditConfiguration(...)`/`super._onProductTemplateUpdate(...)` tetap valid dipanggil (method-method itu MASIH ada namanya sama di 19.0, cuma isinya beda — lihat DIFF-01/02). | Sama seperti DIFF-01 |
| DIFF-04 | `models/product_template.py::convert_price()` — pemanggil `self.env['res.currency']._convert()` | `res.currency._convert(self, from_amount, to_currency, company=None, date=None, round=True)` | Tidak berubah | Signature `_convert()` dikonfirmasi stabil 17.0→18.0 (CAND-03, `SUMMARY.md` 17_18) — belum diverifikasi ULANG khusus 18.0→19.0 di sesi ini, tapi tidak ada perubahan `res.currency` yang tercatat di `knowledge/version-diffs/18-to-19.md` §1/§1a manapun. Risiko rendah. | `knowledge/version-diffs/18-to-19.md` (tidak menyebut `res.currency`), analisis baru |
| DIFF-05 | `models/purchase_order.py::onchange_partner_id` (override total nama method core) | `purchase.order.onchange_partner_id` (core `purchase`) | Tidak berubah — tetap override total | BSL-005 (baseline spec) mendokumentasikan override total ini sejak 17.0/18.0. **Diverifikasi langsung 2026-08-26:** core `purchase.order.onchange_partner_id` MASIH ada di 19.0 dengan nama identik (`enterprise19.0/odoo/addons/purchase/models/purchase_order.py:445`, `@api.onchange('partner_id', 'company_id')`) — isinya set `fiscal_position_id`/`payment_term_id`/dst berdasarkan partner (mirip 18.0). Karena modul ini override method dengan nama SAMA (bukan `_inherit` extend), efek samping core ini **tetap tertimpa total** di 19.0 juga — perilaku BSL-005 (dipertahankan sesuai `CLAUDE.md`, tidak diperbaiki) konsisten berlaku, bukan hal baru yang perlu ditangani migrasi ini. | Verifikasi langsung `native-target` 19.0, 2026-08-26 |
| DIFF-06 | `controllers/main.py` — `@route(..., type='json', auth='user')` (4 route) | `odoo.http.route` — parameter `type` | Deprecated (bukan breaking) | Dikonfirmasi `knowledge/version-diffs/18-to-19.md` §1: `type='json'` di 19.0 tetap jalan sebagai **alias deprecated** untuk `type='jsonrpc'` (dikonfirmasi langsung di `native-target` `odoo/http.py` — pesan `"Since 19.0, @route(type='json') is a deprecated alias..."`). Aman diport apa adanya, cleanup opsional (bisa diganti `type='jsonrpc'` di step 3 sebagai non-breaking improvement, TIDAK wajib). | `knowledge/version-diffs/18-to-19.md` §1 (verifikasi langsung) |
| DIFF-07 | `models/purchase_order.py`, `purchase_order_line.py`, `product_template.py` — pola umum Python (`_cr`/`_uid`/`_context`, `_sql_constraints`, `groups_id`, `osv.expression`, `read_group`, `auto_join`, `SUPERUSER_ID`, `ormcache_context`, `name_search`, `@api.returns`, `toggle_active`) | Berbagai perubahan API §1 `knowledge/version-diffs/18-to-19.md` | **Tidak berlaku — modul tidak memakai pola manapun** | Grep langsung ke seluruh `models/*.py` (2026-08-26): 0 match untuk semua pola di atas. Modul ini kecil & modern, tidak memakai API internal/deprecated apapun dari daftar §1. | Grep `source-codebase/purchase_product_optional/models/*.py`, 2026-08-26 |
| DIFF-08 | `views/purchase_order_views.xml` — atribut `groups=` | `res.groups`/`groups_id`→`group_ids` (§1 knowledge) | Tidak berlaku | Grep `views/*.xml` untuk `groups=` — 0 match. Tidak ada manipulasi group/access di view modul ini. | Grep, 2026-08-26 |
| DIFF-09 | Seluruh modul — pemakaian `sale.order.line.tax_id` | `sale.order.line.tax_id`→`tax_ids` (rename, §1a knowledge, ditemukan project `advanced_sales_analysis`) | Tidak berlaku | Grep `tax_id` ke seluruh modul (`.py`/`.xml`/`.js`) — 0 match. Modul ini tidak menyentuh field pajak SO line sama sekali. | Grep, 2026-08-26 |
| DIFF-10 | `static/src/js/product_configurator_dialog/*.js`, `product/*.js`, `product_list/*.js`, `product_template_attribute_line/*.js`, `badge_extra_price/*.js` | Format data many2one Odoo record (tuple vs objek, sama isu DIFF-01) | Tidak berlaku (komponen ini tidak baca `record.data` Odoo langsung) | Grep pola akses tuple (`.data.xxx[0]`, `?.[0]`) ke SELURUH `static/src/js/**/*.js` — HANYA `purchase_product_field.js` yang match (8×, sudah dicatat DIFF-01). 5 komponen dialog lain mengelola state sendiri (props biasa + hasil `orm.call`/`search_read`, bukan Odoo `record.data` proxy) — TIDAK terpapar perubahan format many2one `record.data`. Perlu tetap diverifikasi ulang di step 6 (code migration) via eksekusi nyata, bukan cuma grep statis. | Grep seluruh `static/src/js/`, 2026-08-26 |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| — | — | — | Tidak ada dependency OCA/third-party (dikonfirmasi §0/§2 `01a_MIGRATION_INTAKE.md` — scan manifest bersih, `purchase`/`purchase_product_matrix`/`sale` semua modul core Odoo). Konfirmasi final dev masih tertunda (dev menjawab "tidak yakin") — tidak mengubah baris tabel ini karena tidak ada kandidat OCA yang perlu dicek. |

---

## 3. Temuan Baru — Kandidat Migration Records

- [x] **DIFF-01/DIFF-02/DIFF-03** (kategori `dependency-compat`, `purchase_product_matrix`) — general, berlaku untuk SEMUA modul custom yang mem-`patch`/extend `PurchaseOrderLineProductField` (pola umum konfigurator Purchase custom, sama seperti `purchase_product_matrix` sendiri jadi target patch berulang di `dependency-compat/purchase_product_matrix/17-to-18.md` yang sudah ada sebelumnya). **Akan dicatat** ke `migration-tool/migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md` di akhir step ini sebagai kandidat kuat `dependency-compat/purchase_product_matrix/18-to-19.md` (file BARU).
- [x] **DIFF-07/08/09** (kategori `version-diff`, konfirmasi negatif) — bukan temuan baru untuk `knowledge/`, tapi berguna dicatat di `migration-records/` sebagai data point "modul modern tanpa dependency ke API lama" — kurang prioritas untuk promosi.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 (format many2one `record.data`, `purchase_product_field.js`) | **Tinggi** | Breaking pasti (bukan "mungkin") — 8 titik kode akan salah baca/tulis atau crash kalau tidak diport. Wajib Fase E step 6, prioritas pertama. |
| DIFF-02 (`_openGridConfigurator` dihapus dari base) | **Tinggi** | Breaking pasti — `TypeError` runtime kalau jalur fallback (`result.mode !== 'configurator'`) tereksekusi. Baris ini SEMENTARA tidak ke-cover test existing (perlu dicek di step 5/9 apakah ada test yang memicu jalur ini — `get_single_product_variant()` yang menentukan `mode` berasal dari core, CAND-07 mencatat `purchase_warning`/`mode` malah TIDAK PERNAH terisi untuk konteks Purchase, jadi kemungkinan jalur `else` fallback ini secara praktik jarang/tidak pernah tereksekusi produksi — TETAP wajib diperbaiki, bukan alasan untuk skip). |
| DIFF-03 (komposisi registry field) | Rendah | Non-breaking untuk pola `patch()` yang dipakai modul ini — cukup diverifikasi lewat instalasi (G1) + Tour test (G2), tidak perlu perubahan kode. |
| DIFF-05 (override core `onchange_partner_id`) | Rendah | Diverifikasi langsung — core method masih ada nama sama, perilaku override total (BSL-005) konsisten tidak berubah. |
| DIFF-06 (`type='json'` deprecated) | Rendah | Tidak breaking, cleanup opsional. |
| DIFF-04, 07, 08, 09, 10 | Rendah/Tidak berlaku | Dikonfirmasi bersih/stabil dari grep+cross-check langsung. |

**Kesimpulan step 2:** migrasi ini **BUKAN** "port trivial" seperti kelihatannya dari scan awal §2b intake (tidak ada `attrs=`/`<tree>`/JSON field) — ada **1 file JavaScript (`purchase_product_field.js`) dengan 2 breaking change pasti** (DIFF-01, DIFF-02) yang butuh rewrite signifikan mengikuti pola native 19.0 (format many2one objek + hook `useMatrixConfigurator`). Sisanya (Python, view XML, 5 komponen Owl dialog lain, override `onchange_partner_id`) dikonfirmasi bersih/stabil — semua item step 2 sudah terverifikasi, tidak ada TODO tersisa. Siap lanjut ke Step 3 (Migration Spec).
