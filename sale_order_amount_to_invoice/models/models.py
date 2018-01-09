# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderAmountToInvoice(models.Model):
    _inherit = 'sale.order'

    amount_to_invoice = fields.Monetary(compute="_calculate_amount_to_invoice", store=True)

    @api.one
    @api.depends('order_line.qty_to_invoice')
    def _calculate_amount_to_invoice(self):
        for line in self.order_line:
            self.amount_to_invoice += line.price_reduce_taxinc * line.qty_to_invoice
            # detect down payment or sale order lines to be refunded
            if line.product_uom_qty < line.qty_invoiced:
                if self.partner_id.company_type == 'company':
                    # Add tax to price_unit, amount_total is tax inclusive
                    self.amount_to_invoice -= (line.price_unit + line.price_tax) * line.qty_invoiced
                else:
                    self.amount_to_invoice -= line.price_unit * line.qty_invoiced
