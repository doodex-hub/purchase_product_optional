# -*- coding: utf-8 -*-
# BACKFILL (doc-dev-backfill) — Step 07, Mode E (headless Tour, see
# doc-dev-backfill/ai-doc/USAGE_GUIDE.md §Mode E). Exercises the real product configurator dialog
# JS/OWL flow (BR-01/AC-01-01) through Odoo's own headless Chrome — this is what the blocked
# Claude Browser MCP session (07B_QA_AI_BROWSER.md) was meant to verify visually.

from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestPurchaseProductOptionalTour(HttpCase):

    def setUp(self):
        super().setUp()
        opt_attr = self.env['product.attribute'].create({
            'name': 'BACKFILL Tour Opt Attr', 'create_variant': 'always',
        })
        opt_val = self.env['product.attribute.value'].create({
            'name': 'Only Value', 'attribute_id': opt_attr.id,
        })
        opt_tmpl = self.env['product.template'].create({
            'name': 'BACKFILL QA Optional Product',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': opt_attr.id, 'value_ids': [(6, 0, [opt_val.id])],
            })],
        })
        self.env['product.template'].create({
            'name': 'BACKFILL QA Main Product',
            'optional_product_ids': [(6, 0, [opt_tmpl.id])],
        })
        self.env['res.partner'].create({'name': 'BACKFILL QA Vendor'})

    def test_product_configurator_dialog_tour(self):
        self.start_tour("/web", "purchase_product_optional_configurator_tour", login="admin")
