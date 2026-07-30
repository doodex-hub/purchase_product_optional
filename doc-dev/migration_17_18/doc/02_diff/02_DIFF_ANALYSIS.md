# Diff & Compatibility Analysis — purchase_product_optional

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-07-29
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

> **Koreksi 2026-07-29 (setelah `native-target` DAN `enterprise18` (Enterprise 18.0,
> `D:\Kuncoro\doodex\repo\enterprise18`) sama-sama di-connect user):** draft pertama dokumen ini
> ditulis SEBELUM Enterprise 18.0 di-connect — user dengan tepat menegaskan itu tergesa. Setelah
> Enterprise 18.0 dicek juga, ditemukan **DIFF-07 (baru)** yang mengubah pemahaman F-01/MF-01 secara
> signifikan (lihat §1). Kesimpulan DIFF-02/DIFF-03 TIDAK berubah (malah makin dikonfirmasi — modul
> `sale_product_configurator` juga tidak ada di Enterprise 18.0, cuma tersisa
> `test_rental_product_configurators`), tapi §1 sekarang jadi lebih lengkap. Jangan anggap draft
> sebelum revisi ini sebagai final kalau dibaca dari histori.

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **[ESCALATION] `sale_product_configurator` TIDAK ADA LAGI di 18.0** — modulnya sendiri sudah
   dihapus dari Odoo 18.0 (hanya tersisa `test_sale_product_configurators`, modul test). Seluruh
   fungsinya (`_get_first_possible_combination`, `_create_product_variant`,
   `_get_variant_for_combination`, `_get_attribute_exclusions`, `optional_product_ids`) sudah
   DIPINDAH ke **Community** (`product`, sebagian `sale`). Manifest `depends` modul ini WAJIB diubah
   di Fase A1 (hapus `sale_product_configurator`, kemungkinan tidak perlu tambahan apapun karena
   `product` sudah jadi dependency transitif lewat `purchase`). Ini perubahan MEKANIS wajib untuk
   instalasi — bukan pilihan. Detail: DIFF-02.
2. **[ESCALATION] Field `result.purchase_warning` yang dibaca modul ini (`purchase_product_field.js:78`)
   TIDAK ditemukan sumbernya di 18.0 Community** — di 17.0 kemungkinan besar disuplai oleh bagian
   "purchase" dari `sale_product_configurator` (Enterprise, tidak bisa diverifikasi langsung karena
   source Enterprise tidak tersedia). Di 18.0, `sale` punya `sale_warning` (analog untuk SO), tapi
   TIDAK ada `purchase_warning` setara di `purchase`/`purchase_product_matrix` Community. **Perlu
   keputusan:** apakah ini fitur yang memang hilang di 18.0 (perlu verifikasi lewat install nyata
   Fase G1/G2), atau perlu Enterprise 18.0 source untuk cross-check apakah tersembunyi di modul lain.
   Detail: DIFF-03.
3. **[ESCALATION] `PurchaseOrderLineProductField` (dipatch modul ini) berubah struktur besar di
   18.0** — base class ganti jadi `ProductLabelSectionAndNoteField`, dan method
   `_editProductConfiguration` (yang di-override modul ini untuk re-buka dialog saat edit) **TIDAK
   ADA LAGI**, diganti `onEditConfiguration()`. Kalau modul tetap patch nama method lama, override itu
   jadi **dead code** — alur "edit konfigurasi yang sudah tersimpan" (BSL-009) akan diam-diam JATUH ke
   behavior default (`_openGridConfigurator`), bukan membuka dialog custom modul ini. Ini **wajib
   diperbaiki di step 6** (rename method di patch, mengikuti API baru) — perubahan MEKANIS untuk
   kompatibilitas, bukan perubahan business logic. Detail: DIFF-04.
4. Semua temuan di atas didapat dari `native-target` (`D:\Kuncoro\doodex\repo\odoo18`, Community
   only) yang baru di-connect user hari ini. **`native-source` (Odoo 17.0) dan Enterprise source
   (18.0) TIDAK di-connect** — beberapa detail (terutama poin 2) tidak bisa dipastikan 100% tanpa itu.
   Kalau ada Enterprise 18.0 source yang bisa di-connect nanti, DIFF-03 bisa diverifikasi lebih pasti.

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | `migration-tool/knowledge/version-diffs/17-to-18.md` — dipakai sebagai referensi umum (tree→list, Owl, `create()` multi-record, dll) |
| `dependency-compat/purchase_product_matrix/...` | Tidak | Belum ada — ditulis sebagai kandidat baru di `migration-records/` (§3) |
| `dependency-compat/sale_product_configurator/...` | Tidak | Belum ada — temuan §1/DIFF-02/DIFF-03 jadi kandidat pertama |

---

## 1. Perubahan Native (Core/Enterprise)

> Dicek terhadap `native-target` (`D:\Kuncoro\doodex\repo\odoo18`, Community, connected 2026-07-29).
> `native-source` (17.0) TIDAK di-connect — sebagian baris memakai `01b_BASELINE_SPEC.md` (perilaku
> 17.0 yang sudah diverifikasi eksekusi nyata via BACKFILL) sebagai baseline pembanding, bukan baca
> langsung source 17.0.

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `product_template.py:26-29` `convert_price` → `res.currency._convert()` | `addons/base/models/res_currency.py:273` `_convert(self, from_amount, to_currency, company=None, date=None, round=True)` | **Tidak berubah secara fungsional** — `company`/`date` TETAP optional dengan fallback (`company or self.env.company`, `date or fields.Date.context_today(self)`), identik prinsipnya dengan yang terbukti tidak crash di 17.0 (MF-05/BSL-018). Signature persis sama di 18.0. | Rendah — port 1:1 aman, MF-05 bisa ditutup sebagai **dikonfirmasi tetap valid di 18.0** (bukan cuma "belum diverifikasi") | `native-target` langsung |
| DIFF-02 | `__manifest__.py` `depends: [..., 'sale_product_configurator']` | Modul `sale_product_configurator` **DIHAPUS TOTAL** dari 18.0 (dicek: hanya ada `test_sale_product_configurators`, modul test unittest, bukan modul asli). Fungsinya (`_get_first_possible_combination`, `_create_product_variant`, `_get_variant_for_combination`, `_get_attribute_exclusions`) pindah ke **`product`** (Community, `product/models/product_template.py:865-1200`), field `optional_product_ids`+`get_single_product_variant` dasar juga di `product` (`:1413`), di-extend `sale` (`sale/models/product_template.py:211`, nambah `has_optional_products`/`is_combo`/`sale_warning`) | **Install-breaking** — `depends` menunjuk modul yang tidak ada akan gagal install total di 18.0 (`ModuleNotFoundError`/gagal resolusi dependency). WAJIB dihapus dari `depends` di Fase A1. `product` sudah jadi dependency transitif lewat `purchase`→`product`, jadi kemungkinan TIDAK perlu tambahan depends baru — perlu dikonfirmasi saat G1 (install test) | `native-target` langsung |
| DIFF-03 | `purchase_product_field.js:78` baca `result.purchase_warning` | Di 18.0: `sale` override `get_single_product_variant` cuma tambah `sale_warning` (pola field `sale_line_warn`/`sale_line_warn_msg`, `sale/models/product_template.py:230-234`). `purchase` PUNYA field analog (`purchase_line_warn`/`purchase_line_warn_msg`, `purchase/models/product.py:22-23`), TAPI **TIDAK ada override `get_single_product_variant` di `purchase`** yang mengubahnya jadi `purchase_warning` di response — dicek di `native-target` (Community) DAN `enterprise18` (Enterprise), `purchase_product_matrix` juga tidak override ini (lihat DIFF-07, comment eksplisit "purchase only uses matrix"). Konsisten dengan pola DIFF-07: Purchase core 18.0 sengaja TIDAK diberi mekanisme setara Sale | **Behavior kemungkinan hilang** — kalau produk punya `purchase_line_warn != 'no-message'`, modul ini TIDAK akan pernah menerima `result.purchase_warning` di 18.0 (key tidak pernah ada di response), jadi `WarningDialog`/notification block/warning (BSL-004/BSL-005) tidak akan pernah terpicu. **BUKAN error/crash** — cuma silent, fitur warning purchase hilang. Sama seperti DIFF-07, kemungkinan besar sumber `purchase_warning` di 17.0 adalah Enterprise `sale_product_configurator` yang sudah tidak ada di 18.0 sama sekali (Community maupun Enterprise) — **masih perlu verifikasi G1/G2 nyata** untuk 100% pasti (baca kode statis tidak bisa membuktikan sesuatu TIDAK PERNAH terjadi di semua kombinasi kondisi) | `native-target` + `enterprise18`, keduanya dicek |
| DIFF-04 | `purchase_product_field.js` patch `PurchaseOrderLineProductField` — override `_editProductConfiguration` (baris 97-102) | `purchase_product_matrix/static/src/js/purchase_product_field.js` (18.0): class SEKARANG `extends ProductLabelSectionAndNoteField` (dari `@account`, sebelumnya kemungkinan besar `Many2OneField`/base lain — tidak bisa dipastikan tanpa native-source 17.0). Method **`_editProductConfiguration` TIDAK ADA**, diganti `onEditConfiguration()` (baris 59-63) | **Override jadi dead code** — patch modul ini menambah method `_editProductConfiguration` yang TIDAK PERNAH dipanggil manapun di base class 18.0 (base memanggil `onEditConfiguration`). Alur "buka kembali dialog custom saat edit baris sudah terkonfigurasi" (BSL-009) akan DIAM-DIAM jatuh ke `_openGridConfigurator(true)` bawaan (grid, bukan dialog custom modul ini) — regresi behavior, BUKAN error. **WAJIB diperbaiki di Fase E (step 6)**: rename method di patch dari `_editProductConfiguration` → `onEditConfiguration`, ini perubahan mekanis untuk kompatibilitas (diizinkan per `CLAUDE.md` §Forbidden Actions), BUKAN perubahan business logic (behavior yang dipertahankan sama, cuma nama hook API yang mengikuti) | `native-target` langsung |
| DIFF-05 | `purchase_product_field.js` `_openGridConfigurator()` dipanggil TANPA argumen (AC-01-06) | 18.0: `_openGridConfigurator(edit)` (baris 65) — dipakai internal dengan `edit` boolean eksplisit (`_openGridConfigurator(false)`/`_openGridConfigurator(true)`) | **Kemungkinan aman** — `edit` jadi `undefined` kalau dipanggil tanpa argumen, falsy sama seperti `false` di titik-titik pemakaiannya (`if (edit) {...}` baris 74). Tidak crash, behavior kemungkinan identik. Tetap dicatat sebagai perubahan implisit yang perlu diverifikasi eksplisit di step 9 (bukan diasumsikan aman tanpa test) | `native-target` langsung |
| DIFF-06 | `views/purchase_order_views.xml` xpath `//tree/field[...]` (2×) + inner `<tree>` | `<tree>` dihapus dari 18.0, wajib `<list>` (`knowledge/version-diffs/17-to-18.md` §1, sudah dikonfirmasi install-breaking) | **Install-breaking** (sudah diketahui sejak step 1) — WAJIB Fase A2. Ditambahkan di sini untuk kelengkapan tabel DIFF, referensi sama | `knowledge/version-diffs/17-to-18.md` (sudah ada, dikonfirmasi ulang relevan) |
| DIFF-07 | `purchase_order_line.py:24-28` field `product_add_mode` (rusak, F-01/MF-01/BSL-008) | **Pola SAH & AKTIF di 18.0, tapi cuma di sisi Sale**: `sale_product_matrix/models/sale_order_line.py:9` — `product_add_mode = fields.Selection(related='product_template_id.product_add_mode', depends=['product_template_id'])` (persis pola yang coba ditiru field rusak modul ini, versi Purchase). `sale_product_matrix/models/product_template.py:20-25` override `get_single_product_variant()` MENAMBAHKAN `res['mode'] = self.product_add_mode` — inilah sumber key `result.mode` yang dibaca `purchase_product_field.js`/`sale_product_field.js`. **`purchase_product_matrix/models/purchase.py:150` (18.0) punya comment eksplisit: "configurable products are only configured through the matrix in purchase, so no need to check product_add_mode."** — desain SENGAJA: Purchase core TIDAK pernah dapat mekanisme `product_add_mode`/`result.mode` bawaan, beda dari Sale | **Klarifikasi penting untuk F-01/MF-01/BSL-007:** field `product_add_mode` yang rusak BUKAN sekadar field mati tak berdampak — desainnya jelas meniru pola `sale_product_matrix`, TAPI modul ini TIDAK PERNAH menambahkan bagian kedua yang wajib (override Python `get_single_product_variant` untuk inject `res['mode']`, seperti `sale_product_matrix` lakukan) — jadi bahkan kalau field-nya benar terdaftar, `result.mode` tetap TIDAK PERNAH terisi dari sisi modul ini sendiri. Satu-satunya kemungkinan `result.mode` pernah terisi di 17.0 adalah lewat Enterprise `sale_product_configurator` (yang sekarang tidak ada lagi di 18.0, baik Community maupun Enterprise — dicek `test_rental_product_configurators` adalah satu-satunya sisa, itu pun modul test) melakukan injeksi generik lintas model. **Implikasi migrasi:** BSL-007/AC-01-06 (cabang `_openGridConfigurator()` dipicu `result.mode`) kemungkinan besar SUDAH TIDAK PERNAH REACHABLE di 18.0 — bukan karena kode modul berubah, tapi karena satu-satunya sumber `result.mode` (mekanisme Enterprise 17.0) sudah hilang total dari platform. Ini beda dari DIFF-04/DIFF-05 (yang genuinely bisa diperbaiki) — DIFF-07 kemungkinan besar TIDAK BISA diperbaiki tanpa scope baru (menulis override `get_single_product_variant` sendiri di modul ini, yang berarti MENAMBAH kode baru, bukan port) | `native-target` (Community) DAN `enterprise18` (Enterprise, dicek eksplisit — `sale_product_configurator` juga tidak ada di Enterprise 18.0) |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak relevan — semua dependency modul ini native/Community/Enterprise Odoo, bukan OCA/third-party
(dikonfirmasi step 1 `01a_MIGRATION_INTAKE.md` §2).

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| `purchase` | Ya, ada di 18.0 (Community) | `native-target` | Rendah — model/field yang dipakai modul ini (`purchase.order`, `purchase.order.line`) masih ada |
| `purchase_product_matrix` | Ya, ada di 18.0 (Community, LGPL-3 — **bukan Enterprise seperti disangka di step 1**, koreksi: lihat `[STRUKTUR-FOLDER]`/catatan di bawah) | `native-target` | **Tinggi** — lihat DIFF-04/DIFF-05, `PurchaseOrderLineProductField` berubah struktur besar |
| `sale_product_configurator` | **TIDAK ADA** — modul dihapus, fungsinya pindah ke `product`/`sale` | `native-target` | **Kritis** — lihat DIFF-02/DIFF-03, wajib diubah di manifest + verifikasi ulang `purchase_warning` |

**Koreksi penting terhadap `01a_MIGRATION_INTAKE.md` §2:** dokumen itu menandai
`purchase_product_matrix` sebagai "Native/Enterprise" — setelah cek `native-target`, modul ini
ternyata **LGPL-3 (Community)**, bukan Enterprise. Ini tidak mengubah kesimpulan "bukan OCA", tapi
memperbaiki asumsi lisensi. Dicatat sebagai kandidat update ke `01a_MIGRATION_INTAKE.md` §2 (baris
tabel dependency) — bisa diperbaiki langsung karena masih dalam project yang sama (bukan lewat
curation).

**Koreksi tambahan (setelah `enterprise18` di-connect):** bukan cuma `purchase_product_matrix` —
`sale_product_matrix` dan `product_matrix` (dua modul yang jadi rujukan silang untuk memahami pola
`product_add_mode`/DIFF-07 di atas) JUGA Community, dicek langsung ada di `native-target`
(`odoo18/addons/`), TIDAK ada di `enterprise18`. Satu-satunya modul dependency 17.0 yang benar-benar
Enterprise DAN benar-benar hilang di 18.0 adalah `sale_product_configurator` (DIFF-02) — dikonfirmasi
GANDA sekarang (tidak ada di `native-target` Community, DAN tidak ada di `enterprise18`, cuma tersisa
`test_rental_product_configurators` sebagai modul test unrelated).

---

## 3. Temuan Baru — Migration Records

- [x] Temuan general (version-diff) → dicatat sebagai kandidat di
  `migration-tool/migration-records/purchase_product_optional_17_18/SUMMARY.md`: penghapusan total
  modul `sale_product_configurator` di 18.0 (fungsinya merge ke `product`/`sale` core) — ini
  kandidat KUAT untuk `knowledge/version-diffs/17-to-18.md` (general, bukan spesifik modul ini,
  berlaku untuk SEMUA modul yang depend `sale_product_configurator`).
- [x] Temuan per-dependency → kandidat `dependency-compat/purchase_product_matrix/17-to-18.md`
  (perubahan `PurchaseOrderLineProductField`: base class, rename `_editProductConfiguration`→
  `onEditConfiguration`, `_openGridConfigurator(edit)` butuh argumen) dan
  `dependency-compat/sale_product_configurator/17-to-18.md` (modul dihapus, lihat detail DIFF-02/03).
- [x] Promosi ke `knowledge/` HANYA lewat sesi curation terpisah (`templates/CURATION_PROMPT.md`) —
  BELUM dilakukan di step ini.

---

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-02 — `sale_product_configurator` dihapus | **Kritis** | Install-breaking, wajib Fase A1 |
| DIFF-06 — `<tree>`→`<list>` | **Kritis** | Install-breaking, wajib Fase A2 (sudah diketahui sejak step 1) |
| DIFF-04 — `_editProductConfiguration`→`onEditConfiguration` | **Tinggi** | Bukan install-breaking, tapi regresi fungsional diam-diam (BSL-009) kalau tidak diperbaiki di Fase E |
| DIFF-03 — `purchase_warning` kemungkinan hilang | **Tinggi** | Perlu verifikasi G1/G2 nyata; kalau benar hilang, ini `[GAP-MIGRASI]` yang butuh keputusan (terima hilang, atau re-implementasi manual) |
| DIFF-05 — `_openGridConfigurator()` tanpa argumen | Sedang | `purchase_product_matrix` (tanpa default `edit=false`) beda dari `sale_product_matrix` (punya default) — kemungkinan tetap aman (falsy), verifikasi step 9 |
| DIFF-07 — `product_add_mode`/`result.mode` cuma didukung di Sale, sengaja tidak di Purchase | **Tinggi (klarifikasi, bukan blocker baru)** | BSL-007/AC-01-06 kemungkinan besar sudah tidak reachable sejak sumbernya (Enterprise 17.0) hilang — bukan regresi migrasi, tapi perlu didokumentasikan supaya tidak dikira bug migrasi kalau ternyata tidak reachable saat step 9/10 |
| DIFF-01 — `_convert()` signature | Rendah | Dikonfirmasi tetap aman, menutup ketidakpastian MF-05 |
