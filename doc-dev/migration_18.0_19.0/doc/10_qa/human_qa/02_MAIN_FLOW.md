# Main Flow Test — purchase_product_optional (18.0 → 19.0)

**Level:** Main Flow.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-03, S-04, S-05 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Buat 2 vendor dengan property "Purchase Currency" berbeda satu sama lain.
2. Buat PO dengan vendor A, catat currency PO.
3. Ganti partner ke vendor B (currency berbeda) — CATATAN: currency PO TIDAK akan otomatis berubah
   mengikuti vendor B, ini SENGAJA dipertahankan sebagai bug lama (BSL-005/006), bukan hal yang perlu
   dilaporkan sebagai bug baru.
4. Buat produk dengan `product.supplierinfo` khusus untuk salah satu vendor di atas.
5. Buat PO dengan vendor tersebut, tambah baris produk itu, buka dialog konfigurator.
6. Pastikan harga yang tampil di dialog mengikuti harga supplierinfo vendor itu (bukan harga standar).
7. Pilih produk dengan atribut yang membuat variant baru harus dibuat (dynamic attribute) + optional
   product, klik Confirm.
8. Pastikan baris tersimpan benar (nama produk, harga, quantity) — TIDAK ada baris kosong/nama
   "undefined"/harga salah (ini yang akan terjadi kalau format data many2one salah, DIFF-01).
9. Simpan PO.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker `odoo:19.0`, langkah 1-9 | Test otomatis + Tour (AI) | Pass | `TestOnchangePartnerCurrency`, `TestConvertPrice`, `TestPurchaseProductOptionalController`, Tour `purchase_product_optional_configurator_tour` |
