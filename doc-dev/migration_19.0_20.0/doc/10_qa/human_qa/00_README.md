# Human QA Checklists — purchase_product_optional (20.0)

**Sumber:** skenario S-01..S-09 di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per Level. Kalau skenario
berubah di sana, regenerate file di folder ini.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Dialog configurator terbuka | Sebelum deploy/hotfix apa pun |
| `02_MAIN_FLOW.md` | Harga vendor, tambah optional + simpan | Deploy rutin |
| `03_DETAIL.md` | Eksklusi, tipe atribut, edit ulang | Sebelum rilis besar / UAT |
| `04_NEGATIVE.md` | Dua dialog, Cancel | Minimal sekali sebelum rilis besar |

**Data yang perlu disiapkan sekali (staging):** 2 vendor (A, B); produk utama dengan harga vendor A=80,
B=90 dan 1-2 optional product (salah satu punya harga vendor A); satu optional dengan 2 atribut yang saling
mengecualikan (Product → Attributes → "Exclude For"); satu produk dengan 2 varian (mis. warna Merah/Biru).
