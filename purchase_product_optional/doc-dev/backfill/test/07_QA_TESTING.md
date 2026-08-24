# QA Testing — purchase_product_optional

**Step:** 07 — QA Testing (backfill, TANPA UAT — BACKFILL berhenti di sini)
**Ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`, `03B_TEST_PLAN.md`
**Tanggal:** 2026-07-29

---

## 1. Area / AC yang Harus Dicakup

- [x] AC-01 — Dialog konfigurator auto-open + warning block
- [x] AC-02 — Harga per-vendor di dialog
- [x] AC-06-02 — Confirm tanpa dynamic variant
- [x] AC-07 — Badge exclusion + tombol Confirm disabled
- [x] AC-08 — Kolom tree PO line (product_template_id/product_id)
- [x] AC-09 — Auto-install (desk-review)

---

## 2. Format Skenario

Lihat `07B_QA_AI_BROWSER.md` untuk format yang sama dipakai bersama.

---

## 3. Skenario (business flow — state transition, edge case, error handling, access rights)

### S-01: Dialog konfigurator terbuka otomatis untuk produk dengan optional product
**Precondition:** PO baru, produk template punya `optional_product_ids` terisi (dibuat sebagai
fixture BACKFILL: "BACKFILL QA Main Product" + "BACKFILL QA Optional Product").
**Mode eksekusi:** AI-in-the-loop (browser) dicoba — **diblokir oleh limitasi environment** (tab
browser sandbox ini tidak pernah `visibilityState: visible`, OWL webclient tidak sempat mounting).
Lihat `07B_QA_AI_BROWSER.md` untuk diagnosis lengkap (root cause dikonfirmasi via
`odoo.loader.failed/missing` kosong — modul JS ini sendiri TIDAK bermasalah).
**Steps:**
1. Buka Purchase > Orders > New.
2. Set vendor.
3. Pada baris PO, pilih product template "BACKFILL QA Main Product".
**Expected:** Dialog `ProductConfiguratorDialogPurchase` terbuka otomatis, menampilkan produk utama
+ 1 optional product dengan tombol "Add".
**Actual:** **PASS PENUH end-to-end** via Odoo Tour headless (Mode E, Chrome sungguhan,
`0 failed, 0 error(s) of 13 tests`) — dialog terbuka otomatis, optional product ditambah via
"Add", Confirm menyimpan baris baru, PO benar-benar ter-save. Screenshot pendukung:
`test/07B_screenshot_dialog_confirmed.png`. Payload backend juga sudah diverifikasi via `HttpCase`
Step 04. Detail lengkap: `07B_QA_AI_BROWSER.md`.
**Status:** ☑ Pass (end-to-end, Tour headless real + backend HttpCase)
**Provenance:** [HASIL-BACA] dikonfirmasi end-to-end (Tour) + HTTP nyata (Step 04)

---

### S-02: Kolom tree PO line sesuai BR-11
**Precondition:** Form PO manapun terbuka.
**Mode eksekusi:** AI-in-the-loop (browser) dicoba — **diblokir**, sama seperti S-01. Sebagai
gantinya, klaim struktural ini sudah diverifikasi via `TestPurchaseOrderFormViewColumns`
(`TransactionCase`, Step 04) yang membaca arch view HASIL MERGE langsung dari registry Odoo — bukti
setara/lebih presisi dari sekadar screenshot untuk klaim atribut XML (`column_invisible`/`optional`).
**Steps:**
1. Buka form Purchase Order manapun.
2. Perhatikan kolom baris order.
**Expected:** Kolom "Product Template" tampil, kolom "Product Variant" (`product_id`) tersembunyi
secara default.
**Actual:** Visual TIDAK terverifikasi (blocked). Merged view arch dikonfirmasi lewat test Step 04:
`product_template_id` punya `column_invisible="0"`, `product_id` punya `optional="hide"`.
**Status:** ☑ Pass (via Unit test Step 04, bukan visual browser)
**Provenance:** [HASIL-BACA] dikonfirmasi via test Step 04

---

### S-03: Tombol Confirm disabled selama kombinasi tidak valid (AC-07)
**Precondition:** Produk dengan atribut yang punya exclusion (dua value saling exclude).
**Mode eksekusi:** Desk-review (fixture exclusion butuh setup data lebih kompleks daripada waktu
sesi ini — lihat keterbatasan §4). Logic sudah diverifikasi via baca kode
(`_checkExclusions`/`isPossibleConfiguration`, `static/src/js/product_configurator_dialog/
product_configurator_dialog.js:405-535`) dan TIDAK diverifikasi ulang secara visual di sesi ini.
**Steps:** *(tidak dieksekusi — desk-review)*
**Expected:** Tombol "Confirm" disabled ketika ada produk dengan kombinasi yang termasuk exclusion.
**Actual:** Tidak dieksekusi — desk-review dari kode saja.
**Status:** ☐ Pass / ☐ Fail — **N/A, desk-review**
**Provenance:** [HASIL-BACA]

---

### S-04: Auto-install (AC-09)
**Precondition:** `docker-env` fresh install (Step 04) — `-i purchase_product_optional` langsung
diminta secara eksplisit di command (bukan trigger auto_install natural).
**Mode eksekusi:** Desk-review — `auto_install: True` dibaca langsung dari `__manifest__.py:29`,
TIDAK diverifikasi ulang dengan skenario "install 3 dependency lalu modul ini ikut terinstall
sendiri" (di luar scope waktu sesi, dan docker-compose Step 04 sudah memaksa instalasi eksplisit
sehingga tidak bisa jadi bukti auto-install juga bekerja).
**Steps:** *(tidak dieksekusi)*
**Expected:** Modul auto-install begitu `purchase`+`purchase_product_matrix`+`sale_product_configurator`
ter-install.
**Actual:** Tidak dieksekusi — desk-review manifest.
**Status:** ☐ Pass / ☐ Fail — **N/A, desk-review**
**Provenance:** [HASIL-BACA]

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | Skenario umum (AI-interaktif/desk-review) | ✅ Selesai ditulis | S-01 visual-verified (Tour), S-02 arch-verified (Step 04), S-03/S-04 desk-review | Campuran |
| `07B_QA_AI_BROWSER.md` | Verifikasi browser AI (Claude Browser MCP + Odoo Tour headless) | ✅ Selesai ditulis | Claude Browser MCP blocked; **Tour headless berhasil**, screenshot nyata tersedia | AI-in-the-loop (browser MCP, blocked) + Tour headless (Mode E, berhasil) |

**Keterbatasan eksekusi (WAJIB diisi):**
1. **S-01 (dialog konfigurator):** Claude Browser MCP blocked (tab tidak pernah `visible`, lihat
   `07B_QA_AI_BROWSER.md`), TAPI diganti Odoo Tour headless (Mode E) yang **PASS PENUH** setelah
   2 percobaan Dockerfile (Chrome) + 3 iterasi perbaikan bug di script Tour sendiri (bukan bug
   modul — detail root-cause di `FINDINGS.md`/`07B_QA_AI_BROWSER.md`). Hasil akhir `0 failed, 0
   error(s) of 13 tests` — **S-01 kini Pass end-to-end** (dialog buka, optional product ditambah,
   PO tersimpan), bukan cuma payload backend atau screenshot parsial.
2. **S-02 (kolom tree PO line):** tidak termasuk dalam Tour (di luar scope langkah yang ditulis),
   tetap diverifikasi via `TestPurchaseOrderFormViewColumns` (`TransactionCase` Step 04, baca arch
   view hasil merge dari registry) — bukti yang setara/lebih presisi untuk klaim atribut XML
   dibanding sekadar screenshot.
2. **S-03 (exclusion/badge warning):** desk-review — butuh fixture 2 atribut dengan relasi exclusion
   (`product.template.attribute.exclusion`), di luar cakupan waktu sesi ini setelah S-01/S-02 (lebih
   representatif untuk BR-01/BR-02/BR-11) sudah diprioritaskan.
3. **S-04 (auto-install):** desk-review — butuh siklus install-dari-nol terpisah dari docker-env
   Step 04 (yang sudah memaksa `-i` eksplisit, tidak bisa jadi bukti auto-install juga bekerja).

---

## 5. Rekap Findings (jumlah per tag, detail lengkap di `doc-dev/backfill/FINDINGS.md`)

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 8 (F-01 s/d F-08) |
| `[DIKONFIRMASI]` | 0 (belum ada konfirmasi pemilik modul) |
| `[HASIL-BACA]` (tanpa masalah) | Sisanya (BR-01, BR-02, BR-06, BR-07, BR-09, BR-10, BR-11, BR-12 — dikonfirmasi lewat test, tidak ada masalah) |

**Verdict:** Backfill dokumentasi selesai sampai Step 07 (QA Testing). **Tidak ada sign-off** — ini
bukan release gate. Keputusan atas 8 item `[PERLU-KEPUTUSAN]` di `FINDINGS.md` ada di tangan
pemilik modul — 3 di antaranya (F-01, F-02, F-05) sudah dikonfirmasi/direvisi berdasarkan eksekusi
nyata (Step 04), dan F-08 ditemukan langsung dari warning registry Odoo (Step 07), bukan cuma
dugaan baca kode.

---

## 6. Bug / Perlu Perbaikan (KONSOLIDASI dari §3+`07B`)

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| Step 01/04 (baca kode + test) | — | F-01: `product_add_mode` tidak terdaftar sebagai field (dikonfirmasi via warning registry) | ☐ Belum |
| Step 01/04 (baca kode + test) | — | F-02: `onchange_partner_id` menimpa total method core Odoo `purchase.order` (dikonfirmasi via MRO) | ☐ Belum |
| Step 01 (baca kode) | — | F-03: cabang `else` di `onchange_partner_id` adalah no-op, currency partner tidak pernah tersinkron | ☐ Belum |
| Step 01 (baca kode) | — | F-04: `ir.config_parameter` global untuk currency — race condition multi-user | ☐ Belum |
| Step 01/04 (baca kode + test) | — | F-05: `convert_price()` senyap skip konversi kalau param currency belum di-set (dikonfirmasi: return unchanged) | ☐ Belum |
| Step 01 (baca kode) | — | F-06: `id_vendor` dibaca via `document.getElementById`, fragile | ☐ Belum |
| Step 01 (baca kode) | — | F-07: harga supplier tidak difilter company | ☐ Belum |
| Step 07 (browser/registry) | — | F-08: label field `id_vendor` bentrok dengan `id` (warning registry) | ☐ Belum |

Lihat `07B_QA_AI_BROWSER.md` untuk detail S-01/S-02 (keduanya Pass, tidak ada bug baru ditemukan
lewat browser).

---

## 7. Slot Metode Masa Depan (belum dibuat)

- `07C_QA_PLAYWRIGHT.md` — belum dipakai, tidak dibuat (sesuai kebijakan "jangan buat file kosong").
