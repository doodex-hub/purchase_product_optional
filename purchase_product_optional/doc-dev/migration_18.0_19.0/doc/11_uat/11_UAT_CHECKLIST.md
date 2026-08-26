# UAT Checklist — Migrasi purchase_product_optional (18.0 → 19.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 18.0 sekarang, kecuali item yang
> memang disepakati berubah (tidak ada — migrasi ini murni port kompatibilitas, tidak ada fitur baru
> atau bug lama yang diperbaiki).
>
> **Dokumen ini adalah draft test script untuk DIJALANKAN SENDIRI oleh business user/stakeholder** —
> bukan laporan hasil test AI. Kolom Actual/Status di bawah SENGAJA dikosongkan.

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

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka app **Purchase** → klik **New** | Form Request for Quotation baru terbuka | | [ ] Pass [ ] Fail |
| 2 | Isi field **Vendor** | Vendor terpilih, currency PO ikut menyesuaikan (kalau vendor pertama kali dipilih) | | [ ] Pass [ ] Fail |
| 3 | Di tab Products, klik **Add a line**, ketik nama produk yang punya optional products, pilih dari dropdown | Dialog **"Configure your product"** langsung terbuka otomatis (bukan cuma baris kosong) | | [ ] Pass [ ] Fail |
| 4 | Di dalam dialog, klik **Add** pada salah satu produk optional yang ditawarkan | Produk optional itu tercentang/terpilih untuk ditambahkan | | [ ] Pass [ ] Fail |
| 5 | Klik **Confirm** | Dialog tertutup, DUA baris muncul di PO (produk utama + optional), masing-masing dengan nama produk yang benar (bukan kosong/"undefined") | | [ ] Pass [ ] Fail |
| 6 | Klik **Save** (ikon awan/tombol Save) | PO tersimpan, judul PO berubah dari "New" jadi nomor PO (mis. P00123) | | [ ] Pass [ ] Fail |

### T-02: Harga otomatis mengikuti vendor

**Data dummy yang perlu dientri:** Produk yang punya harga khusus (supplierinfo) untuk vendor tertentu.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat PO baru dengan vendor yang punya harga khusus untuk suatu produk | | | [ ] Pass [ ] Fail |
| 2 | Tambah baris dengan produk tersebut, buka dialog konfigurasi | Harga yang tampil di dialog SESUAI dengan harga khusus vendor itu (bukan harga jual standar) | | [ ] Pass [ ] Fail |

### T-03: Edit ulang konfigurasi baris yang sudah tersimpan

**Data dummy yang perlu dientri:** Lanjutan dari PO di T-01 (belum di-Confirm PO-nya, masih draft).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka kembali PO draft dari T-01 (belum dikonfirmasi ke vendor) | Baris produk yang sudah dikonfigurasi masih terlihat lengkap | | [ ] Pass [ ] Fail |
| 2 | Klik ikon edit/pensil di baris produk yang sudah dikonfigurasi (kalau tersedia) | Dialog "Configure your product" terbuka LAGI dengan data yang sudah dipilih sebelumnya (bukan mulai dari kosong) | | [ ] Pass [ ] Fail |

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
| 1 | Buat PO + dialog konfigurator + optional product | T-01 | [ ] Pass [ ] Fail | |
| 2 | Harga per-vendor | T-02 | [ ] Pass [ ] Fail | |
| 3 | Edit ulang konfigurasi | T-03 | [ ] Pass [ ] Fail | |

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
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan
> menyetujui.
