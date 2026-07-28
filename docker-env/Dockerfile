# Instansiasi Mode B, Step 04 -- purchase_product_optional.
# Dibuat 2026-07-28 setelah run #3 gagal total (container tidak pernah start sama sekali).
#
# Root cause run #3: docker-compose.yml sebelumnya override `entrypoint: []` supaya bisa
# menyisipkan `pip3 install websocket-client` di depan command lewat `bash -c "... && odoo ..."`.
# Itu SALAH -- image resmi `odoo:17.0` punya entrypoint script yang menerjemahkan env var
# HOST/USER/PASSWORD (di docker-compose.yml) jadi argumen koneksi database (`db:5432`) untuk
# proses odoo. Begitu entrypoint dibuang, terjemahan itu ikut hilang, container gagal start
# sebelum sempat menulis satu baris log pun (terbukti dari mtime odoo.log yang tidak berubah
# sama sekali dari run #2).
#
# Fix: install websocket-client di layer IMAGE (build step), bukan di command/entrypoint --
# supaya entrypoint bawaan image tetap utuh dan command di docker-compose.yml bisa dikembalikan
# persis seperti versi yang SUDAH TERBUKTI jalan di run #1 dan run #2.
#
# !! REVISI run #4 (2026-07-28) !! -- build gagal: "no such option: --break-system-packages".
# pip3 bawaan image odoo:17.0 versinya lebih lama dari pip 23.0.1 (yang pertama kali menambah
# flag ini untuk PEP 668 externally-managed-environment) -- flag itu tidak dikenal, jadi dibuang.
#
# !! REVISI run #4/#5 (2026-07-28) !! -- setelah websocket-client terpasang, Tour & QUnit
# (HttpCase.browser_js/start_tour) masih di-skip, kali ini dengan pesan "Chrome executable not
# found" -- image odoo:17.0 resmi tidak menyertakan Chrome/Chromium.
#
# !! REVISI run #6 (2026-07-28) -- DIHENTIKAN, BUKAN diperbaiki !! -- percobaan `apt-get install
# chromium` GAGAL (exit code 100, package/repo tidak tersedia di image ini). Ini environment gap
# yang SUDAH DIANTISIPASI di komentar atas -- "di luar scope BACKFILL untuk menyiapkan itu".
# Sesuai batas workaround di CLAUDE.md (satu percobaan wajar, gagal -> stop, jangan coba
# variasi lain), TIDAK dicoba lagi dengan source apt berbeda dsb. Dockerfile dikembalikan ke
# versi yang SUDAH TERBUKTI jalan (websocket-client saja) -- Tour & QUnit tetap SKIP karena
# Chrome, dicatat sebagai limitasi lingkungan di FINDINGS.md/04A_DEV_TESTING.md, bukan blocker
# gate Step 04. Kalau dev mau Tour/QUnit benar-benar jalan, perlu image custom Doodex yang sudah
# menyertakan Chrome/Chromium -- di luar scope sesi ini.
FROM odoo:17.0
USER root
RUN pip3 install websocket-client
USER odoo
