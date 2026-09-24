# Main Flow — purchase_product_optional

**Level:** Main Flow. **Estimasi waktu:** ~5 menit.

```
1. PO baru, Vendor = vendor A → tambah produk utama → dialog terbuka.
2. Cek harga: produk utama = harga vendor A (contoh 80); optional yang punya harga vendor A menampilkan
   harga itu (contoh 40); optional tanpa harga vendor menampilkan harga beli standar.
3. Klik "+ Add" pada satu optional → optional pindah ke atas, Total = jumlah harga.
4. Klik + pada qty produk utama → qty 2, Total naik; klik − → kembali 1.
5. Confirm → dua baris muncul di PO (produk utama + optional) dengan harga yang sama seperti di dialog.
6. Save → judul berubah dari "New" ke nomor PO.
7. Ulangi langkah 1-2 dengan vendor B: produk utama = harga vendor B (contoh 90), optional tanpa harga
   vendor B → harga standar. Cancel.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker 19.0 vs 20.0 + Enterprise (AI) | Claude | Pass | Identik 19.0 |
