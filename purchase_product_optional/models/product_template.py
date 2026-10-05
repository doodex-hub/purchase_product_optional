# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    """
    Inherit the model product.template to add custom functionality.
    """

    def convert_price(self, price, from_currency, to_currency=None):
        """
        Convert the price from one currency to another.
        
        :param price: The amount in the original currency
        :param from_currency: ID of the original currency
        :param to_currency: ID of the target currency (the purchase order currency).
                            Defaults to the current company currency.
        :return: The converted price in the target currency
        """
        currency_obj = self.env['res.currency']
        from_currency = currency_obj.browse(from_currency)
        to_currency = currency_obj.browse(to_currency) if to_currency else self.env.company.currency_id
        if from_currency == to_currency:
            return price
        price = from_currency._convert(
            from_amount=price,
            to_currency=to_currency,
        )
        return price
