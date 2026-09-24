# Detail — purchase_product_optional

**Level:** Detail. **Estimasi waktu:** ~10 menit.

```
Eksklusi atribut
1. Buka dialog produk utama; pada optional yang punya eksklusi, nilai yang dikecualikan tampil pudar.
2. Pilih kombinasi terlarang → muncul "This option or combination of options is not available",
   tombol Add nonaktif. Pilih nilai lain → normal kembali.

Tipe atribut & custom value
3. Pada optional dengan atribut dropdown / pills / warna / checkbox / radio "custom": ubah tiap pilihan;
   extra price tampil sebagai badge (contoh "+$ 5.00"); pilih nilai custom → kotak "Enter a customized
   value" muncul, isi teks.
4. Add → Confirm → Save → baris optional tersimpan.

Edit ulang baris ber-varian
5. Buat PO dengan produk ber-varian (lihat 04_NEGATIVE langkah 1-3 cara aman), Save.
6. Klik baris → ikon pensil di kolom Product → muncul grid varian DAN dialog "Configure your product"
   dengan pilihan tersimpan sudah terpilih. Tutup grid (✕), klik Cancel di configurator → baris tetap.
   Save sukses.
```

**Catatan (bukan kegagalan):** optional dengan banyak varian bisa tampil $0.00 (perilaku lama); label
varian di bawah nama produk pada baris PO tidak lagi tampil di Odoo 20 (tampilan standar Odoo 20).

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker 19.0 vs 20.0 + Enterprise (AI) | Claude | Pass | Identik 19.0 |
