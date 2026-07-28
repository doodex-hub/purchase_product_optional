# -*- coding: utf-8 -*-
"""Karakterisasi BR-07/BR-09 -- endpoint JSON RPC di controllers/main.py.

Integration test (HttpCase) karena route ini level controller/HTTP -- bukan Unit.
Ref: doc-dev/backfill/test/03B_TEST_PLAN.md -- 04B_API_TEST.md diputuskan TIDAK dibuat (4 route
ini internal-only, konsumen cuma JS modul sendiri), jadi dites di sini sebagai Integration biasa.

Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill), belum dieksekusi via
Odoo+Postgres nyata di sesi Cowork ini -- lihat doc-dev/backfill/test/04A_DEV_TESTING.md.
"""
import json

from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseProductOptionalControllers(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # NOTE (2026-07-28, real Mode B run): create_variant HARUS diset 'dynamic' di sini, SAAT
        # attribute dibuat -- mengubahnya BELAKANGAN (setelah product_template memakainya) melempar
        # UserError asli Odoo ("You cannot change the Variants Creation Mode... because it is used
        # on the following products"). Ini dikonfirmasi lewat run nyata pertama (lihat
        # docker-env/logs/odoo.log baris ~915), bukan diasumsikan dari baca kode -- test-only fix,
        # tidak menyentuh kode bisnis modul.
        cls.attribute = cls.env['product.attribute'].create({
            'name': 'Integration Test Attribute',
            'create_variant': 'dynamic',
        })
        cls.attr_value_1 = cls.env['product.attribute.value'].create({
            'name': 'A1', 'attribute_id': cls.attribute.id,
        })
        cls.attr_value_2 = cls.env['product.attribute.value'].create({
            'name': 'A2', 'attribute_id': cls.attribute.id,
        })
        cls.optional_tmpl = cls.env['product.template'].create({
            'name': 'Integration Optional Product',
            'sale_ok': True,
            'purchase_ok': True,
        })
        cls.main_tmpl = cls.env['product.template'].create({
            'name': 'Integration Main Product',
            'purchase_ok': True,
            'optional_product_ids': [(6, 0, [cls.optional_tmpl.id])],
            'attribute_line_ids': [(0, 0, {
                'attribute_id': cls.attribute.id,
                'value_ids': [(6, 0, [cls.attr_value_1.id, cls.attr_value_2.id])],
            })],
        })

    def _json_rpc(self, route, params):
        return self.url_open(
            route,
            data=json.dumps({'jsonrpc': '2.0', 'method': 'call', 'params': params}),
            headers={'Content-Type': 'application/json'},
        )

    def test_ac_07_01_get_optional_products_route(self):
        """AC-07-01 (data layer): route get_optional_products mengembalikan
        optional_product_ids milik product template utama."""
        self.authenticate('admin', 'admin')
        combination = self.main_tmpl.attribute_line_ids.product_template_value_ids.ids
        response = self._json_rpc('/purchase_product_optional/get_optional_products', {
            'product_template_id': self.main_tmpl.id,
            'combination': combination,
            'parent_combination': [],
            'currency_id': self.env.company.currency_id.id,
            'so_date': '2026-07-28',
        })
        self.assertEqual(response.status_code, 200)
        result = response.json().get('result')
        self.assertIsNotNone(result, "AC-07-01: route mengembalikan hasil, bukan error")
        returned_tmpl_ids = [p['product_tmpl_id'] for p in result]
        self.assertIn(
            self.optional_tmpl.id, returned_tmpl_ids,
            "AC-07-01: optional_product_ids milik main_tmpl ikut dikembalikan route ini",
        )

    def test_ac_09_01_create_product_route(self):
        """AC-09-01: route create_product membuat product.product baru dari kombinasi
        atribut dynamic.

        NOTE (2026-07-28, run #2): kombinasi SEBELUMNYA salah -- mengoper KEDUA ptav
        (attr_value_1 + attr_value_2) sekaligus untuk SATU attribute line, yang bukan kombinasi
        valid (satu attribute line non-multi cuma boleh punya SATU value terpilih per kombinasi).
        Itu bikin `_create_product_variant` gagal membuat variant (`product_id` balik `False`).
        Diperbaiki: ambil SATU ptav saja. Test-only fix, tidak menyentuh kode bisnis.
        """
        self.authenticate('admin', 'admin')
        combination = self.main_tmpl.attribute_line_ids.product_template_value_ids[:1].ids
        response = self._json_rpc('/purchase_product_optional/create_product', {
            'product_template_id': self.main_tmpl.id,
            'combination': combination,
        })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertNotIn(
            'error', result,
            f"AC-09-01: route tidak boleh error -- {result.get('error')}",
        )
        product_id = result.get('result')
        self.assertTrue(product_id, "AC-09-01: route mengembalikan id product.product baru")
