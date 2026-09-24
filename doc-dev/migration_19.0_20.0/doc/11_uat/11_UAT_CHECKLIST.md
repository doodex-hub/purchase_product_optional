# UAT Checklist — Migrasi purchase_product_optional (19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`, `CROSS_VERSION_COMPARE.md`
**Tanggal:** 2026-09-24

> Kriteria sukses: user TIDAK merasakan bedanya dibanding 19.0, kecuali item yang disepakati/terpaksa
> berubah (lihat "Review Item Out-of-Scope").
>
> **PENYIMPANGAN EKSPLISIT dari prinsip default (dicatat transparan):** pemilik project (Kuncoro)
> menginstruksikan 2026-09-24 — *"lanjut step 11, sign-off percaya test ai yang sudah dilakukan"*.
> Kolom Actual/Status di bawah diisi dari **evidence AI**, BUKAN eksekusi tangan business user:
> Step 9 (21/21 test + Tour 17 langkah, Community dan Enterprise 20) dan Step 10 (Cross-Version-Compare
> live 19.0 vs 20.0 dengan Playwright, 9 skenario, screenshot di `10_qa/screenshots/`). Beda dari sign-off
> 18→19: kali ini ada verifikasi **visual** (screenshot 19 vs 20 dibandingkan, menemukan & memperbaiki
> regresi ikon RMV-02) dan T-03 (edit ulang) **sudah punya evidence eksekusi**. Risiko residual yang
> diterima: tidak ada pengguna nyata yang mencoba dengan data/kebiasaan kerja sehari-hari; UI diuji di
> resolusi desktop 1280 px saja; data produksi tidak pernah dipakai (port kode saja).

---

## Persiapan Sebelum UAT (Precondition & Data)

*(untuk dipakai kalau business user ingin menjalankan sendiri di staging — `10_qa/human_qa/` berisi versi
singkat per level)*

- [x] Modul `purchase_product_optional` `20.0.1.0.0` terinstall — di environment Docker AI (Community dan
      Enterprise 20); **staging nyata belum**.
- [ ] Login sebagai user Purchase (bukan Administrator) — evidence AI memakai admin.
- [x] Data: vendor "QA Vendor A" (harga khusus) & "QA Vendor B"; produk "QA Main Product" (harga vendor
      A 80, B 90, standar 100) dengan optional "QA Optional Product" (harga vendor A 40, standar 50),
      "QA Exclusion Product" (Size Small tidak boleh dengan Finish Matte), "QA Types Product" (dropdown,
      pills +5, warna, checkbox, nilai custom); "QA Configurable Product" (warna Merah/Biru).
- [x] Database salinan/staging — DB Docker sekali pakai, sudah dihapus.

## Skenario Test

### T-01: Buat PO dengan konfigurasi produk & optional product

**Data:** Vendor = QA Vendor A, produk = QA Main Product, optional = QA Optional Product.
**Evidence:** Step 10 S-01/S-03 (19 vs 20 identik) + Tour Step 9.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Purchase → New, isi Vendor "QA Vendor A" | Form RFQ baru | Sesuai (AI) | [x] Pass (evidence AI) |
| 2 | Add a product → "QA Main Product" | Dialog "Configure your product" terbuka otomatis, ikon −/+ dan "+ Add" terlihat | Sesuai setelah fix ikon RMV-02 | [x] Pass (evidence AI) |
| 3 | Klik "+ Add" pada QA Optional Product | Optional pindah ke atas, Total $120 | Total $120 | [x] Pass (evidence AI) |
| 4 | Confirm → Save | 2 baris (80 dan 40), nomor PO muncul | Sesuai, sama dengan 19.0 | [x] Pass (evidence AI) |

### T-02: Harga mengikuti vendor

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Vendor A → QA Main Product | Main $80, QA Optional Product $40 | $80 / $40 (19 dan 20) | [x] Pass (evidence AI) |
| 2 | Vendor B → QA Main Product | Main $90, optional tanpa harga vendor B = standar $50 | $90 / $50 (19 dan 20) | [x] Pass (evidence AI) |

### T-03: Edit ulang konfigurasi baris tersimpan

**Data:** PO tersimpan berisi baris "QA Configurable Product" warna Merah.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka PO, klik baris, klik ikon pensil di kolom Product | Grid varian dan dialog "Configure your product" terbuka dengan Merah terpilih | Sesuai (19 dan 20 identik) | [x] Pass (evidence AI, Step 10 S-07) |
| 2 | Tutup grid (✕), Cancel di configurator, Save | Baris tetap, PO tersimpan | Sesuai | [x] Pass (evidence AI) |

### T-04: Pilihan atribut & eksklusi

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Di optional "QA Exclusion Product" pilih Matte (Size Small) | Pesan "This option or combination of options is not available", tombol Add nonaktif | Sesuai | [x] Pass (evidence AI, S-04) |
| 2 | Pilih Large | Kombinasi valid lagi | Sesuai | [x] Pass (evidence AI) |
| 3 | "QA Types Product": ubah dropdown, pills (badge +$5), warna, checkbox, nilai custom "Hello QA" → Confirm → Save | Semua tampil & bisa dipilih, baris tersimpan dengan nilai custom | Sesuai, data sama dengan 19.0 | [x] Pass (evidence AI, S-09) |

### T-05: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa / Perilaku Lama (Informasi, Bukan Kegagalan)

- **Currency PO tidak ikut currency vendor** saat ganti vendor — perilaku lama sejak 17.0 (BSL-005/006),
  dibuktikan unit test.
- **Produk ber-varian membuka dua dialog** (grid + configurator); kalau setelah mengisi grid user menekan
  **Cancel** di configurator, Save gagal "Oops!" — **sama persis di 19.0** (RMV-03). Tutup dengan ✕ atau
  Confirm aman.
- **Optional product ber-varian tampil $0.00** dan pilihan atribut non-varian tidak tersimpan di baris —
  sama di 19.0 (RMV-05).
- **Tampilan standar Odoo 20 yang berubah** (bukan modul): label varian "(Red)" tidak tampil di bawah
  nama produk di baris PO, judul grid = nama produk, gaya tombol (RMV-04).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario | Status | Catatan |
|---|---|---|---|---|
| 1 | Buat PO + dialog + optional | T-01 | [x] Pass | Evidence AI (Tour + Playwright 19 vs 20) |
| 2 | Harga per-vendor | T-02 | [x] Pass | Evidence AI, verifikasi angka tampil di dialog |
| 3 | Edit ulang konfigurasi | T-03 | [x] Pass | Evidence AI — gap T-03 dari 18→19 tertutup |
| 4 | Atribut & eksklusi | T-04 | [x] Pass | Evidence AI |

## Review Item Out-of-Scope

Pemilik modul sudah mengonfirmasi (2026-09-24, `FINDINGS.md`):

- Eksklusi atribut lintas-produk hilang di Odoo 20 (platform) — tidak dipakai produksi (MF-03).
- Aset App Store dari branch rilis `19.0` tidak di-port; diterapkan saat membuat branch rilis `20.0` (MF-01).
- Bug/quirk lama dipertahankan apa adanya (MF-02, RMV-03, RMV-05).

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan dengan salinan data produksi — belum dilakukan (migrasi ini port kode
      saja). Wajib kalau produksi di-upgrade, bukan install baru.
- [ ] Backup database produksi sebelum upgrade nyata.
- [x] README modul direview: "Odoo version" diperbarui 17.0 → 20.0 (root & modul).
- [ ] Rekomendasi: jalankan `10_qa/human_qa/01_SMOKE.md` + `02_MAIN_FLOW.md` sekali di staging
      Enterprise dengan user Purchase non-admin.
- [ ] Branch rilis `20.0`: terapkan packaging store (MF-01).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Pemilik project | Kuncoro | 2026-09-24 | *(instruksi chat: "lanjut step 11, sign-off percaya test ai yang sudah dilakukan")* |

> Sign-off ini BUKAN hasil eksekusi tangan business user — lihat catatan penyimpangan di atas. Risiko
> residual (tanpa uji pengguna nyata, tanpa data produksi, admin-only) diterima sadar oleh pemilik project.

## Penutupan Migrasi

- [x] `doc/MIGRATION_CLOSED.md` ditulis dengan SHA commit penutupan (lihat file itu).
