# Findings — purchase_product_optional (migrasi 19.0 → 20.0)

> Konsolidasi tunggal gap/bug/ambiguitas yang butuh keputusan manusia (template
> `migration-tool/templates/FINDINGS.md`). ID `MF-NNN` — tidak bentrok dengan `F-NNN`
> (`doc-dev/backfill/FINDINGS.md`) maupun `CAND-NN` (migration records).

**Modul:** purchase_product_optional
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-24

---

## Ringkasan

| ID | Judul | Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | 5 commit aset store di branch rilis `19.0` tidak di-port | 1 | `[PERLU-KEPUTUSAN]` | Rendah | Default diambil (tidak di-port), menunggu konfirmasi |
| MF-02 | Bundel quirk 19.0 yang dipertahankan (BSL-005/006/009/010/013/017/018/021/022/025/027/028, CAND-08) | 1 | `[DIWARISI-SOURCE]` | Info | Dipertahankan |
| MF-03 | Parent exclusions (eksklusi atribut lintas-produk) hilang di 20.0 | 1-2 | `[GAP-MIGRASI]` | Sedang | Default diambil (kontrak `parent_exclusions={}`), menunggu konfirmasi |

---

## Detail

### MF-01 — Aset store pasca-migrasi 18→19 tidak ikut `migration/19.0`
**Ditemukan di:** Step 1 (2026-09-24), sudah dicatat sebagai open item saat conditioning.
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `git log migration/19.0..origin/19.0` — `2c8a7cb` cleaning, `1f8f24b` banner.gif, `13be2f0`
assets/hapus img, `636b71c`/`265a6d3` index.html, `cb61fd9` fix key `images`.
**Deskripsi:** branch rilis `19.0`/`staging/19.0` punya 5 commit (+merge) yang tidak ada di
`migration/19.0`. Commit "cleaning" juga menghapus `tests/` (tidak cocok untuk branch migrasi yang
butuh test Step 6/9).
**Dampak:** listing App Store 20.0 akan memakai aset lama (`banner.png`, folder `img/`) kalau
`migration/20.0` dirilis apa adanya.
**Rekomendasi (default yang diambil):** TIDAK di-port di migrasi ini (source of truth = `migration/19.0`,
scope = kode fungsional). Saat membuat branch rilis `20.0`, dev menerapkan ulang packaging (cherry-pick
commit aset + bump key `images`) sesuai praktik rilis 19.0.
**Keputusan pemilik modul:** *(kosong)*

### MF-02 — Quirk 19.0 yang dipertahankan identik
**Ditemukan di:** Step 1 (2026-09-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` BSL-005/006 (F-02/F-03), BSL-009 (F-01), BSL-010 (F-07), BSL-013/018
(F-04/F-05), BSL-017 (F-08), BSL-021, BSL-022, BSL-025, BSL-027, BSL-028; CAND-08 (17_18 SUMMARY).
**Deskripsi:** bug/quirk yang sudah ada di 19.0 dan sengaja TIDAK diperbaiki (keputusan dev 18→19,
berlaku lanjut). Yang baru terdokumentasi di migrasi ini: BSL-021 (perbandingan `product_id` selalu
true), BSL-022 (`productUOMId`/`pricelistId` selalu `undefined`), BSL-025 (`hasPTAVCustom` tanpa
panggilan), BSL-027/028 (harga ditimpa saat ganti qty/atribut).
**Keputusan pemilik modul:** dipertahankan (default `CLAUDE.md`), kecuali dev minta lain.

### MF-03 — Eksklusi atribut lintas-produk tidak lagi didukung platform 20.0
**Ditemukan di:** Step 1-2 (2026-09-24)
**Tag:** `[GAP-MIGRASI]`
**Ref:** BSL-020, BSL-016; `02_DIFF_ANALYSIS.md` DIFF-06.
**Lokasi:** `controllers/main.py` (`_get_product_information_purchase`, `get_values_purchase`,
`get_optional_products`).
**Deskripsi:** native 20.0 menghapus model `product.template.attribute.exclusion` (`exclude_for`) dan
menggantinya dengan `excluded_value_ids` yang domain-nya dibatasi ke template yang SAMA
(`product_template_attribute_value.py` 20.0 baris 50-57). `_get_attribute_exclusions()` dan
`_get_first_possible_combination()` tidak lagi menerima `parent_combination` dan tidak mengembalikan
`parent_exclusions`. Modul memanggil keduanya dengan `parent_combination=` → `TypeError` di setiap
buka dialog kalau tidak diubah.
**Dampak:** aturan "nilai atribut optional product X tidak tersedia bila produk utama memakai nilai Y"
tidak bisa lagi dikonfigurasi maupun dievaluasi di 20.0 (juga tidak di `sale` native). Eksklusi dalam
satu produk (`exclusions`) dan kombinasi arsip tetap jalan.
**Rekomendasi (default yang diambil, satu-satunya opsi yang tidak menambah fitur):** hapus kwarg
`parent_combination` dari dua panggilan native; controller tetap mengembalikan key
`parent_exclusions` berisi `{}` supaya kontrak JS (`_checkExclusions`) tidak berubah. Tidak
mengimplementasikan ulang fitur parent exclusion di modul (itu menambah fitur/model data baru).
**Keputusan pemilik modul:** *(kosong — konfirmasi apakah fitur ini pernah dipakai produksi)*

---

## Cara Pakai

Lihat template. Update setiap step menemukan hal yang butuh keputusan manusia; Step 4 dan Step 8 wajib
membaca file ini sebagai bagian gate.
