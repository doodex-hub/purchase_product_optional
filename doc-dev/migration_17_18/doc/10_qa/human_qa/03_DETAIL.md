# Detail Test — purchase_product_optional

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi tetap valid.
**Estimasi waktu:** ~10 menit.
**Sumber:** skenario `S-06`, `S-07`, `S-08` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## 1. Warning/Blocking Message produk (tahu batasannya)

```
1. Buka Settings > Purchase, pastikan toggle "Warnings" AKTIF.
2. Buka Purchase > Products > pilih produk apapun > tab Purchase > field
   "Warning when purchasing this product" > pilih "Warning" atau
   "Blocking Message", isi pesan.
3. Buat RFQ baru, tambah produk itu ke baris.
```

**Yang akan terjadi (BUKAN bug, ini perilaku Odoo standar):** Dialog peringatan tetap
MUNCUL berisi pesan yang diisi — tapi ini datang dari mekanisme ONCHANGE STANDAR Odoo
`purchase.order.line`, BUKAN dari fitur khusus modul `purchase_product_optional`. Untuk
tipe "Blocking Message", baris TETAP tersimpan (tidak benar-benar diblokir oleh modul
ini) — fitur block versi modul ini sudah tidak aktif sejak Odoo 18 (mekanisme sumbernya
hilang dari platform), dan ini SUDAH SEHARUSNYA begitu, bukan sesuatu yang perlu
dilaporkan sebagai bug.

## 2. Urutan konfirmasi: grid dulu, baru dialog produk

```
1. Buat RFQ baru, vendor yang punya harga vendor untuk produk test.
2. Tambah baris produk yang matrix-eligible + punya optional products (misal
   "Customizable Desk") — dua dialog akan terbuka bertumpuk.
3. Isi quantity di dialog grid "Choose Product Variants" (belakang) untuk
   kombinasi yang diinginkan (misal Steel/White = 1).
4. Klik Confirm pada dialog grid TERLEBIH DAHULU.
5. Setelah dialog grid tertutup, klik Confirm pada dialog "Configure your
   product" (depan).
```

**Harus terjadi:** SATU baris PO tersimpan dengan produk, varian, qty, dan harga yang
BENAR/konsisten — bukan duplikat, bukan harga yang salah varian.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-07-30 | Mode B, docker 18.0 (`purchase_product_optional_18_demo`) | Claude (AI-interaktif) | ✅ Pass | Lihat `10_BUSINESS_FLOW_MIGRATION.md` S-06/S-07/S-08 — `purchase_warning`/`mode` custom dikonfirmasi dead code (bukan regresi), urutan grid-dulu menghasilkan satu baris bersih (P00015, $350.00) |
