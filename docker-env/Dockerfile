# Instance BARU untuk migrasi 18.0 (Step 6, Checkpoint G1) — TERPISAH dari instance BACKFILL
# 17.0 (`docker-env/` di `source-codebase`, port 8079). Dibuat 2026-07-29.
#
# Warisan lesson dari BACKFILL (17.0, lihat CLAUDE.md sumber `purchase-product-optional` untuk
# kronologi lengkap run #3-#6):
# - `websocket-client` WAJIB di-install di layer IMAGE (build), BUKAN lewat override `entrypoint`/
#   `command` — image resmi Odoo punya entrypoint script yang menerjemahkan env var
#   HOST/USER/PASSWORD jadi koneksi db, kalau di-override itu ikut hilang dan container gagal start
#   total.
# - `pip3 install` di image ini TIDAK pakai `--break-system-packages` (pip bawaan image lebih lama
#   dari 23.0.1, flag itu tidak dikenal — beda dari environment Cowork sandbox biasa).
# - Chrome/Chromium TIDAK tersedia di image resmi `odoo:17.0` — Tour & QUnit sempat di-skip karena
#   ini. **Belum diverifikasi apakah `odoo:18.0` sama** — cek ulang saat G1 pertama, jangan asumsikan
#   otomatis sama ataupun otomatis berbeda. Kalau gagal install Chrome lagi, JANGAN dikejar lebih
#   dari 1 percobaan wajar (batas workaround test-only) — cukup catat sebagai limitasi lingkungan,
#   sama seperti keputusan run #6 BACKFILL.
# !! REVISI 2026-07-29 !! -- build pertama gagal exit code 1 di `pip3 install websocket-client`.
# Beda dari image odoo:17.0 (pip lama, TIDAK kenal --break-system-packages) -- base image
# odoo:18.0 kemungkinan sudah pakai pip lebih baru yang menegakkan PEP 668
# (externally-managed-environment), MENOLAK pip install biasa di luar virtualenv. Fix: coba
# --break-system-packages dulu, fallback ke pip3 biasa kalau flag itu tidak dikenal (kebalikan
# dari kasus 17.0) -- supaya Dockerfile ini tetap jalan di kedua kemungkinan tanpa perlu tebak
# versi pip persis.
FROM odoo:18.0
USER root
RUN pip3 install --break-system-packages websocket-client \
    || pip3 install websocket-client
USER odoo
