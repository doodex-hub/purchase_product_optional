# -*- coding: utf-8 -*-
"""Karakterisasi BR-04/BR-08/F-01 — field `product_add_mode` & compute attribute values.

Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill), belum dieksekusi via
Odoo+Postgres nyata di sesi Cowork ini — lihat doc-dev/backfill/test/04A_DEV_TESTING.md.
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseOrderLineFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'F-01/F-08 Test Vendor'})
        cls.attribute = cls.env['product.attribute'].create({
            'name': 'F-08 Test Attribute',
            'create_variant': 'no_variant',
        })
        cls.attr_value_1 = cls.env['product.attribute.value'].create({
            'name': 'Value 1', 'attribute_id': cls.attribute.id,
        })
        cls.attr_value_2 = cls.env['product.attribute.value'].create({
            'name': 'Value 2', 'attribute_id': cls.attribute.id,
        })
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'F-08 Test Product',
            'purchase_ok': True,
            'attribute_line_ids': [(0, 0, {
                'attribute_id': cls.attribute.id,
                'value_ids': [(6, 0, [cls.attr_value_1.id, cls.attr_value_2.id])],
            })],
        })
        cls.product = cls.product_tmpl.product_variant_ids[:1]
        cls.other_product = cls.env['product.product'].create({'name': 'F-08 Other Product'})
        cls.po = cls.env['purchase.order'].create({'partner_id': cls.partner.id})

    # ------------------------------------------------------------------
    # AC-04 — product_add_mode dead field (BR-04 / F-01)
    # ------------------------------------------------------------------

    def test_ac_04_01_module_loads(self):
        """AC-04-01: modul berhasil di-import tanpa SyntaxError (kalau baris 24-28
        purchase_order_line.py benar-benar SyntaxError, TIDAK ADA test di file ini yang bisa
        jalan sama sekali -- import akan gagal duluan sebelum test manapun dikoleksi).
        """
        self.assertTrue(
            self.env['purchase.order.line']._fields,
            "AC-04-01: model purchase.order.line berhasil ter-load",
        )

    def test_ac_04_02_product_add_mode_field_missing(self):
        """AC-04-02 / F-01: `product_add_mode` TIDAK terdaftar sebagai field nyata di
        purchase.order.line -- kesalahan parenthesis membuatnya jadi kwarg inert ke
        fields.Many2many() alih-alih field tersendiri.
        """
        self.assertNotIn(
            'product_add_mode', self.env['purchase.order.line']._fields,
            "AC-04-02 (F-01): product_add_mode SEHARUSNYA tidak terdaftar (bug parenthesis "
            "purchase_order_line.py:24-28) -- kalau assertion ini GAGAL, F-01 sudah diperbaiki, "
            "update FINDINGS.md jadi RESOLVED",
        )

    # ------------------------------------------------------------------
    # AC-08 — compute fields membersihkan value tidak valid (BR-08)
    # ------------------------------------------------------------------

    def test_ac_08_01_custom_attribute_values_cleared_on_product_change(self):
        """AC-08-01: _compute_custom_attribute_values membersihkan custom value yang tidak lagi
        valid untuk product_id baru."""
        ptav = self.product_tmpl.attribute_line_ids.product_template_value_ids[:1]
        line = self.env['purchase.order.line'].create({
            'order_id': self.po.id,
            'product_id': self.product.id,
            'product_qty': 1,
            'product_custom_attribute_value_ids': [(0, 0, {
                'custom_product_template_attribute_value_id': ptav.id,
                'custom_value': 'test value',
            })],
        })
        self.assertTrue(line.product_custom_attribute_value_ids)
        line.product_id = self.other_product
        line._compute_custom_attribute_values()
        self.assertFalse(
            line.product_custom_attribute_value_ids,
            "AC-08-01: custom attribute value lama dibersihkan setelah product_id diganti",
        )

    def test_ac_08_02_no_variant_attribute_values_cleared_on_product_change(self):
        """AC-08-02: _compute_no_variant_attribute_values membersihkan no-variant value yang
        tidak lagi valid untuk product_id baru."""
        ptav = self.product_tmpl.attribute_line_ids.product_template_value_ids[:1]
        line = self.env['purchase.order.line'].create({
            'order_id': self.po.id,
            'product_id': self.product.id,
            'product_qty': 1,
        })
        line.product_no_variant_attribute_value_ids = [(6, 0, ptav.ids)]
        self.assertTrue(line.product_no_variant_attribute_value_ids)
        line.product_id = self.other_product
        line._compute_no_variant_attribute_values()
        self.assertFalse(
            line.product_no_variant_attribute_value_ids,
            "AC-08-02: no-variant attribute value lama dibersihkan setelah product_id diganti",
        )
