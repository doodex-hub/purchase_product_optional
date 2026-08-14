# Human QA Checklists — purchase_product_optional

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga — jangan diedit terpisah sampai tidak sinkron.

**WAJIB dipakai terlepas dari mode eksekusi QA yang dipilih** (skenario di atas dieksekusi AI-interaktif, tapi manusia/dev/QA/PM tetap butuh cara re-verifikasi sendiri kapan saja tanpa AI/tooling, cukup baca dan ikuti langkah bernomor).

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Trigger dialog configurator (produk configurable) + update langsung (produk sederhana) | Re-cek super cepat sebelum deploy/hotfix — kalau ini gagal, STOP, jangan lanjut apapun |
| `02_MAIN_FLOW.md` | Edit baris tersimpan, harga vendor, optional products | QA rutin, atau setelah deploy yang menyentuh flow utama modul |
| `03_DETAIL.md` | `purchase_warning`/`mode` (dead code warisan), urutan grid+configurator | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard kombinasi invalid, bug dialog overlap (F-06/MF-06, HARUS TETAP terjadi identik) | Direkomendasikan sebelum rilis besar APAPUN — termasuk memastikan bug warisan TIDAK sengaja "keperbaiki"/berubah |

Angka prefix (01-04) = urutan prioritas kalau waktu terbatas (Smoke dulu, baru Main Flow, dst) — bukan urutan wajib dijalankan berurutan.

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → keempat file
- Kapan pun ada perubahan yang menyentuh `purchase_product_field.js`/`product_configurator_dialog.js` → jalankan `04_NEGATIVE.md` terlepas dari kombinasi lain, untuk memastikan bug warisan F-06 tidak berubah perilaku tanpa sengaja
