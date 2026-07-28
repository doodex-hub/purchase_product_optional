# QA AI Browser (AI-in-the-loop) — purchase_product_optional

> Step 07 · BACKFILL — metode berbeda dari skenario umum di `07_QA_TESTING.md` §3 (desk-review/Mode
> B): AI navigasi browser sungguhan (Claude in Chrome), verifikasi hasil/screenshot secara live.
>
> **Environment:** Mode B G2 hidup (`docker-env/docker-compose.yml`, database
> `purchase_product_optional_demo`, `http://localhost:8079`), login `admin`. Data test dibuat
> langsung lewat UI (bukan mengubah kode): attribute baru "QA Dynamic Finish" (Dynamically, value
> "QA Value A") ditambahkan ke produk demo "Customizable Desk" (`[FURN_0096]`, sudah punya attribute
> Legs [Instantly] + Color [Instantly] + optional product "Conference Chair"), plus
> `product.supplierinfo` baru: vendor "Azure Interior", harga $700 (vs list price $750).
>
> **Tanggal eksekusi:** 2026-07-28
> **Status:** Selesai — 4 dari 5 kelompok AC diverifikasi live; AC-06-02 (DOM element hilang) dan
> AC-09-02 (invalid-combination guard) tidak sempat direproduksi (lihat §Keterbatasan di bawah),
> TAPI investigasi menemukan bug baru bernilai Tinggi (F-06) yang tidak ada di skenario awal.

---

## Skenario

### S-10: Dialog trigger — produk matrix-eligible + optional products (AC-01)
**Precondition:** Mode B G2 hidup, produk "Customizable Desk" (Legs×Color = matrix-eligible,
optional product "Conference Chair" terpasang), vendor "Azure Interior" (supplierinfo $700).
**Mode eksekusi:** AI-in-the-loop (browser)
**Steps:**
1. Buka RFQ baru, isi Vendor = Azure Interior.
2. Di baris produk, ketik dan pilih "Customizable Desk".
3. Amati dialog yang muncul.
**Expected:** Sesuai `01A_FUNCTIONAL_SPEC.md` BR-01/AC-01, satu dialog "Configure your product"
(`ProductConfiguratorDialogPurchase`) terbuka menampilkan harga per-vendor + optional products.
**Actual:** Dialog "Configure your product" MEMANG terbuka di depan dan menampilkan harga benar
($700.00, sesuai vendor Azure Interior — bukan list price $750). **TAPI** ditemukan SECARA
TIDAK SENGAJA: dialog KEDUA — "Choose Product Variants" (grid, milik `purchase_product_matrix`,
dipicu independen oleh `super._onProductTemplateUpdate()`) — juga terbuka BERTUMPUK di belakang
dialog pertama, tidak terlihat sampai area belakang di-klik. Kalau user hanya berinteraksi dengan
dialog depan (skenario realistis — tidak ada indikasi visual jelas ada dialog kedua) dan langsung
klik Confirm, baris produk UTAMA ("Customizable Desk") **TIDAK PERNAH masuk ke Purchase Order sama
sekali** — hanya optional product (Conference Chair) yang tersimpan. Direproduksi 2× (lihat detail
lengkap + reproduksi susulan di `FINDINGS.md` F-06).
**Status:** ☐ Pass / ☑ Fail (temuan baru F-06, bukan bagian AC-01 asli tapi ditemukan lewat
verifikasi AC-01)
**Provenance:** [PERLU-KEPUTUSAN] — lihat F-06.

---

### S-11: Harga per-vendor di dialog configurator (AC-05-01, terkait F-04)
**Precondition:** Sama seperti S-10, vendor Azure Interior punya `supplierinfo` $700 untuk
Customizable Desk (list price $750).
**Mode eksekusi:** AI-in-the-loop (browser)
**Steps:**
1. Buka dialog "Configure your product" untuk Customizable Desk dengan vendor Azure Interior aktif.
2. Baca harga yang ditampilkan di dialog.
**Expected:** Harga mengikuti `supplierinfo` vendor terpilih ($700), bukan list price standar
($750) — sesuai BR-01 dan mekanisme baca DOM `id_vendor_0` (F-04).
**Actual:** **CONFIRMED** — dialog menampilkan $700.00, sesuai harga vendor, bukan $750. Mekanisme
`document.getElementById('id_vendor_0')` (F-04) terbukti BEKERJA BENAR di kondisi form tunggal
normal. Risiko edge-case F-04 (id conflict/dua form sekaligus) tetap tidak diverifikasi — di luar
skenario normal yang bisa direproduksi lewat interaksi manual.
**Status:** ☑ Pass
**Provenance:** [DIKONFIRMASI] — mekanisme kondisi-normal terverifikasi; edge-case F-04 tetap
[PERLU-KEPUTUSAN] terpisah.

---

### S-12: Tambah optional product dari dalam dialog (AC-07-01)
**Precondition:** Dialog "Configure your product" terbuka untuk Customizable Desk, section
"Add optional products" menampilkan Conference Chair dengan tombol "+Add".
**Mode eksekusi:** AI-in-the-loop (browser)
**Steps:**
1. Klik "+Add" pada Conference Chair.
2. Amati perubahan tampilan dialog.
**Expected:** Conference Chair pindah dari mode ringkas (+Add) ke mode penuh (quantity stepper +
tombol "Remove product"), harga optional ditambahkan ke Total.
**Actual:** **CONFIRMED** — persis sesuai expected; Conference Chair menampilkan quantity=1, tombol
"Remove product" muncul menggantikan "+Add".
**Status:** ☑ Pass
**Provenance:** [DIKONFIRMASI]

---

### S-13: Hapus optional product dari dalam dialog (AC-07-02)
**Precondition:** Lanjutan S-12 — Conference Chair sudah ditambahkan sebagai optional product di
dialog yang sama.
**Mode eksekusi:** AI-in-the-loop (browser)
**Steps:**
1. Klik "Remove product" pada baris Conference Chair.
2. Amati perubahan tampilan dialog.
**Expected:** Conference Chair kembali ke mode ringkas ("+Add"), tidak lagi dihitung di Total.
**Actual:** **CONFIRMED** — persis sesuai expected, "Remove product" berhasil mengembalikan
Conference Chair ke state semula (tombol "+Add" muncul kembali).
**Status:** ☑ Pass
**Provenance:** [DIKONFIRMASI]

---

### S-14: Alur lengkap Confirm — grid + configurator + save eksplisit (klarifikasi F-06)
**Precondition:** Sama seperti S-10.
**Mode eksekusi:** AI-in-the-loop (browser)
**Steps:**
1. Pilih Customizable Desk → dua dialog terbuka (grid di belakang, configurator di depan).
2. Isi qty=1 di grid "Choose Product Variants" (kombinasi White • QA Value A × Steel), klik Confirm
   PADA GRID.
3. Tambahkan Conference Chair via "+Add" di configurator dialog (masih di depan), klik Confirm.
4. Klik SAVE eksplisit (ikon cloud breadcrumb).
5. Reload halaman penuh (navigate ulang ke URL PO yang sama).
**Expected:** Kalau user mengisi KEDUA dialog dengan benar DAN melakukan save eksplisit, kedua baris
(Customizable Desk + Conference Chair) tersimpan benar.
**Actual:** **CONFIRMED** — setelah langkah 1-4, chatter mencatat `$0,00 → $7.000,00 (Untaxed
Amount)`; setelah full reload (langkah 5), KEDUA baris tetap ada dan benar (Customizable Desk qty
10 — qty 10 murni artefak input test, bukan bug — @ $700, Conference Chair qty 1 @ $0.00, Total
$8.050,00). Ini mengonfirmasi data model & persistensi BENAR selama user melalui KEDUA dialog +
save eksplisit — bug F-06 murni soal dialog depan/belakang yang tidak terkoordinasi dan mudah
diabaikan user (S-10), BUKAN soal korupsi data yang lebih dalam.
**Status:** ☑ Pass (mengonfirmasi mekanisme dasar benar, sekaligus mempersempit lingkup F-06)
**Provenance:** [DIKONFIRMASI]

---

## Keterbatasan (tidak sempat direproduksi sesi ini)

- **AC-06-02** (elemen `id_vendor_0` hilang dari DOM — kondisi abnormal, mis. dua form PO sekaligus
  di halaman yang sama) — tidak direproduksi, butuh skenario multi-form/dialog-dalam-dialog yang
  sulit dipicu lewat interaksi manual normal. Tetap `[PERLU-KEPUTUSAN]` di F-04.
- **AC-09-02** (guard kombinasi attribute tidak valid saat Confirm) — tidak sempat direproduksi;
  waktu sesi dialihkan ke investigasi F-06 (dialog stacking) yang ternyata bernilai lebih tinggi
  dan tidak terduga dari skenario awal. Direkomendasikan jadi prioritas kalau ada sesi 07B lanjutan.
- **AC-01 sub-cabang lain** (single-variant direct-assign tanpa dialog, warning/block dialog dari
  `purchase_warning`) — tidak direproduksi; produk demo yang tersedia tidak punya kombinasi yang
  memicu cabang-cabang ini secara alami tanpa mengubah data attribute lebih jauh.

## Temuan baru dari sesi ini (di luar rencana awal S-06 s/d S-09)

**F-06** — dialog "Configure your product" dan "Choose Product Variants" (grid) tumpang tindih
tanpa koordinasi, bisa menghilangkan baris produk utama dari PO tanpa error apapun (detail lengkap +
3 leftover `console.log` debug: lihat `doc-dev/backfill/FINDINGS.md`). Ditemukan TIDAK SENGAJA saat
menjalankan S-10 (verifikasi AC-01 dasar) — bukan hasil skenario yang direncanakan sebelumnya.
