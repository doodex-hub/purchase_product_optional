# Negative Test — purchase_product_optional

**Level:** Negative — hal yang HARUS ditolak, atau (khusus modul ini) bug warisan yang HARUS TETAP terjadi identik — kalau perilakunya berubah (jadi lebih baik ATAU lebih buruk dari 17.0), itu artinya ada regresi migrasi yang perlu diinvestigasi, bukan "perbaikan" yang boleh dibiarkan.
**Estimasi waktu:** ~10 menit.
**Sumber:** skenario `S-09`, `S-10` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## 1. Guard kombinasi atribut tidak valid

```
1. Buka dialog "Configure your product" untuk produk apapun yang punya
   beberapa pilihan atribut.
2. Coba cari cara memilih kombinasi yang seharusnya tidak tersedia (biasanya
   TIDAK BISA lewat klik biasa — pilihan yang tidak valid tidak muncul di UI).
3. Kalau berhasil membuat kombinasi aneh, klik Confirm.
```

**Harus terjadi:** Kalau kombinasi memang tidak valid, klik Confirm TIDAK melakukan
apa-apa (dialog tetap terbuka, tidak ada yang tersimpan). **Catatan:** skenario ini
SULIT direproduksi lewat UI normal (radio button hanya menampilkan opsi valid) — kalau
tidak berhasil dipaksa, ini BUKAN kegagalan, cukup catat "tidak bisa direproduksi via
UI" dan lanjut.

## 2. Bug warisan: dua dialog tumpang tindih (HARUS TETAP terjadi, JANGAN dianggap bug baru)

```
1. Buat RFQ baru, vendor apapun yang punya harga untuk produk test.
2. Tambah baris produk yang matrix-eligible + punya optional products (misal
   "Customizable Desk") — dua dialog akan terbuka bertumpuk: "Configure your
   product" di depan, "Choose Product Variants" (grid) di belakang.
3. TUTUP dialog grid (klik X, JANGAN isi apapun, JANGAN klik Confirm-nya).
4. Klik Confirm HANYA pada dialog "Configure your product" (depan).
```

**Harus terjadi (ini bug warisan yang DISENGAJA dipertahankan, BUKAN untuk
diperbaiki):** Baris produk UTAMA hilang total dari PO, tanpa error/warning apapun
yang tampil. Kalau baris JUSTRU tersimpan dengan benar di sini — itu artinya perilaku
BERUBAH dari 17.0, laporkan sebagai temuan regresi (bukan sebagai "sudah diperbaiki,
bagus").

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-07-30 | Mode B, docker 18.0 (`purchase_product_optional_18_demo`) | Claude (AI-interaktif) | ⚠️ Sebagian | Skenario 1 (guard kombinasi invalid): tidak berhasil direproduksi via UI (limitasi cara uji, kode tidak disentuh migrasi — risiko rendah). Skenario 2 (dialog overlap): ✅ direproduksi identik — baris hilang total tanpa error (P00016, F-06/MF-06), sesuai ekspektasi bug warisan |
