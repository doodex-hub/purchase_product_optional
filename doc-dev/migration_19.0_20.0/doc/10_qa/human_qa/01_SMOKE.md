# Smoke Test — purchase_product_optional

**Level:** Smoke — kalau gagal: STOP, jangan deploy.
**Estimasi waktu:** ~2 menit.

```
1. Purchase → New (Request for Quotation).
2. Isi Vendor = vendor A.
3. Tab Products → "Add a product" → ketik nama produk utama (yang punya optional) → pilih.
4. Harus muncul dialog "Configure your product" berisi produk utama (harga, qty dengan tombol − 1 +)
   dan bagian "Add optional products". Ikon − / + dan "+ Add" TERLIHAT (bukan kotak kosong).
5. Klik Cancel → dialog tertutup, baris hilang.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker 20.0 + Enterprise (AI, Playwright) | Claude | Pass | Setelah fix ikon RMV-02 |
