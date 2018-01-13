# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderAmountToInvoice(models.Model):
    _inherit = 'sale.order'

    amount_to_invoice = fields.Monetary(compute="_calculate_amount_to_invoice", store=True)

    @api.one
    @api.depends('order_line.qty_to_invoice', 'order_line.discount')
    def _calculate_amount_to_invoice(self):
        for line in self.order_line:
            # pricde_reduce_taxinc handles all discount/tax operations
            self.amount_to_invoice += line.price_reduce_taxinc * line.qty_to_invoice
            # detect down payment or sale order lines to be refunded
            # extra calculation necessary because a few fields won't compute with qty = 0
            if line.product_uom_qty < line.qty_invoiced:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if self.partner_id.company_type == 'company':
                    # Add tax to price_unit, amount_total is tax inclusive
                    tax = line.price_unit * line.tax_id.amount / 100
                    self.amount_to_invoice -= (price + tax) * line.qty_invoiced
                else:
                    self.amount_to_invoice -= price * line.qty_invoiced
