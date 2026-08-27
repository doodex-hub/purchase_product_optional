# UAT Checklist — Migrasi purchase_product_optional (18.0 → 19.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 18.0 sekarang, kecuali item yang
> memang disepakati berubah (tidak ada — migrasi ini murni port kompatibilitas, tidak ada fitur baru
> atau bug lama yang diperbaiki).
>
> **Dokumen ini awalnya adalah draft test script untuk dijalankan sendiri oleh business user/stakeholder**
> — bukan laporan hasil test AI. **PENYIMPANGAN EKSPLISIT dari prinsip default itu (dicatat transparan,
> bukan disembunyikan):** pemilik project ("Kuncoro") eksplisit menginstruksikan 2026-08-26 — "UAT
> dianggap selesai, percaya ai test" — sign-off di bawah didasarkan pada hasil test otomatis AI (Step
> 9 Dev Testing + Step 10 QA Testing: 13/13 unit/integration test pass, Tour end-to-end `tour succeeded`,
> code review 0🔴), **BUKAN eksekusi manual UI oleh business user**. Risiko residual yang diterima
> dengan keputusan ini: gap visual/UI (rendering halus, label, posisi tombol) yang cuma bisa ditangkap
> mata manusia TIDAK PERNAH benar-benar diverifikasi visual — AI-interaktif (Claude Browser) sudah
> dicoba dan gagal di Step 10 (pane tidak compositing, lihat `10_qa/10_BUSINESS_FLOW_MIGRATION.md`).
> Skenario T-01..T-03 di bawah tetap diisi Status berdasarkan evidence AI yang paling dekat
> merepresentasikan tiap skenario (Tour test untuk T-01, unit test untuk T-02, TIDAK ADA evidence
> untuk T-03 — lihat catatan per-skenario).

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `purchase_product_optional` versi `19.0.1.0.0` sudah terinstall di environment
      staging/UAT Odoo 19.0 (bukan environment Docker sementara yang dipakai AI untuk testing —
      environment itu sudah dimatikan setelah step 10).
- [ ] Login sebagai user dengan akses Purchase (bukan cuma Administrator) — role Purchase
      User/Manager sesuai yang biasa dipakai staf pembelian sehari-hari.
- [ ] Minimal 1 vendor (Contact) dengan Purchase Currency terisi.
- [ ] Minimal 1 produk dengan "optional products" terkonfigurasi (produk yang saat dipilih di baris
      PO akan membuka dialog "Configure your product").
- [ ] Minimal 1 produk dengan `product.supplierinfo` (harga khusus vendor) terisi untuk vendor di atas.
- [ ] Database yang dipakai UAT sebaiknya salinan/staging, bukan database produksi asli.

## Skenario Test (Test Script)

### T-01: Buat Purchase Order dengan konfigurasi produk & optional product

**Data dummy yang perlu dientri:** Vendor mana saja yang sudah punya Purchase Currency; produk yang
punya optional products (tanyakan tim produk mana yang biasa dipakai kalau tidak yakin).

**Evidence AI (bukan eksekusi manual):** Tour test `purchase_product_optional_configurator_tour`
menjalankan PERSIS langkah 1-6 di bawah lewat Chrome headless asli (bukan simulasi/mock) —
`tour succeeded`, 15/15 langkah, log `docker-env/logs/odoo_test3.log` (2026-08-26).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka app **Purchase** → klik **New** | Form Request for Quotation baru terbuka | Tour step 1-3: menu Purchase terbuka, form baru dibuat | [x] Pass (evidence Tour, bukan manual) |
| 2 | Isi field **Vendor** | Vendor terpilih, currency PO ikut menyesuaikan (kalau vendor pertama kali dipilih) | Tour step 4-5: vendor "BACKFILL QA Vendor" terpilih | [x] Pass (evidence Tour, bukan manual) |
| 3 | Di tab Products, klik **Add a line**, ketik nama produk yang punya optional products, pilih dari dropdown | Dialog **"Configure your product"** langsung terbuka otomatis (bukan cuma baris kosong) | Tour step 6-9: dialog terbuka otomatis, modal-title "Configure your product" terkonfirmasi | [x] Pass (evidence Tour, bukan manual) |
| 4 | Di dalam dialog, klik **Add** pada salah satu produk optional yang ditawarkan | Produk optional itu tercentang/terpilih untuk ditambahkan | Tour step 10-11: "BACKFILL QA Optional Product" ditambahkan | [x] Pass (evidence Tour, bukan manual) |
| 5 | Klik **Confirm** | Dialog tertutup, DUA baris muncul di PO (produk utama + optional), masing-masing dengan nama produk yang benar (bukan kosong/"undefined") | Tour step 12-13: dialog tertutup, baris optional muncul dengan nama benar | [x] Pass (evidence Tour, bukan manual) |
| 6 | Klik **Save** (ikon awan/tombol Save) | PO tersimpan, judul PO berubah dari "New" jadi nomor PO (mis. P00123) | Tour step 14-15: Save diklik, breadcrumb tidak lagi "New" | [x] Pass (evidence Tour, bukan manual) |

### T-02: Harga otomatis mengikuti vendor

**Data dummy yang perlu dientri:** Produk yang punya harga khusus (supplierinfo) untuk vendor tertentu.

**Evidence AI (bukan eksekusi manual):** `TestConvertPrice` (3 unit test) memverifikasi logika
`convert_price()`/harga per-supplierinfo secara langsung ke database (bukan lewat klik UI) — pass,
`docker-env/logs/odoo_test3.log` (2026-08-26). Ini BUKAN bukti visual (tidak ada screenshot dialog
menampilkan angka harga yang benar ke mata manusia), murni verifikasi nilai balik function.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat PO baru dengan vendor yang punya harga khusus untuk suatu produk | — | Tidak dijalankan lewat UI — diverifikasi via unit test langsung ke method `convert_price()`/pencarian `supplierinfo` | [x] Pass (evidence unit test, BUKAN eksekusi UI manual) |
| 2 | Tambah baris dengan produk tersebut, buka dialog konfigurasi | Harga yang tampil di dialog SESUAI dengan harga khusus vendor itu (bukan harga jual standar) | Logika backend yang menghasilkan angka tersebut terverifikasi benar; tampilan visual angka di dialog TIDAK diverifikasi manusia | [x] Pass (evidence unit test, BUKAN eksekusi UI manual) |

### T-03: Edit ulang konfigurasi baris yang sudah tersimpan

**Data dummy yang perlu dientri:** Lanjutan dari PO di T-01 (belum di-Confirm PO-nya, masih draft).

**TIDAK ADA evidence AI untuk skenario ini** — sudah dicatat sebagai gap sejak Step 5
(`05b_TEST_PLAN_MIGRATION.md` AC-04-01) dan tetap gap sampai Step 10 (`10_qa/human_qa/02_MAIN_FLOW.md`
langkah 8-9). Tidak ada Tour test maupun unit test yang menjalankan alur "buka ulang baris yang sudah
dikonfigurasi". Kode terkait TIDAK diubah migrasi ini (perilaku diasumsikan identik 18.0 berdasarkan
analisis kode, BUKAN eksekusi), risiko dinilai rendah — tapi ini **benar-benar belum pernah dijalankan**,
beda dari T-01/T-02 yang setidaknya punya evidence eksekusi nyata.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka kembali PO draft dari T-01 (belum dikonfirmasi ke vendor) | Baris produk yang sudah dikonfigurasi masih terlihat lengkap | — | [ ] Tidak terverifikasi — tidak ada evidence AI maupun manual |
| 2 | Klik ikon edit/pensil di baris produk yang sudah dikonfigurasi (kalau tersedia) | Dialog "Configure your product" terbuka LAGI dengan data yang sudah dipilih sebelumnya (bukan mulai dari kosong) | — | [ ] Tidak terverifikasi — tidak ada evidence AI maupun manual |

### T-04: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Currency PO tidak berubah saat ganti vendor dengan currency berbeda** — ini perilaku LAMA yang
  sengaja dipertahankan (bukan bug baru dari migrasi ini). Kalau saat testing kamu mengganti vendor
  dan currency PO tidak ikut berubah, **itu memang sudah begitu sejak versi 18.0 lama**, bukan sesuatu
  yang perlu dilaporkan sebagai kegagalan.
- **Field tersembunyi "ID" (id_vendor)** — ada field internal berlabel "ID" yang tidak terlihat di
  form (disembunyikan lewat styling), dipakai sistem untuk keperluan teknis. Tidak ada aksi user
  yang diperlukan terkait ini.
- **Dua dialog terbuka bersamaan (kasus jarang)** — kalau ada produk yang SEKALIGUS punya banyak
  varian (grid) DAN optional products, secara teori bisa muncul dua dialog konfigurasi tumpang
  tindih. Ini KETERBATASAN DESAIN LAMA yang sudah ada sejak versi sebelumnya, bukan sesuatu yang
  diperbaiki di migrasi ini. Kalau ketemu kasus ini saat UAT, silakan laporkan sebagai catatan
  (bukan kegagalan blocking) — lihat `10_qa/human_qa/04_NEGATIVE.md` untuk detail teknis.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Buat PO + dialog konfigurator + optional product | T-01 | [x] Pass | Evidence Tour test (AI), bukan eksekusi manual — lihat catatan penyimpangan di atas |
| 2 | Harga per-vendor | T-02 | [x] Pass | Evidence unit test (AI), bukan eksekusi manual — logika terverifikasi, tampilan visual TIDAK diverifikasi manusia |
| 3 | Edit ulang konfigurasi | T-03 | ⚠️ **Tidak terverifikasi** | Tidak ada evidence AI maupun manual — gap sejak Step 5, risiko dinilai rendah dari analisis kode (tidak diubah migrasi ini), TAPI genuinely belum pernah dijalankan sama sekali |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima bahwa migrasi ini TIDAK mengubah/memperbaiki:

- Bug currency PO tidak sinkron dengan vendor (BSL-005/006) — dipertahankan apa adanya, dikonfirmasi
  eksplisit oleh dev sebelumnya.
- Keterbatasan desain "dua dialog terbuka bersamaan" untuk produk matrix+optional sekaligus — sudah
  ada sejak versi lama, tidak diperbaiki di migrasi ini.
- Field `product_add_mode` yang tidak pernah aktif secara teknis (tidak berdampak ke user, murni
  warning internal saat instalasi).

## Prasyarat Sebelum Go-Live Produksi

- [ ] **Rehearsal upgrade sungguhan belum dilakukan** (migrasi ini "port kode saja", bukan upgrade
      instance dengan data produksi asli, sesuai kesepakatan awal `01a_MIGRATION_INTAKE.md` §3) —
      kalau instance produksi nantinya di-upgrade beneran (bukan instalasi baru), rehearsal upgrade
      dengan salinan data produksi WAJIB dilakukan terpisah dari migrasi kode ini.
- [ ] Backup database produksi sebelum upgrade nyata (kalau berlaku).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Pemilik project | Kuncoro | 2026-08-26 | *(instruksi verbal/chat: "UAT dianggap selesai, percaya ai test")* |

> **PENYIMPANGAN DARI PRINSIP DEFAULT (dicatat transparan, bukan disembunyikan):** sign-off ini
> BUKAN berdasarkan eksekusi tangan sendiri oleh business user — pemilik project eksplisit
> menginstruksikan menerima hasil test AI (Step 9 Dev Testing + Step 10 QA Testing) sebagai dasar
> kelulusan UAT, 2026-08-26. Risiko residual yang diterima dengan keputusan ini: T-01/T-02 punya
> evidence eksekusi nyata (Tour + unit test) tapi bukan verifikasi visual manusia; **T-03 (edit ulang
> konfigurasi) sama sekali TIDAK ada evidence eksekusi apapun**, murni asumsi dari analisis kode tidak
> berubah. Kalau di kemudian hari muncul isu terkait alur T-03 atau gap visual/UI, ini adalah risiko
> yang SUDAH diketahui dan disetujui secara sadar saat sign-off ini — bukan sesuatu yang luput
> tak terduga.
