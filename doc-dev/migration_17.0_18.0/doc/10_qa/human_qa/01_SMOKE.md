# Smoke Test — purchase_product_optional

**Level:** Smoke — kalau salah satu langkah gagal: STOP, jangan lanjut deploy.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-01, S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Pastikan modul ter-install tanpa error di Apps (cari "Purchase Product Optional", status Installed).
2. Buka app Purchase → buat Request for Quotation baru.
3. Isi Vendor.
4. Tambah baris produk → pilih produk yang punya optional products.
5. Konfirmasi dialog "Configure your product" terbuka OTOMATIS (bukan dropdown biasa).
6. Klik "Add" pada salah satu optional product yang ditawarkan.
7. Klik "Confirm".
8. Simpan PO (klik Save).
9. Pastikan kedua baris (produk utama + optional) muncul di PO, dan PO ter-save (bukan lagi "New").
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-24 | Docker `odoo:18.0`, langkah 2-9 | Tour otomatis (AI, headless Chrome) | Pass | 15/15 langkah, lihat `docker-env/logs/odoo_step9.log` |
