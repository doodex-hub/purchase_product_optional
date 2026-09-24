# Negative — purchase_product_optional

**Level:** Negative. **Estimasi waktu:** ~5 menit.

```
1. PO baru, vendor A → tambah produk ber-varian (mis. warna Merah/Biru).
2. Muncul DUA dialog: grid varian (depan) dan "Configure your product" (belakang, tidak bisa diklik).
   Ini perilaku lama (sejak 17.0), bukan kegagalan migrasi.
3. Isi qty di grid → Confirm → tersisa dialog "Configure your product".
4. Tutup dialog itu dengan ✕ (atau Confirm) → Save → PO tersimpan dengan baris dari grid.
   PERINGATAN (perilaku lama, sama di 19.0): kalau di langkah 4 menekan "Cancel", Save akan gagal
   ("Oops!"). Keluar dengan Discard.
5. PO baru → tambah produk utama → di dialog klik Cancel → baris hilang, tidak ada baris kosong tersisa.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker 19.0 vs 20.0 + Enterprise (AI) | Claude | Pass | Perilaku identik 19.0 (termasuk bug langkah 4 Cancel, RMV-03) |
