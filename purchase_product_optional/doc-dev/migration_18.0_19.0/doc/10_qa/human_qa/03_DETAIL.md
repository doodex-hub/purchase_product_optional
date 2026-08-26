# Detail Test — purchase_product_optional (18.0 → 19.0)

**Level:** Detail.
**Sumber:** S-06 di `../10_BUSINESS_FLOW_MIGRATION.md` — fallback grid configurator.

```
1. Cari kondisi di mana `product.template.get_single_product_variant()` mengembalikan `result.mode`
   BUKAN `'configurator'` dan BUKAN kosong/false untuk konteks Purchase (per catatan CAND-07, kondisi
   ini kemungkinan besar TIDAK PERNAH terjadi di alur normal — purchase/purchase_product_matrix tidak
   mengisi field ini untuk Purchase).
2. Kalau kondisi itu berhasil ditemukan/direproduksi: pilih produk tersebut di baris PO.
3. Amati: apakah dialog grid "Choose Product Variants" terbuka (bukan error JS `TypeError`)?
```

**Catatan:** kalau langkah 1 tidak bisa direproduksi lewat data produk manapun yang tersedia — itu
KONSISTEN dengan analisis kode (CAND-07), bukan kegagalan checklist ini. Cukup catat "tidak
direproduksi, konsisten dugaan unreachable" di tabel hasil.

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| — | — | — | **Belum dieksekusi** | Kode sudah diverifikasi lewat code review (Step 8) mirror pola native 19.0 persis — direkomendasikan dicoba kalau ada data produksi nyata yang mereproduksi kondisi ini |
