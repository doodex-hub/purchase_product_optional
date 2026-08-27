# Main Flow Test — purchase_product_optional

**Level:** Main Flow + Detail (S-05 digabung di sini, satu-satunya skenario Detail).
**Estimasi waktu:** ~10 menit.
**Sumber:** S-03, S-04, S-05 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Buat 2 vendor dengan property "Purchase Currency" berbeda satu sama lain.
2. Buat PO dengan vendor A, catat currency PO.
3. Ganti partner ke vendor B (currency berbeda) — CATATAN: currency PO TIDAK akan otomatis berubah
   mengikuti vendor B, ini SENGAJA dipertahankan sebagai bug lama (F-02/F-03), bukan hal yang perlu
   dilaporkan sebagai bug baru.
4. Buat produk dengan `product.supplierinfo` khusus untuk salah satu vendor di atas.
5. Buat PO dengan vendor tersebut, tambah baris produk itu, buka dialog konfigurator.
6. Pastikan harga yang tampil di dialog mengikuti harga supplierinfo vendor itu (bukan harga standar).
7. Simpan baris (dengan atau tanpa optional product).
8. Buka kembali baris yang sudah tersimpan tadi, klik ikon edit configuration (pensil di sebelah nama
   produk, kalau ada) atau buka baris untuk mengedit.
9. Pastikan dialog "Configure your product" terbuka kembali dengan data yang sudah tersimpan
   sebelumnya (bukan grid/dropdown biasa).
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-24 | Docker `odoo:18.0`, langkah 1-7 | Test otomatis (AI) | Pass | `TestOnchangePartnerCurrency`, `TestConvertPrice`, `TestPurchaseProductOptionalController` |
| — | — | — | **Langkah 8-9 belum dieksekusi** | Direkomendasikan dev/QA jalankan manual sebelum rilis — perubahan kode terkait (rename `onEditConfiguration`) mekanis murni, risiko rendah |
