# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class SaleOrderLineAbsoluteDiscount(models.Model):
    _inherit = 'sale.order.line'

    discount_absolute = fields.Float(string="Discount (Euro)", default=0.0, help="Only one discount mode can be active for a sale order line.")
    # track_visibility onchange?

    @api.constrains('discount_absolute')
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_absolute')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.discount_absolute > 0:
                if line.discount_absolute > line.price_unit:
                    raise Warning("Discount cannot be greater than Unit price.")
                else:
                    price = line.price_unit - line.discount_absolute
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
})
