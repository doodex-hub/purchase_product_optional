# Test Plan (Migrasi) — purchase_product_optional

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-24

---

## Step 9 — Dev Testing

Eksekusi: `odoo-bin -i purchase_product_optional --test-enable --test-tags /purchase_product_optional
--stop-after-init --without-demo=all` di container 20.0 build-from-source (Mode C + Mode D Tour headless
Chrome). `docker compose down -v` sebelum tiap rerun (gotcha knowledge 19-to-20).

Test existing (BACKFILL, 13) + **test baru migrasi ini** (ditandai *baru*) untuk menutup gap lama
(AC-02-02/AC-04-01/AC-05-02 tanpa test di 18→19) dan jalur yang disentuh breaking change:

| AC | Unit (`TransactionCase`) | Integration (`HttpCase` route) | Tour |
|---|---|---|---|
| AC-01-01 | install G1 (log) | — | — |
| AC-02-01 | — | — | `purchase_product_optional_configurator_tour` |
| AC-02-02 | *baru* `test_simple_product_single_variant_no_configurator` (return `get_single_product_variant`) | — | — |
| AC-02-03 | — | `test_get_values_purchase_returns_optional_product` (+ *baru* asersi `parent_exclusions == {}`), *baru* `test_get_optional_products_route`, *baru* `test_update_combination_route` | Tour (dialog load) |
| AC-03-01 | — | — | Tour (harga tampil — tidak diasersi angka) |
| AC-03-02 | `TestConvertPrice` ×3 (API param diganti `set_int`) | — | — |
| AC-04-01 | — | — | *baru* tour edit ulang (kalau stabil; CAND-08 dua dialog) — kalau tidak stabil, dicatat gap |
| AC-05-01 | — | `test_create_product_creates_dynamic_variant` | — |
| AC-05-02 | — | *baru* `test_get_values_purchase_same_template_exclusions` | — |
| AC-05-03 | — | — | Tour (confirm + baris optional + save) |
| AC-06-01 | `test_currency_not_synced_to_partner_purchase_currency`, `test_onchange_partner_id_mro_shadowing_candidates`, *baru* `test_onchange_stores_currency_param` | — | — |
| AC-06-02 | *baru* asersi `id_vendor` di `test_onchange_stores_currency_param` | — | — |
| AC-07-01 | `test_product_template_and_variant_columns` | — | — |
| AC-08-01 | `TestAttributeValueCompute` ×3 | — | — |
| AC-09-01 | `test_product_add_mode_not_registered_as_field` | — | — |
| AC-09-02 | *baru* `test_id_vendor_label` | — | — |

## Step 10 — QA Testing

**STOP sebelum Step 10** (instruksi user — slot browser/Docker dibatasi). Rencana saat slot diberikan:
AI-interaktif via Playwright MCP (`--http-interface=0.0.0.0`, port 8201) untuk skenario visual yang
tidak diasersi Tour: harga vendor tampil benar (AC-03-01), dua dialog (CAND-08), edit ulang (AC-04-01),
eksklusi visual (AC-05-02).

| AC | Manual | AI-interaktif | AI+tool |
|---|---|---|---|
| AC-03-01, AC-04-01, AC-05-02, CAND-08 | — | Playwright MCP | — |

## Step 11 — UAT

| Kelompok fitur | AC | UAT |
|---|---|---|
| PO + dialog + optional | AC-02, AC-05 | Manual business user |
| Harga vendor | AC-03 | Manual |
| Edit ulang | AC-04 | Manual |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer/AI | Unit/Integration/Tour | Otomatis (Docker) | 18 |
| 10 | QA/AI | AI-interaktif | Menunggu slot | 4 |
| 11 | PM/User | UAT | Manual | 3 kelompok |
