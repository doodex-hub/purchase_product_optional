# -*- coding: utf-8 -*-
"""Wrapper Python untuk menjalankan+melaporkan hasil QUnit suite modul ini.

Provenance: [HASIL-BACA]. Ditambahkan BACKFILL (Step 04, backfill, 2026-07-28) SETELAH run #2
Mode B menunjukkan bundle `web.qunit_suite_tests` berhasil di-generate (log
`docker-env/logs/odoo.log` baris ~983) TAPI tidak ada hasil pass/fail per test QUnit yang
dilaporkan -- artinya `--test-tags=/purchase_product_optional` saja TIDAK cukup untuk benar-benar
MENJALANKAN suite QUnit, cuma membangun bundle asset-nya. Wrapper ini (pola umum di addon Odoo yang
punya QUnit test sendiri) memakai `HttpCase.browser_js` untuk membuka `/web/tests` yang di-filter
ke modul ini lewat Chrome headless dan menunggu hasil sungguhan.

Belum dieksekusi -- lihat doc-dev/backfill/test/04A_DEV_TESTING.md untuk status run #2/#3.
"""
from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseProductOptionalQUnit(HttpCase):

    def test_qunit_suite(self):
        """Jalankan suite QUnit `purchase_product_optional` (product_configurator_dialog_tests.js
        + purchase_product_field_tests.js) lewat Chrome headless, tunggu semua test selesai."""
        self.browser_js(
            url_path="/web/tests?module=purchase_product_optional",
            code="",
            ready="",
            login="admin",
            timeout=120,
        )
