# Main Flow Test — purchase_product_optional

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~10 menit.
**Sumber:** skenario `S-03`, `S-04`, `S-05` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## 1. Edit baris yang sudah dikonfigurasi

```
1. Buka PO/RFQ yang sudah punya baris produk configurable (hasil dari
   01_SMOKE.md langkah 1, atau PO lain yang sudah ada).
2. Klik baris produk itu untuk masuk mode edit.
```

**Harus terjadi:** Dialog "Configure your product" terbuka LAGI, dengan pilihan atribut
yang SAMA seperti yang sudah dipilih sebelumnya (misal Legs=Steel, Color=White tetap
ter-pilih) — BUKAN kosong/default.

## 2. Harga berdasarkan vendor (supplierinfo)

```
1. Pastikan produk test (misal "Customizable Desk") punya harga vendor khusus:
   buka Purchase > Products > pilih produk > tab Purchase > tambah baris Vendor
   dengan harga tertentu (misal Vendor "Azure Interior" @ $350.00).
2. Buat RFQ baru dengan Vendor yang SAMA persis dengan yang diisi di atas.
3. Tambah baris produk itu — dialog configurator terbuka.
```

**Harus terjadi:** Harga yang tampil di dialog SESUAI dengan harga vendor yang diisi
di langkah 1 (bukan $0.00, bukan harga standar produk).

## 3. Optional products — tambah & hapus

```
1. Di dialog configurator produk utama, klik "+Add" pada salah satu optional
   product yang muncul.
2. Kalau optional product itu SENDIRI punya optional product lain (nested),
   cek apakah optional product lanjutan itu ikut muncul.
3. Hapus salah satu baris optional product (kalau ada >1 sumber/parent untuk
   optional product yang sama) dan cek apakah baris itu TETAP ADA sampai
   SEMUA parent-nya dihapus.
```

**Harus terjadi:** Optional product bertambah tanpa duplikat, dan tidak ikut hilang
sampai semua sumbernya (parent) dihapus.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-07-30 | Mode B, docker 18.0 (`purchase_product_optional_18_demo`) | Claude (AI-interaktif) | ✅ Pass | Lihat `10_BUSINESS_FLOW_MIGRATION.md` S-03/S-04/S-05 — dialog reopen dengan data tersimpan (DIFF-04), harga $350.00 sesuai supplierinfo, optional products dikonfirmasi sesi sebelumnya |
