# UAT Checklist — Migrasi purchase_product_optional

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-24

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 17.0, kecuali bug lama (lihat "Item yang Sengaja Tidak Diperbaiki" di bawah) yang memang disepakati tetap ada.

---

## Persiapan Sebelum UAT

- [ ] Modul `purchase_product_optional` versi 18.0 sudah terinstall di environment staging/UAT (bukan hasil Docker testing AI — instalasi terpisah di instance yang akan dipakai UAT).
- [ ] Login sebagai user dengan role Purchase User (Buyer) biasa — bukan cuma Administrator.
- [ ] Minimal 1 vendor (Contact) dengan "Purchase Currency" diisi.
- [ ] Minimal 1 produk dengan atribut varian/optional products sudah dikonfigurasi (Sales > Products > tab Optional Products / Attributes).
- [ ] Minimal 1 produk dengan Vendor Pricelist (`product.supplierinfo`) yang menyebut vendor di atas.
- [ ] Database yang dipakai adalah **salinan/staging**, bukan database produksi asli.

## Skenario Test

### T-01: Buat Purchase Order dan konfigurasi produk

**Data dummy yang perlu dientri:**
- Vendor: pilih vendor yang sudah disiapkan di atas.
- Produk: pilih produk yang punya optional products.
- Quantity: 1.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Purchase > Orders > New | Form Purchase Order baru terbuka | | [ ] Pass [ ] Fail |
| 2 | Isi field Vendor dengan vendor dummy | Vendor terpilih | | [ ] Pass [ ] Fail |
| 3 | Di baris produk, ketik nama produk dummy dan pilih | Dialog "Configure your product" terbuka OTOMATIS (bukan langsung masuk sebagai baris biasa) | | [ ] Pass [ ] Fail |
| 4 | Di dalam dialog, klik "Add" pada salah satu optional product yang muncul di daftar | Optional product tertambah ke daftar yang akan disertakan | | [ ] Pass [ ] Fail |
| 5 | Klik tombol "Confirm" | Dialog tertutup, DUA baris (produk utama + optional) muncul di Purchase Order | | [ ] Pass [ ] Fail |
| 6 | Klik "Save" | Purchase Order tersimpan (judul berubah dari "New" ke nomor PO) | | [ ] Pass [ ] Fail |

### T-02: Harga mengikuti vendor yang dipilih

**Data dummy:** produk dengan Vendor Pricelist khusus (harga beda dari harga standar produk).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat PO baru dengan vendor yang PUNYA harga khusus di Vendor Pricelist produk tsb | — | | |
| 2 | Tambah baris dengan produk itu, buka dialog konfigurator | Harga yang tampil di dialog = harga dari Vendor Pricelist, BUKAN harga standar produk | | [ ] Pass [ ] Fail |

### T-03: Edit ulang konfigurasi baris yang sudah tersimpan

**Data dummy:** lanjutan dari PO di T-01 (belum di-confirm PO-nya, masih draft).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pada baris yang sudah dikonfigurasi (hasil T-01), cari cara untuk membuka ulang konfigurasinya (biasanya ikon pensil/edit di baris) | Dialog "Configure your product" terbuka lagi dengan pilihan yang SAMA seperti sebelumnya tersimpan | | [ ] Pass [ ] Fail |

### T-04: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Currency PO tidak otomatis berubah saat ganti vendor** — ini bug lama yang SENGAJA dipertahankan (lihat "Item yang Sengaja Tidak Diperbaiki" di bawah), BUKAN sesuatu yang perlu dilaporkan sebagai kegagalan test.
- **Kombinasi produk matrix (banyak varian) + optional products sekaligus** — kasus jarang, ada risiko dua dialog terbuka bersamaan (bug desain lama, identik 17.0). Kalau kebetulan menemui produk seperti ini saat UAT dan melihat perilaku aneh, laporkan ke dev tapi ini BUKAN regresi dari migrasi.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Instalasi & tampilan dasar | (dicek sebelum T-01) | [ ] Pass [ ] Fail | |
| 2 | Dialog konfigurator (fitur inti) | T-01, T-03 | [ ] Pass [ ] Fail | |
| 3 | Harga per-vendor | T-02 | [ ] Pass [ ] Fail | |

## Item yang Sengaja Tidak Diperbaiki (Bug Lama, Dipertahankan)

Dikonfirmasi keputusan dev 2026-08-24 — item berikut adalah bug/quirk yang SUDAH ADA di versi 17.0, sengaja dipertahankan identik (bukan tugas migrasi untuk memperbaiki):

- Currency Purchase Order tidak otomatis mengikuti vendor yang dipilih (kecuali kebetulan sudah sama).
- Ganti partner PO bisa menimpa perilaku bawaan Odoo terkait payment term/fiscal position/incoterm.
- Field teknis `product_add_mode` tidak berfungsi (tidak terlihat di UI, tidak berdampak ke user).
- Harga di dialog konfigurator bisa tampil tanpa konversi currency (silent) kalau setting tertentu belum pernah disentuh.
- Di lingkungan multi-company, harga optional product bisa ikut menghitung harga dari company lain.

Stakeholder mengonfirmasi sadar & menerima kelima item di atas: [ ] Ya

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan di staging (bukan cuma database Docker testing AI) — **belum dilakukan di sesi ini**, dicatat eksplisit sebagai prasyarat sebelum go-live produksi.
- [ ] Backup database produksi sebelum upgrade nyata.
- [ ] T-03 dan T-04 (kombinasi matrix+optional) dijalankan minimal sekali secara manual sebelum go-live — belum tercakup otomatis (lihat `10_BUSINESS_FLOW_MIGRATION.md` S-05/S-06).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan menyetujui.
