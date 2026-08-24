# -*- coding: utf-8 -*-
# BACKFILL (doc-dev-backfill) — tests written retroactively to characterize existing behavior.
# See doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md and doc-dev/backfill/FINDINGS.md for the
# AC/finding each test documents. Do NOT change models/controllers/views based on results here —
# report gaps in FINDINGS.md instead.

import json
import logging

from lxml import etree

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, HttpCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestConvertPrice(TransactionCase):
    """AC-03-01/02/03 — product.template.convert_price(), ref FINDINGS F-05."""

    def test_convert_price_same_currency_no_conversion(self):
        currency = self.env.company.currency_id
        self.env['ir.config_parameter'].sudo().set_param('currency_id', str(currency.id))
        price = self.env['product.template'].convert_price(50.0, currency.id)
        self.assertEqual(price, 50.0)

    def test_convert_price_different_currency_converts(self):
        company = self.env.company
        company_currency = company.currency_id
        # active_test=False: most of the ~170 res.currency records ship inactive by default,
        # a plain search() only sees active ones and can return nothing on a single-currency DB.
        other_currency = self.env['res.currency'].with_context(active_test=False).search(
            [('id', '!=', company_currency.id)], limit=1
        )
        self.assertTrue(other_currency, "Need at least 2 res.currency records to test conversion")
        other_currency.write({'active': True})
        self.env['res.currency.rate'].create({
            'currency_id': other_currency.id,
            'name': fields.Date.today(),
            'rate': 2.0,
            'company_id': company.id,
        })
        self.env['ir.config_parameter'].sudo().set_param('currency_id', str(company_currency.id))
        price = self.env['product.template'].convert_price(100.0, other_currency.id)
        self.assertNotEqual(
            price, 100.0,
            "convert_price should apply a real conversion when from/to currencies differ",
        )

    def test_convert_price_param_not_set_returns_without_raising(self):
        # FINDINGS F-05 (revised after real Step 04 run): ir.config_parameter.get_param()'s
        # default is `False`, not `None` -> int(False) == 0 -> convert_price does NOT raise
        # TypeError as originally assumed. It silently browses currency id 0 (non-existent) and
        # returns a fallback value instead of failing loudly. Documented here, not fixed.
        self.env['ir.config_parameter'].sudo().search([('key', '=', 'currency_id')]).unlink()
        price = self.env['product.template'].convert_price(100.0, self.env.company.currency_id.id)
        _logger.info(
            "BACKFILL F-05: convert_price(100.0, ...) with unset 'currency_id' param "
            "returned %r without raising", price,
        )


@tagged('post_install', '-at_install')
class TestOnchangePartnerCurrency(TransactionCase):
    """AC-03-04/05 — purchase.order.onchange_partner_id(), ref FINDINGS F-02/F-03."""

    def test_currency_not_synced_to_partner_purchase_currency(self):
        # FINDINGS F-03: the 'else' branch does `self.currency_id = self.currency_id` (no-op) —
        # this documents that the PO currency is NOT actually switched to the partner's
        # property_purchase_currency_id in the most common case (partner set, currency differs).
        company_currency = self.env.company.currency_id
        other_currency = self.env['res.currency'].with_context(active_test=False).search(
            [('id', '!=', company_currency.id)], limit=1
        )
        self.assertTrue(other_currency)
        other_currency.write({'active': True})
        partner = self.env['res.partner'].create({
            'name': 'BACKFILL Test Vendor',
            'property_purchase_currency_id': other_currency.id,
        })
        po = self.env['purchase.order'].new({
            'partner_id': partner.id,
            'currency_id': company_currency.id,
        })
        po.onchange_partner_id()
        self.assertEqual(
            po.currency_id, company_currency,
            "Documents F-03: currency_id stays unchanged even though partner's "
            "property_purchase_currency_id differs",
        )

    def test_onchange_partner_id_mro_shadowing_candidates(self):
        # FINDINGS F-02: log every class in the MRO that defines `onchange_partner_id` on
        # purchase.order. If Odoo core also defines one, only the class earliest in the MRO
        # actually runs — the rest are silently shadowed. Read odoo.log for the logged list to
        # confirm/refute F-02 empirically (see 04A_DEV_TESTING.md).
        po_model = type(self.env['purchase.order'])
        defining_classes = [
            f'{cls.__module__}.{cls.__qualname__}'
            for cls in po_model.__mro__
            if 'onchange_partner_id' in cls.__dict__
        ]
        _logger.info(
            "BACKFILL F-02: classes defining purchase.order.onchange_partner_id: %s",
            defining_classes,
        )
        self.assertTrue(defining_classes)


@tagged('post_install', '-at_install')
class TestAttributeValueCompute(TransactionCase):
    """AC-04-01/02/03 — purchase.order.line custom/no-variant attribute value computes."""

    def _make_line(self, product_tmpl, **values):
        order = self.env['purchase.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'BACKFILL PO Vendor'}).id,
        })
        return self.env['purchase.order.line'].new({
            'order_id': order.id,
            'product_id': product_tmpl.product_variant_id.id if product_tmpl else False,
            **values,
        })

    def test_custom_attribute_values_pruned_on_product_change(self):
        attribute = self.env['product.attribute'].create({
            'name': 'BACKFILL Custom Attr', 'create_variant': 'no_variant', 'display_type': 'radio',
        })
        value = self.env['product.attribute.value'].create({
            'name': 'BACKFILL Custom Value', 'attribute_id': attribute.id, 'is_custom': True,
        })
        template_a = self.env['product.template'].create({
            'name': 'BACKFILL Template A',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': attribute.id,
                'value_ids': [(6, 0, [value.id])],
            })],
        })
        template_b = self.env['product.template'].create({'name': 'BACKFILL Template B'})
        ptav = template_a.attribute_line_ids.product_template_value_ids

        line = self._make_line(template_a, product_custom_attribute_value_ids=[(0, 0, {
            'custom_product_template_attribute_value_id': ptav.id,
            'custom_value': 'engraving text',
        })])
        self.assertTrue(line.product_custom_attribute_value_ids)

        line.product_id = template_b.product_variant_id.id
        line._compute_custom_attribute_values()
        self.assertFalse(line.product_custom_attribute_value_ids)

    def test_no_variant_attribute_values_pruned_on_product_change(self):
        attribute = self.env['product.attribute'].create({
            'name': 'BACKFILL No-Variant Attr', 'create_variant': 'no_variant',
        })
        value = self.env['product.attribute.value'].create({
            'name': 'BACKFILL No-Variant Value', 'attribute_id': attribute.id,
        })
        template_a = self.env['product.template'].create({
            'name': 'BACKFILL Template C',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': attribute.id,
                'value_ids': [(6, 0, [value.id])],
            })],
        })
        template_b = self.env['product.template'].create({'name': 'BACKFILL Template D'})
        ptav = template_a.attribute_line_ids.product_template_value_ids

        line = self._make_line(
            template_a,
            product_no_variant_attribute_value_ids=[(6, 0, ptav.ids)],
        )
        self.assertTrue(line.product_no_variant_attribute_value_ids)

        line.product_id = template_b.product_variant_id.id
        line._compute_no_variant_attribute_values()
        self.assertFalse(line.product_no_variant_attribute_value_ids)

    def test_attribute_values_cleared_without_product(self):
        line = self._make_line(False)
        line._compute_custom_attribute_values()
        line._compute_no_variant_attribute_values()
        self.assertFalse(line.product_custom_attribute_value_ids)
        self.assertFalse(line.product_no_variant_attribute_value_ids)


@tagged('post_install', '-at_install')
class TestProductAddModeField(TransactionCase):
    """AC-05-01 — ref FINDINGS F-01."""

    def test_product_add_mode_not_registered_as_field(self):
        self.assertNotIn(
            'product_add_mode',
            self.env['purchase.order.line']._fields,
            "See FINDINGS.md F-01: product_add_mode is swallowed as a kwarg into "
            "fields.Many2many(...) instead of being declared as its own field",
        )


@tagged('post_install', '-at_install')
class TestPurchaseOrderFormViewColumns(TransactionCase):
    """AC-08-01 — merged form view columns for product_template_id / product_id."""

    def test_product_template_and_variant_columns(self):
        result = self.env['purchase.order'].get_view(view_type='form')
        arch = etree.fromstring(result['arch'])
        product_tmpl_fields = arch.xpath("//field[@name='product_template_id']")
        product_id_fields = arch.xpath("//field[@name='product_id']")
        self.assertTrue(product_tmpl_fields, "product_template_id field not found in merged view")
        self.assertTrue(product_id_fields, "product_id field not found in merged view")
        self.assertEqual(product_tmpl_fields[0].get('column_invisible'), '0')
        self.assertEqual(product_id_fields[0].get('optional'), 'hide')


@tagged('post_install', '-at_install')
class TestPurchaseProductOptionalController(HttpCase):
    """AC-06-01/AC-07-01 — controllers/main.py JSON-RPC routes, real HTTP call (Mode B/C)."""

    def setUp(self):
        super().setUp()
        self.optional_attribute = self.env['product.attribute'].create({
            'name': 'BACKFILL Optional Attr', 'create_variant': 'always',
        })
        self.optional_value = self.env['product.attribute.value'].create({
            'name': 'BACKFILL Optional Value', 'attribute_id': self.optional_attribute.id,
        })
        self.optional_template = self.env['product.template'].create({
            'name': 'BACKFILL Optional Product',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.optional_attribute.id,
                'value_ids': [(6, 0, [self.optional_value.id])],
            })],
        })
        self.main_template = self.env['product.template'].create({
            'name': 'BACKFILL Main Product',
            'optional_product_ids': [(6, 0, [self.optional_template.id])],
        })

    def _json_rpc(self, route, params):
        response = self.url_open(
            route,
            data=json.dumps({'jsonrpc': '2.0', 'method': 'call', 'params': params}),
            headers={'Content-Type': 'application/json'},
        )
        return response.json()

    def test_get_values_purchase_returns_optional_product(self):
        self.authenticate('admin', 'admin')
        result = self._json_rpc('/purchase_product_optional/get_values_purchase', {
            'product_template_id': self.main_template.id,
            'quantity': 1,
            'currency_id': self.env.company.currency_id.id,
            'so_date': fields.Date.today().isoformat(),
        })
        payload = result.get('result')
        self.assertIsNotNone(payload, f"Unexpected JSON-RPC error: {result.get('error')}")
        self.assertEqual(len(payload['optional_products']), 1)
        self.assertEqual(
            payload['optional_products'][0]['product_tmpl_id'], self.optional_template.id
        )
        self.assertIn('exclusions', payload['products'][0])

    def test_create_product_creates_dynamic_variant(self):
        self.authenticate('admin', 'admin')
        dynamic_attribute = self.env['product.attribute'].create({
            'name': 'BACKFILL Dynamic Attr', 'create_variant': 'dynamic',
        })
        dynamic_value = self.env['product.attribute.value'].create({
            'name': 'BACKFILL Dynamic Value', 'attribute_id': dynamic_attribute.id,
        })
        dynamic_template = self.env['product.template'].create({
            'name': 'BACKFILL Dynamic Product',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': dynamic_attribute.id,
                'value_ids': [(6, 0, [dynamic_value.id])],
            })],
        })
        ptav = dynamic_template.attribute_line_ids.product_template_value_ids
        self.assertFalse(dynamic_template.product_variant_ids)

        result = self._json_rpc('/purchase_product_optional/create_product', {
            'product_template_id': dynamic_template.id,
            'combination': ptav.ids,
        })
        product_id = result.get('result')
        self.assertIsNotNone(product_id, f"Unexpected JSON-RPC error: {result.get('error')}")
        self.assertTrue(self.env['product.product'].browse(product_id).exists())
