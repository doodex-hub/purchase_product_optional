# Human QA Checklists — purchase_product_optional

**Sumber:** diturunkan dari skenario S-01..S-06 di `../10_BUSINESS_FLOW_MIGRATION.md`.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Install bersih + alur konfigurator dasar | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Harga per-vendor, onchange currency, edit ulang konfigurasi | QA rutin |
| `03_DETAIL.md` | — | Tidak ada skenario Detail lain di luar S-05 (sudah masuk `02_MAIN_FLOW.md` sebagai langkah tambahan) |
| `04_NEGATIVE.md` | Dua dialog terbuka bersamaan | Wajib sebelum rilis besar |

**Kombinasi disarankan:** deploy rutin → `01_SMOKE.md` + `02_MAIN_FLOW.md`; sebelum UAT → keempat file.
