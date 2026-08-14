# Smoke Test — purchase_product_optional

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain, balik ke step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~5 menit.
**Sumber:** skenario `S-01`, `S-02` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## 1. Produk configurable (atribut + optional products)

```
1. Buka Purchase > Orders > Requests for Quotation > New.
2. Pilih Vendor apapun yang punya harga (supplierinfo) untuk produk test.
3. Di tab Products, klik "Add a product", cari produk yang punya beberapa atribut
   (contoh: "Customizable Desk").
4. Pilih produk itu — akan muncul dialog "Configure your product" (kadang bertumpuk
   dengan dialog grid "Choose Product Variants" di belakangnya — ini NORMAL, lihat
   04_NEGATIVE.md untuk detail bug warisan terkait).
5. Pilih atribut (misal Legs=Steel, Color=White).
6. Klik "+Add" pada salah satu optional product yang muncul di bawah (misal
   "Conference Chair").
7. Klik "Confirm".
```

**Harus terjadi:** Baris PO terisi dengan produk utama + optional product yang ditambahkan,
harga terisi, dialog tertutup, TIDAK ADA error merah di layar.

## 2. Produk sederhana (tanpa atribut/optional)

```
1. Di RFQ yang sama (atau RFQ baru), klik "Add a product".
2. Cari produk sederhana yang TIDAK punya varian (contoh: "Chair floor protection").
3. Pilih produk itu.
```

**Harus terjadi:** Baris PO LANGSUNG terisi produk itu, TIDAK ADA dialog apapun yang
muncul (beda dengan langkah 1 di atas).

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-07-30 | Mode B, docker 18.0 (`purchase_product_optional_18_demo`) | Claude (AI-interaktif) | ✅ Pass | Produk "Customizable Desk" (S-01) & "Chair floor protection" (S-02) — lihat `10_BUSINESS_FLOW_MIGRATION.md` S-01/S-02 untuk bukti lengkap |
