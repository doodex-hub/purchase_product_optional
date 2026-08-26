# Human QA Checklists — purchase_product_optional (18.0 → 19.0)

**Sumber:** diturunkan dari skenario S-01..S-07 di `../10_BUSINESS_FLOW_MIGRATION.md`.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Install bersih + alur konfigurator dasar | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Harga per-vendor, onchange currency, variant dinamis | QA rutin |
| `03_DETAIL.md` | Fallback grid configurator (jarang tereksekusi) | Sebelum rilis besar, kalau ada waktu |
| `04_NEGATIVE.md` | Dua dialog terbuka bersamaan | Wajib sebelum rilis besar |

**Kombinasi disarankan:** deploy rutin → `01_SMOKE.md` + `02_MAIN_FLOW.md`; sebelum UAT → keempat file.
