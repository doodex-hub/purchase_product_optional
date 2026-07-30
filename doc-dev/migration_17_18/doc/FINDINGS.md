# Findings — purchase_product_optional (migrasi 17.0 → 18.0)

> Cross-cutting, direkomendasikan (tidak kondisional) — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi. Baru ditambahkan ke `migration-tool`
> 2026-07-29 (lihat `migration-tool/ai-doc/OVERVIEW.md` §11), instance PERTAMA yang memakainya.

**Modul:** purchase_product_optional
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-07-29

---

## Beda Peran dari Mekanisme Lain

Lihat `migration-tool/templates/FINDINGS.md` untuk tabel lengkap. Ringkas: file ini konsolidasi
SEMUA gap lintas step (1-11) yang butuh keputusan manusia — `ESCALATION`/tag `[GAP]`/section gap
step 4/8 tetap dipakai di tempatnya masing-masing, WAJIB didaftarkan juga di sini kalau genuinely
butuh keputusan.

**Catatan khusus modul ini:** modul ini PERNAH lewat tool `doc-dev-backfill` sebelum migrasi ini
(2026-07-28) — sudah punya `doc-dev/backfill/FINDINGS.md` dengan ID `F-01`..`F-06` (skema ID tool
BEDA). Semua entry `MF-NNN` di bawah yang berasal dari situ MEREFERENSIKAN `F-NNN` aslinya secara
eksplisit — jangan bingung kedua skema ID ini.

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | Field `product_add_mode` tidak pernah terdaftar (bug parenthesis) | 1 (warisan `doc-dev/backfill` F-01) | `[DIWARISI-SOURCE]` | Rendah | Terbuka — pastikan tetap identik di 18.0 (step 6/9) |
| MF-02 | `onchange_partner_id` tidak pernah benar-benar mengubah `currency_id` | 1 (warisan F-02) | `[DIWARISI-SOURCE]` | Sedang | Terbuka — pastikan tetap identik di 18.0 |
| MF-03 | `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL — race condition | 1 (warisan F-03) | `[DIWARISI-SOURCE]` | Tinggi | Terbuka — pastikan tetap identik di 18.0 |
| MF-04 | Harga per-vendor bergantung pada `document.getElementById('id_vendor_0')` | 1 (warisan F-04) | `[DIWARISI-SOURCE]` | Sedang | Terbuka — **risiko migrasi konkret**, lihat detail |
| MF-05 | `convert_price` TIDAK crash tanpa `company`/`date` di 17.0 (hipotesis awal salah) | 1 (warisan F-05) | `[DIWARISI-SOURCE]` | Rendah | **✅ RESOLVED (Step 2, 2026-07-29)** — dikonfirmasi via `native-target`: signature `_convert()` 18.0 identik (company/date tetap optional dengan fallback), lihat `02_DIFF_ANALYSIS.md` DIFF-01 |
| MF-06 | Dialog configurator vs grid `purchase_product_matrix` tumpang tindih — baris utama bisa hilang | 1 (warisan F-06) | `[DIWARISI-SOURCE]` | **Tinggi** | Terbuka — pastikan tetap identik di 18.0, prioritas verifikasi step 9/10 |
| MF-07 | `sale_product_configurator` dihapus total di 18.0 — manifest `depends` install-breaking | 2 (2026-07-29) | `[GAP-MIGRASI]` | **Kritis** | Terbuka — wajib fix Fase A1 (step 6), lihat `02_DIFF_ANALYSIS.md` DIFF-02 |
| MF-08 | `result.purchase_warning` kemungkinan tidak pernah ada lagi di response 18.0 | 2 (2026-07-29) | `[GAP-MIGRASI]` | Tinggi | Terbuka — dicek `native-target` DAN `enterprise18`, keduanya tidak punya mekanismenya; tetap perlu verifikasi G1/G2 nyata, lihat DIFF-03 |
| MF-09 | `_editProductConfiguration` (dipatch modul) tidak ada lagi di base class 18.0 — jadi dead code | 2 (2026-07-29) | `[GAP-MIGRASI]` | Tinggi | Terbuka — wajib fix Fase E (rename ke `onEditConfiguration`), lihat DIFF-04 |
| MF-10 | `_openGridConfigurator()` dipanggil tanpa argumen, base class 18.0 minta `edit` boolean | 2 (2026-07-29) | `[GAP-MIGRASI]` | Sedang | Terbuka — kemungkinan aman (falsy), verifikasi step 9, lihat DIFF-05 |
| MF-11 | `product_add_mode`/`result.mode` (F-01/MF-01) — klarifikasi: mekanisme ini SENGAJA cuma ada di Sale, Purchase core tidak pernah dapat ini (dikonfirmasi komentar eksplisit di kode 18.0) | 2 (2026-07-29, setelah `enterprise18` connect) | `[GAP-MIGRASI]` | Tinggi (klarifikasi) | Terbuka — BSL-007/AC-01-06 kemungkinan tidak reachable sejak sumbernya (Enterprise 17.0) hilang; TIDAK diperbaiki (menambah override baru = di luar scope port kode), cukup didokumentasikan supaya tidak dikira regresi migrasi saat step 9/10, lihat DIFF-07 |
| MF-12 | Label duplikat "ID" (`id_vendor` vs `id`) di `purchase.order` — WARNING baru muncul di log G1 18.0 | 6 (2026-07-29, Checkpoint G1 #1, run nyata) | `[DIWARISI-SOURCE]` | Rendah (kosmetik) | **✅ RESOLVED (informasional)** — dikonfirmasi `string='ID'` sudah ada di source 17.0 (`purchase_order_line.py:7`), bukan regresi migrasi; kemungkinan besar 18.0 cuma lebih verbose soal warning ini, bukan behavior baru |
| MF-13 | `useService("rpc")` dihapus total di 18.0 — dialog crash `Service rpc is not available` | 6 (2026-07-29, Checkpoint G2, run nyata browser) | `[GAP-MIGRASI]` | **Kritis** | **✅ RESOLVED (2026-07-29)** — fix mekanis: pakai `import { rpc } from "@web/core/network/rpc"` + panggil `rpc(...)` langsung, mengikuti idiom native `sale/product_configurator_dialog.js` 18.0. Diverifikasi ulang di browser: error hilang. |
| MF-14 | `optional_product_ids`/`has_optional_products` tidak ada tanpa modul `sale` — fitur inti modul mati total | 6 (2026-07-29, Checkpoint G2, run nyata browser) | `[GAP-MIGRASI]` | **Kritis** | **✅ RESOLVED & TERVERIFIKASI (2026-07-29)** — eskalasi user, tambah `'sale'` ke `depends`, restart+retest browser konfirmasi dialog "Configure your product" (termasuk section optional products) tampil bersih tanpa error |

---

## Detail

### MF-01 — Field `product_add_mode` tidak pernah terdaftar di `purchase.order.line`
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-01**
(2026-07-28, tool `doc-dev-backfill`)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-008` (`01b_BASELINE_SPEC.md`), `F-01` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `purchase_product_optional/models/purchase_order_line.py:24-28`
**Deskripsi:** Kurung `Many2many()` tidak ditutup sebelum baris `product_add_mode = fields.Selection(...)`
— field ini jadi keyword-argument ke constructor, bukan field berdiri sendiri. Tidak terdaftar di
`_fields`, tidak dipakai di manapun (digrep 0 pemakaian).
**Dampak:** Dampak fungsional saat ini NOL, tapi terkait langsung ke MF-06 (kemungkinan dimaksudkan
mencegah dialog tumpang tindih).
**Rekomendasi:** TIDAK diperbaiki saat migrasi (prinsip Source of Truth) — port 1:1 apa adanya,
termasuk kurung yang tidak tertutup.
**Keputusan pemilik modul:** *(kosong — diisi manusia kalau perlu keputusan tambahan di luar
"pertahankan identik")*

---

### MF-02 — `onchange_partner_id` tidak pernah benar-benar mengubah `currency_id`
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari **F-02**
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-010`..`BSL-012` (`01b_BASELINE_SPEC.md`), `F-02` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `purchase_product_optional/models/purchase_order.py:9-22`
**Deskripsi:** Ketiga cabang if/elif/else method ini tidak pernah benar-benar meng-override
`currency_id` PO ke currency partner — bertentangan dengan docstring.
**Dampak:** Currency PO tidak auto-follow preferensi partner — user harus ganti manual.
**Rekomendasi:** TIDAK diperbaiki saat migrasi — port 1:1.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-03 — `currency_id` PO disimpan ke `ir.config_parameter` GLOBAL
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari **F-03**
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-016`, `BSL-017` (`01b_BASELINE_SPEC.md`), `F-03` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `purchase_order.py:9-22` (penulis) + `product_template.py:11-30` (pembaca, `convert_price`)
**Deskripsi:** `ir.config_parameter` singleton system-wide dipakai sebagai jembatan currency antara
`onchange_partner_id` dan `convert_price` — rawan race condition multi-user.
**Dampak:** Berpotensi user melihat harga terkonversi ke currency PO milik user LAIN, di lingkungan
multi-user concurrent. Belum ada bukti frekuensi nyata (butuh instrumentasi produksi).
**Rekomendasi:** TIDAK diperbaiki saat migrasi — port 1:1 (termasuk pola global-parameter-nya).
**Keputusan pemilik modul:** *(kosong)*

---

### MF-04 — Harga per-vendor bergantung pada `document.getElementById('id_vendor_0')`
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari **F-04**
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-024` (`01b_BASELINE_SPEC.md`), `F-04` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_configurator_dialog.js:41-43` + `purchase_order_line.py:7-11` +
`views/purchase_order_views.xml:27-36`
**Deskripsi:** Dialog membaca DOM langsung untuk tahu vendor PO, bukan lewat parameter eksplisit.
Rapuh terhadap perubahan konvensi id generation Odoo.
**Dampak — RISIKO MIGRASI KONKRET (beda dari MF-01/02/03 yang murni "pertahankan"):** kalau Odoo 18.0
mengubah skema `id` generation DOM untuk field form (belum dikonfirmasi — perlu dicek step 2/9), pola
`getElementById('id_vendor_0')` bisa return `null` → error runtime `Cannot read properties of null`
saat `.value` diakses — dialog gagal terbuka sama sekali. Ini BUKAN behavior yang dikonfirmasi ada di
17.0 (AC-06-02 belum pernah tereproduksi), tapi migrasi versi adalah PERSIS jenis perubahan yang bisa
memicu ini.
**Rekomendasi:** Port 1:1 dulu (jangan "sekalian" diperbaiki jadi prop eksplisit — itu perubahan
behavior/refactor, di luar scope port kode). **WAJIB diverifikasi eksplisit di step 9 (dev testing)**
dengan skenario buka dialog configurator setelah pilih vendor — kalau ternyata break di 18.0, ini jadi
`ESCALATION` baru (bug source vs breaking change platform yang genuinely butuh keputusan, bukan lagi
murni "pertahankan").
**Keputusan pemilik modul:** *(kosong)*

---

### MF-05 — `convert_price` TIDAK crash tanpa argumen `company`/`date` (hipotesis awal salah)
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari **F-05**
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-018` (`01b_BASELINE_SPEC.md`), `F-05` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_template.py:26-29`
**Deskripsi:** `_convert()` dipanggil tanpa `company`/`date` meski signature upstream 17.0
mensyaratkannya — dikonfirmasi 3× (Mode B run #1/#2/#7) TIDAK crash di build Odoo 17.0 yang dites.
**Dampak — PERLU VERIFIKASI ULANG DI 18.0:** signature `res.currency._convert()` bisa berbeda di
core Odoo 18.0 (default value argumen bisa berubah antar versi). TIDAK boleh diasumsikan otomatis
sama hanya karena 17.0 terbukti aman — ini murni asumsi belum-diverifikasi, beda dari MF-01/02/03/04
yang perilakunya sudah pasti (baik/buruk) dan cuma soal "pertahankan".
**Rekomendasi:** Cek `res.currency._convert()` signature 18.0 di step 2 (Diff Analysis) — kalau
berubah (mis. argumen jadi wajib beneran di 18.0), ini jadi `ESCALATION`/`[GAP-MIGRASI]` baru
(port kode 1:1 bisa genuinely crash di 18.0 walau aman di 17.0 — bukan lagi soal "pertahankan bug",
tapi soal "source tidak salah di 17.0 tapi tidak kompatibel murni karena versi platform").
**Keputusan pemilik modul:** *(kosong — tunggu hasil step 2)*

---

### MF-06 — Dialog configurator vs grid `purchase_product_matrix` tumpang tindih tanpa koordinasi
**Ditemukan di:** Step 1 (2026-07-29), diwarisi dari **F-06** (prioritas Tinggi, temuan paling
bernilai dari BACKFILL — dikonfirmasi live 2× reproduksi)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-020`, `BSL-025` (`01b_BASELINE_SPEC.md`), `F-06` (`doc-dev/backfill/FINDINGS.md`),
terkait `MF-01`/`BSL-008`
**Lokasi:** `purchase_product_field.js:55-95` (`_onProductTemplateUpdate`, `super()` tanpa syarat) +
`:104-154` (`_openProductConfigurator`)
**Deskripsi:** `super._onProductTemplateUpdate()` dipanggil TANPA SYARAT, berpotensi membuka grid
"Choose Product Variants" (`purchase_product_matrix`) BERSAMAAN dengan dialog custom "Configure your
product". Kalau user hanya berinteraksi dialog depan — baris produk UTAMA hilang total dari PO,
TANPA error apapun.
**Dampak:** **TINGGI** — bug fungsional nyata di alur pemakaian normal, bukan edge-case teoretis.
**Rekomendasi:** TIDAK diperbaiki saat migrasi (prinsip Source of Truth) — port 1:1, **WAJIB
direproduksi ulang di step 9/10 (18.0)** untuk konfirmasi behavior identik (bukan cuma diasumsikan
sama karena "kodenya sama") — interaksi dengan `purchase_product_matrix` versi 18.0 bisa saja
berubah, meskipun kode modul ini sendiri tidak diubah secara semantik.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-07 — `sale_product_configurator` dihapus total di 18.0
**Ditemukan di:** Step 2 (2026-07-29), dari `native-target` (`D:\Kuncoro\doodex\repo\odoo18`)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_DIFF_ANALYSIS.md` DIFF-02
**Lokasi:** `purchase_product_optional/__manifest__.py` (`depends`)
**Deskripsi:** Modul `sale_product_configurator` tidak ada lagi di addons 18.0 (dicek langsung) —
fungsinya (kombinasi produk, exclusion, create variant) pindah ke `product`/`sale` Community.
**Dampak:** Install gagal total kalau `depends` tidak diubah — modul yang di-depend tidak ditemukan.
**Rekomendasi:** Hapus `sale_product_configurator` dari `depends` di Fase A1 — `product` sudah jadi
dependency transitif lewat `purchase`, kemungkinan tidak perlu tambahan apapun. Konfirmasi lewat G1.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-08 — `result.purchase_warning` kemungkinan tidak pernah ada lagi di response 18.0
**Ditemukan di:** Step 2 (2026-07-29), dari `native-target`
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_DIFF_ANALYSIS.md` DIFF-03
**Lokasi:** `purchase_product_field.js:78`
**Deskripsi:** `sale` override `get_single_product_variant` di 18.0 cuma tambah `sale_warning`, bukan
`purchase_warning`. `purchase` punya field `purchase_line_warn`/`purchase_line_warn_msg` tapi TIDAK
override `get_single_product_variant` untuk memasukkannya ke response. Mekanisme asli `purchase_warning`
kemungkinan berasal dari bagian "purchase" Enterprise `sale_product_configurator` 17.0 yang tidak bisa
diverifikasi langsung (source Enterprise tidak connected).
**Dampak:** Kalau benar hilang — `WarningDialog`/notification block/warning (BSL-004/BSL-005) tidak
akan pernah terpicu di 18.0, silent (bukan crash).
**Rekomendasi:** Verifikasi nyata lewat G1/G2 (install + coba skenario produk dengan
`purchase_line_warn` diisi). Kalau terbukti hilang, eskalasi ke user: terima sebagai fitur yang
hilang karena perubahan platform (dicatat sebagai deviasi disengaja di `01a_MIGRATION_INTAKE.md` §5),
atau re-implementasi manual (override `get_single_product_variant` di modul ini sendiri untuk
menambah `purchase_warning`, kalau dirasa perlu — ini keputusan scope yang butuh persetujuan
eksplisit, bukan default).
**Keputusan pemilik modul:** *(kosong — tunggu verifikasi G1/G2)*

---

### MF-09 — `_editProductConfiguration` tidak ada lagi di base class 18.0
**Ditemukan di:** Step 2 (2026-07-29), dari `native-target`
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_DIFF_ANALYSIS.md` DIFF-04, terkait `BSL-009`
**Lokasi:** `purchase_product_field.js:97-102` (override modul ini)
**Deskripsi:** `PurchaseOrderLineProductField` 18.0 tidak lagi punya method `_editProductConfiguration`
— diganti `onEditConfiguration()`. Override modul ini jadi dead code (tidak pernah dipanggil).
**Dampak:** Alur re-edit baris yang sudah terkonfigurasi (BSL-009) diam-diam jatuh ke
`_openGridConfigurator(true)` bawaan, bukan dialog custom modul ini — regresi fungsional silent.
**Rekomendasi:** WAJIB diperbaiki Fase E (step 6) — rename method di patch mengikuti API baru. Ini
perubahan mekanis untuk kompatibilitas (diizinkan `CLAUDE.md` §Forbidden Actions), bukan perubahan
business logic.
**Keputusan pemilik modul:** *(kosong — rekomendasi cukup jelas, tapi tetap dicatat sebagai keputusan
resmi sebelum step 6 mengeksekusi)*

---

### MF-10 — `_openGridConfigurator()` dipanggil tanpa argumen `edit`
**Ditemukan di:** Step 2 (2026-07-29), dari `native-target`
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_DIFF_ANALYSIS.md` DIFF-05
**Lokasi:** `purchase_product_field.js` (baris pemanggilan `_openGridConfigurator()`, AC-01-06)
**Deskripsi:** Base class 18.0 `_openGridConfigurator(edit)` mengharapkan argumen boolean, dipakai di
`if (edit) {...}`. Modul ini memanggil tanpa argumen — `edit` jadi `undefined`, falsy, kemungkinan
behave sama seperti `false`.
**Dampak:** Kemungkinan aman (tidak crash, logic `if (edit)` tetap valid untuk `undefined`), tapi
belum diverifikasi eksekusi nyata.
**Rekomendasi:** Verifikasi eksplisit di step 9 (bukan diasumsikan aman) — kalau ternyata masalah,
tambahkan argumen eksplisit `false` di pemanggilan (perubahan mekanis, bukan business logic).
**Keputusan pemilik modul:** *(kosong — kemungkinan besar tidak perlu keputusan, cukup verifikasi)*

---

### MF-11 — `product_add_mode`/`result.mode` sengaja cuma didukung di Sale, bukan Purchase
**Ditemukan di:** Step 2 (2026-07-29), setelah `enterprise18` (Enterprise 18.0) di-connect user
(catatan: draft pertama step 2 sempat dianggap selesai TANPA cek Enterprise dulu — dikoreksi user)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_DIFF_ANALYSIS.md` DIFF-07, terkait langsung `MF-01`/`F-01`/`BSL-007`/`BSL-008`
**Lokasi:** `purchase_order_line.py:24-28` (field rusak) + `purchase_product_field.js` (baca
`result.mode`)
**Deskripsi:** `sale_product_matrix` (Community, 18.0) punya pola LENGKAP yang berfungsi:
field `product_add_mode` related (`sale_order_line.py:9`) + override Python
`get_single_product_variant()` yang inject `res['mode'] = self.product_add_mode`
(`product_template.py:20-25`). `purchase_product_matrix` (Community, 18.0) **punya komentar eksplisit
di kode**: *"configurable products are only configured through the matrix in purchase, so no need to
check product_add_mode"* (`models/purchase.py:150`) — desain SENGAJA, Purchase core tidak pernah
dapat mekanisme setara.
**Dampak:** Field `product_add_mode` di `purchase.order.line` (F-01, rusak) TERNYATA memang meniru
pola `sale_product_matrix` yang sah — TAPI modul ini tidak pernah menambahkan bagian kedua yang wajib
(override `get_single_product_variant` inject `mode`). Jadi bahkan kalau field-nya diperbaiki (yang
TIDAK boleh dilakukan sesuai prinsip Source of Truth), `result.mode` tetap tidak akan pernah terisi
dari modul ini sendiri. Satu-satunya sumber `result.mode` yang masuk akal di 17.0 adalah mekanisme
generik Enterprise `sale_product_configurator` — yang sekarang hilang total di 18.0 (Community
maupun Enterprise, lihat MF-07). **BSL-007/AC-01-06 (cabang grid-configurator via `result.mode`)
kemungkinan besar TIDAK PERNAH reachable, baik di 17.0 (kalau hipotesis ini benar) maupun DIPASTIKAN
tidak reachable di 18.0.**
**Rekomendasi:** TIDAK diperbaiki (menambah override baru = fitur baru, di luar scope port kode kecuali
disetujui eksplisit). Didokumentasikan supaya kalau step 9/10 menemukan cabang ini tidak pernah
ter-trigger, itu DIKENALI sebagai konsekuensi hilangnya platform Enterprise 17.0 — bukan disangka
bug migrasi/regresi kode modul ini.
**Keputusan pemilik modul:** *(kosong — informasional, kemungkinan tidak perlu keputusan aktif kecuali
ingin scope tambahan reimplementasi manual)*

---

### MF-12 — Label duplikat "ID" (`id_vendor` vs `id`) di `purchase.order`

**Ditemukan di:** Step 6 (2026-07-29), Checkpoint G1 #1 (install test nyata, Mode B, Docker 18.0)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `models/purchase_order_line.py:7` (`id_vendor = fields.Char(string='ID')`)
**Lokasi:** Log Odoo: `WARNING ... odoo.addons.base.models.ir_model: Two fields (id_vendor, id) of
purchase.order() have the same label: ID. [Modules: purchase_product_optional and purchase]`
**Deskripsi:** Field `id_vendor` diberi `string='ID'` eksplisit di source 17.0 (bukan perubahan
migrasi) — bertabrakan dengan label bawaan field `id`. Ditemukan lewat eksekusi nyata G1 (bukan
baca kode) karena baru kelihatan sebagai WARNING saat model benar-benar di-load ke registry.
**Dampak:** Kosmetik saja (label ganda di technical/debug view, mis. field selector) — TIDAK
mempengaruhi fungsi field (`id_vendor` tetap dipakai sebagai jembatan DOM, lihat MF-04). Field ini
memang sengaja tidak ditampilkan ke user (CSS `visibility: hidden`), jadi label yang salah pun
kemungkinan besar tidak pernah terlihat end-user normal.
**Rekomendasi:** TIDAK diperbaiki (prinsip Source of Truth — `string='ID'` sudah ada di 17.0, port
1:1). Dicatat murni sebagai informasi tambahan yang baru kelihatan lewat eksekusi G1, supaya kalau
warning yang sama muncul lagi di step 9/10, sudah dikenali sebagai warisan bukan regresi baru.
**Keputusan pemilik modul:** *(kosong — tidak butuh keputusan aktif, murni informasional)*

---

### MF-13 — `useService("rpc")` dihapus total di 18.0

**Ditemukan di:** Step 6 (2026-07-29), Checkpoint G2 (validasi runtime nyata via browser, Claude in
Chrome) — TIDAK terdeteksi oleh review statis Fase E (sintaks JS tetap valid, hanya rusak di runtime)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `product_configurator_dialog.js` (`setup()` + 4 call site: `_loadData`, `_createProduct`,
`_updateCombination`, `_getOptionalProducts`)
**Lokasi:** `purchase_product_optional/static/src/js/product_configurator_dialog/product_configurator_dialog.js`
**Deskripsi:** Pola `this.rpc = useService("rpc")` (dipakai luas di 17.0) tidak lagi terdaftar sebagai
service di 18.0 — dikonfirmasi di `odoo18/addons/web/static/src/core/network/rpc.js`, yang sekarang
mengekspor fungsi biasa `rpc(url, params)`, bukan service. Native `sale/product_configurator_dialog.js`
18.0 sudah memakai idiom baru ini (`import { rpc } from "@web/core/network/rpc"`).
**Dampak:** Dialog crash total begitu dibuka — `Error: Service rpc is not available` di
`ProductConfiguratorDialogPurchase.setup`. Ini KRITIS karena dialog configurator adalah fitur inti
modul, dan bug ini HANYA kelihatan lewat eksekusi browser nyata (G2) — review statis (Fase E) sempat
menyimpulkan file ini "tidak perlu perubahan" karena sintaksnya tetap valid.
**Rekomendasi (sudah dieksekusi):** Ganti ke `import { rpc } from "@web/core/network/rpc"` +
panggilan langsung `rpc(...)` di 4 tempat, hapus `this.rpc = useService("rpc")`. Perubahan mekanis
murni untuk kompatibilitas API, tidak mengubah business logic.
**Keputusan pemilik modul:** Tidak perlu — fix mekanis jelas, langsung dieksekusi & diverifikasi
berhasil di browser (error hilang pada percobaan ulang).
**Lesson untuk `migration-tool`:** validasi kuat untuk prinsip "G1 ≠ G2" — G1 (install test) tidak
akan pernah menangkap ini karena tidak membuka komponen Owl di browser nyata.

---

### MF-14 — `optional_product_ids`/`has_optional_products` hilang tanpa modul `sale`

**Ditemukan di:** Step 6 (2026-07-29), Checkpoint G2 (validasi runtime nyata via browser) — setelah
MF-13 diperbaiki, dialog terbuka tapi crash lagi di titik berbeda
**Tag:** `[GAP-MIGRASI]`
**Ref:** `MF-07` (`DIFF-02`, penghapusan `sale_product_configurator`), `02_DIFF_ANALYSIS.md`
**Lokasi:** `purchase_product_optional/controllers/main.py:90`
(`get_product_configurator_values_purchase`, akses `product_template.optional_product_ids`)
**Deskripsi:** Field `optional_product_ids` (`Many2many`) dan key `has_optional_products` (hasil
override `get_single_product_variant()`) HANYA didefinisikan di `sale/models/product_template.py`
(baris 53-59 dan 219-227) — tidak ada sama sekali di bare `product`/`purchase` 18.0 (dikonfirmasi
baca langsung `odoo18/addons/product/models/product_template.py`). Di 17.0, field ini otomatis
tersedia karena dependency lama `sale_product_configurator` menarik `sale` secara TRANSITIF —
dikonfirmasi lewat perbandingan log: environment 17.0 BACKFILL memuat 56 modul (termasuk `sale`,
urutan ke-49), environment 18.0 (setelah MF-07 fix, `sale_product_configurator` dihapus dari
`depends`) hanya memuat 51 modul, TANPA `sale` sama sekali.
**Dampak:** **KRITIS** — begitu `sale_product_configurator` dihapus dari `depends` (perbaikan yang
sendirinya benar untuk MF-07/DIFF-02), fitur "optional products" (separuh nama & fungsi inti modul
ini) mati total: `AttributeError: 'product.template' object has no attribute 'optional_product_ids'`
setiap kali dialog configurator dibuka untuk produk apapun. Ini efek samping tidak langsung dari fix
lain, bukan mekanisme yang sudah terdaftar di DIFF-01..07 sebelumnya — ditemukan murni lewat G2.
**Opsi yang diberikan ke user (format ESCALATION penuh):**
1. Tambah `'sale'` eksplisit ke `depends` — Risiko rendah, net footprint SAMA seperti 17.0 (sudah
   implisit tertarik di sana lewat `sale_product_configurator`), cuma sekarang eksplisit.
2. Terima sebagai regresi diketahui (fitur optional products non-fungsional tanpa Sales) — Risiko
   tinggi (hilang fitur inti), butuh sign-off eksplisit sebagai deviasi disengaja.
**Keputusan pemilik modul (2026-07-29):** **Opsi 1 — tambah `'sale'` ke `depends`.** Dieksekusi:
`__manifest__.py` `depends` → `['purchase', 'purchase_product_matrix', 'sale']`. `auto_install: True`
tetap konsisten dengan semantik 17.0 (auto-install baru terjadi kalau ketiga dependency + `sale`
sama-sama terinstall — persis behavior lama, cuma sekarang jelas di deklarasi).
**Lesson untuk `migration-tool`:** kelas risiko BARU yang belum tercatat sebelumnya — menghapus satu
dependency untuk fix install-blocking (DIFF-02 jenis) bisa diam-diam menghilangkan dependency LAIN
yang ditarik transitif olehnya, yang kodenya sendiri (tanpa diubah sama sekali) tetap bergantung
padanya. Static review (baca `depends` baru vs kode yang memakai field) tidak cukup — perlu langkah
eksplisit "untuk tiap dependency yang dihapus, cek modul APA SAJA yang ditarik olehnya secara
transitif, dan apakah kode module target memakai sesuatu dari situ."

**✅ Verifikasi ulang (2026-07-29, sesi sama, setelah restart container dengan `-u`):** `sale`
berhasil terinstall (log: 58→59 modul, tanpa error). Retest live via browser (PO baru, "Customizable
Desk" + vendor "Azure Interior"): dialog "Configure your product" terbuka BERSIH — Legs (Steel/
Aluminium/Custom), Color (swatch), DAN section "Add optional products" (Conference Chair, tombol
"+Add" berfungsi) semua tampil tanpa error. `AttributeError` (MF-14) dan `Service rpc is not
available` (MF-13) TIDAK muncul lagi. **MF-14 RESOLVED, terverifikasi eksekusi nyata.**

---

### Konfirmasi tambahan — MF-06/F-06 direproduksi identik di 18.0 (2026-07-29, sesi G2 sama)

Begitu MF-13/MF-14 beres, dialog terbuka — DAN grid "Choose Product Variants"
(`purchase_product_matrix`) ikut terbuka BERSAMAAN persis seperti F-06 (BACKFILL 17.0). Direproduksi
lewat skenario sama seperti backfill: pilih "Customizable Desk" (matrix-eligible) sebagai produk PO.
**Hasil identik dengan 17.0:** begitu user menyelesaikan alur lewat dialog custom (pilih Legs/Color,
tambah optional product "Conference Chair", klik Confirm) TANPA menyelesaikan grid dialog di
belakangnya — baris produk UTAMA ("Customizable Desk") hilang TOTAL dari PO, hanya "Conference
Chair" (optional product) yang tersisa di baris. **Tidak ada error toast/notification** — silent,
persis seperti dideskripsikan F-06/MF-06.

**Detail baru (belum pernah tercatat di BACKFILL 17.0):** console browser menunjukkan 3× error
`Error: Component is destroyed` (di `get_supplierinfo_id`, `get_product_update_price`,
`get_optional_product_prices` — semua ORM call `this.orm.call()` dalam `ProductConfiguratorDialogPurchase`)
saat grid dialog membuka DI ATAS dialog custom yang masih fetch data. Ini kemungkinan konsekuensi
Owl 2 (18.0) yang lebih strict soal component lifecycle (melempar error eksplisit kalau ORM call
resolve setelah component destroyed) dibanding Owl 1 (17.0) yang mungkin diam-diam menelan kondisi
serupa. **Tidak dianggap regresi baru** — akar masalah (dua dialog dibuka tanpa koordinasi) 100%
sama, cuma manifestasi console-nya lebih verbose di 18.0. Dicatat sebagai detail tambahan untuk
Step 9/10, bukan item yang perlu diperbaiki (tetap tunduk prinsip Source of Truth — F-06/MF-06
TIDAK diperbaiki saat migrasi).

**Catatan terpisah (belum dikonfirmasi cukup, kemungkinan bukan bug migrasi):** harga tampil `$0.00`
untuk kedua produk selama sesi test ini — kemungkinan besar karena database demo 18.0 yang baru
tidak punya `supplierinfo` custom untuk vendor "Azure Interior" pada produk-produk ini (setup harga
per-vendor di BACKFILL 17.0 dibuat manual khusus untuk test itu, tidak otomatis terbawa ke db demo
18.0 yang terpisah). Bukan bug kode — perlu setup data test yang sama untuk verifikasi AC-05-01 di
Step 10 (QA Testing) nanti, bukan diasumsikan sebagai regresi MF-04.

---

## Cara Pakai

Lihat `migration-tool/templates/FINDINGS.md` §Cara Pakai untuk aturan lengkap. Ringkas untuk project
ini: ID lanjut dari `MF-13` untuk finding BARU berikutnya (step 6 lanjutan-11). `MF-01`..`MF-12` di
atas TIDAK dihapus/diubah nomornya meski nanti ada temuan baru — cukup update kolom Status begitu
diverifikasi.
