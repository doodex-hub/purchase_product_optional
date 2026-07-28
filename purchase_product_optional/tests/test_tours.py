# -*- coding: utf-8 -*-
"""Wrapper Python untuk Tour `purchase_product_optional_happy_path` (Smoke Test #1).

Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill, 2026-07-28) -- BELUM
dieksekusi via Chrome headless sungguhan. Lihat doc-dev/backfill/test/04A_DEV_TESTING.md dan
static/tests/tours/purchase_product_optional_tour.js untuk catatan risiko selector.
"""
from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseProductOptionalTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'F-02/F-03 Test Vendor'})

        attribute = cls.env['product.attribute'].create({
            'name': 'Tour Test Attribute',
            'create_variant': 'no_variant',
        })
        attr_value = cls.env['product.attribute.value'].create({
            'name': 'Tour Value', 'attribute_id': attribute.id,
        })
        optional_tmpl = cls.env['product.template'].create({
            'name': 'Tour Optional Product',
            'purchase_ok': True,
        })
        cls.main_tmpl = cls.env['product.template'].create({
            'name': 'Tour Configurable Product',
            'purchase_ok': True,
            'optional_product_ids': [(6, 0, [optional_tmpl.id])],
            'attribute_line_ids': [(0, 0, {
                'attribute_id': attribute.id,
                'value_ids': [(6, 0, [attr_value.id])],
            })],
        })

    def test_purchase_product_optional_happy_path_tour(self):
        """Smoke Test #1 (04A_DEV_TESTING.md §1) -- dijalankan sebagai Tour, bukan cuma checklist
        manual. Kalau selector di purchase_product_optional_tour.js belum cocok DOM sungguhan,
        tour ini akan gagal di step terkait -- sesuaikan selector, JANGAN ubah business code.
        """
        self.start_tour("/odoo/purchase", "purchase_product_optional_happy_path", login="admin")
