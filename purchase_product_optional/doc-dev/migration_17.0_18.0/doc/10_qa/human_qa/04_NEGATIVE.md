# Negative Test — purchase_product_optional

**Level:** Negative — soal keamanan/guard, jalankan minimal sekali sebelum rilis besar.
**Sumber:** S-06 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Cari/buat produk yang SEKALIGUS: (a) punya atribut yang memicu grid matrix `purchase_product_matrix`
   (banyak kombinasi varian), DAN (b) punya optional products (memicu dialog konfigurator modul ini).
2. Buat PO, tambah baris dengan produk tersebut.
3. Amati: apakah HANYA SATU dialog yang terbuka, atau dua dialog (grid matrix + configurator) terbuka
   bertumpuk/bersamaan?
4. Kalau dua dialog terbuka: selesaikan HANYA SATU dialog (yang paling depan/terlihat), lalu Save PO.
5. Cek baris PO — apakah data dari dialog yang TIDAK diselesaikan hilang/tidak konsisten tanpa pesan
   error apapun?
```

**Catatan penting:** ini adalah **gotcha desain yang SUDAH ADA identik di 17.0** (dikonfirmasi dari
kode `native-source`/`native-target`, bukan regresi migrasi 18.0) — kalau langkah 5 menunjukkan data
hilang, itu **bukan bug baru dari migrasi ini**, cukup dicatat sebagai limitasi diketahui (lihat
`08_CODE_REVIEW.md` §D dan `10_BUSINESS_FLOW_MIGRATION.md` S-06). Kombinasi produk matrix+optional
sekaligus TIDAK ada di data Tour test otomatis, jadi checklist ini satu-satunya cara memverifikasi
skenario ini.

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-24 | — | — | **Belum dieksekusi manual** (butuh produk dengan kombinasi matrix+optional, tidak ada di data Tour) | Verifikasi kode (Step 8) mengonfirmasi pola identik 17.0/18.0 — bukan blocker gate, tapi tetap direkomendasikan dicoba manual sebelum rilis besar |
