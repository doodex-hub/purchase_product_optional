# Dev Testing — purchase_product_optional

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-24
**Revisi diuji:** `migration/20.0` @ `ad6a1fa` (kode = `b8ca459`)

---

Eksekusi resmi lewat wrapper (dari `purchase_product_optional/docker-env/`):

```bash
bash run-test.sh ppo_step9
```

Wrapper: `docker compose down -v` sebelum & sesudah, `MSYS_NO_PATHCONV=1`, `--test-enable --test-tags
/purchase_product_optional --stop-after-init`, sanity check jumlah "Starting". Environment: Odoo 20.0
build-from-source (`odoo20` read-only), Postgres 16, Chrome 153 headless (Mode D). Demo data default OFF
di 20.0. Log: `docker-env/logs/step9-final.out` (gitignored).

## 9a. Audit Kesiapan Test

1. **Registrasi:** `tests/__init__.py` meng-import kedua file `test_*.py` — tidak ada file yatim.
2. **Isi method (audit `ast` di dalam image, host tanpa Python):** 19 method test, **0 stub**. 18 punya
   `assert*`/`start_tour`; 1 (`test_convert_price_param_not_set_returns_without_raising`, warisan
   BACKFILL) sengaja hanya memverifikasi "tidak raise" + log — valid untuk BSL-018.

| AC | File test | Status | Catatan |
|---|---|---|---|
| AC-01-01 ⚠️ | G1 log + install bagian run | ✅ Lengkap | |
| AC-02-01 ⚠️ | Tour `purchase_product_optional_configurator_tour` | ✅ Lengkap | |
| AC-02-02 | `test_simple_product_single_variant_no_configurator` | ✅ Lengkap (input keputusan JS) | Cabang JS sendiri tidak dieksekusi tour |
| AC-02-03 ⚠️ | 5 HttpCase route | ✅ Lengkap | |
| AC-03-01 | Tour (dialog harga dirender) | ⚠️ Parsial | Angka harga vendor tidak diasersi — Step 10 |
| AC-03-02 ⚠️ | `TestConvertPrice` ×3 | ✅ Lengkap | |
| AC-04-01 | — | ❌ Tidak ada | MF-04 (jalur memicu CAND-08; butuh pembanding 19.0 live) — Step 10 |
| AC-05-01 ⚠️ | `test_create_product_creates_dynamic_variant` | ✅ Lengkap | |
| AC-05-02 | `test_get_values_purchase_same_template_exclusions` | ✅ Lengkap (backend) | Visual Step 10 |
| AC-05-03 ⚠️ | Tour step 11-15 | ✅ Lengkap | |
| AC-06-01 ⚠️ | 3 test `TestOnchangePartnerCurrency` | ✅ Lengkap | |
| AC-06-02 | `test_onchange_stores_currency_param` | ✅ Lengkap | |
| AC-07-01 ⚠️ | `test_product_template_and_variant_columns` | ✅ Lengkap | |
| AC-08-01 | `TestAttributeValueCompute` ×3 | ✅ Lengkap | |
| AC-09-01/02 | 2 test `TestProductAddModeField` | ✅ Lengkap | |

**Verdict audit:** semua AC ⚠️ risiko tinggi berstatus Lengkap. AC-04-01 (bukan ⚠️) dan bagian visual
AC-03-01/AC-05-02 tidak tercakup otomatis — gap eksplisit, dialihkan ke Step 10 (MF-04), bukan
diam-diam dianggap tercakup.

## Baseline

- Test asli source (BACKFILL, lokasi sama dengan source `migration/19.0` — `01a` §4): 13 test, hasil
  terakhir di 19.0 **13/13 pass + Tour sukses** (`migration-records/purchase_product_optional_18.0_19.0/SUMMARY.md`
  §Metrik, 2026-08-26). Kode test itu identik di `migration/19.0`; tidak dijalankan ulang di 19.0 pada
  sesi ini.
- Applicability Fase E: **Ya** — Tour wajib ada: `purchase_product_optional_configurator_tour` ✅.

## Hasil Unit, Integration & Tour Test (target 20.0)

Ringkasan Odoo: **`0 failed, 0 error(s) of 21 tests`** (19 test modul + 2 `WebSuite`/`MobileWebSuite`
yang dijalankan runner untuk tag modul — tanpa hoot test modul, pass). Sanity: 24 baris "Starting".
Tour: `[15/15]` → `tour succeeded`; browser log "Owl is running in 'dev' mode" (validasi schema
`useProps` aktif); 0 `console.error`/`OwlError`. Warning modul hanya baseline (BSL-009, BSL-017).

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | — | — | ✅ Pass | install bersih |
| AC-02-01 | — | — | configurator tour | ✅ Pass | judul "Configure your product" terverifikasi |
| AC-02-02 | simple product | — | — | ✅ Pass | |
| AC-02-03 | — | get_values (+parent_exclusions `{}`), get_optional_products, update_combination, same-template exclusions, create_product | — | ✅ Pass | |
| AC-03-02 | 3 | — | — | ✅ Pass | API `get_int`/`set_int` |
| AC-05-01 | — | create_product | — | ✅ Pass | |
| AC-05-02 | — | same-template exclusions | — | ✅ Pass | |
| AC-05-03 | — | — | tour 11-15 | ✅ Pass | baris optional + save |
| AC-06-01/02 | 3 | — | — | ✅ Pass | |
| AC-07-01 | 1 | — | — | ✅ Pass | |
| AC-08-01 | 3 | — | — | ✅ Pass | |
| AC-09-01/02 | 2 | — | — | ✅ Pass | |
| AC-03-01, AC-04-01 | — | — | — | ⏸ Step 10 | MF-04 |

Loop test→fix: run pertama G2 (`logs/g2-run1.out`) sudah pass tanpa perbaikan tambahan; run resmi ini
mengulang di HEAD ter-commit dengan hasil identik.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di luar CAND-01..06. Catatan operasional: `run-test.sh` + image
  build-from-source milik `optional_field_save` 20.0 terpakai ulang dengan cache hit penuh (build <1 menit).

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration/Tour pass — **siap Step 10** (Step 10 TIDAK dimulai — menunggu
  slot dari user, sesuai instruksi).

## Rerun Step 10 (loop-back, 2026-09-24)

Dipicu 2 perubahan dari Step 10: (1) tour memakai `stepUtils.showAppsMenuItem()` agar jalan dengan
`web_enterprise` (MF-05), (2) fix ikon RMV-02 + 2 step asersi ikon di tour (total 17 step).

| Run | Modul ter-install | Hasil | Log |
|---|---|---|---|
| Community | `purchase_product_optional` | `0 failed, 0 error(s) of 21 tests`, Tour `[17/17]` `tour succeeded` | `docker-env/logs/step10-comm2.out` |
| Enterprise 20 | + `account_budget_purchase`, `purchase_quality_control` (124 modul, termasuk `web_enterprise`) | `0 failed, 0 error(s) of 21 tests`, Tour `tour succeeded` | `docker-env/logs/step10-ent3.out` |

Perintah Enterprise:

```bash
bash run-test.sh ppo_ent "" account_budget_purchase,purchase_quality_control
```
