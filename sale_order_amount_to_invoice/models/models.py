# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderAmountToInvoice(models.Model):
    _inherit = 'sale.order'

    amount_to_invoice = fields.Monetary(compute="_calculate_amount_to_invoice")

    @api.one
    @api.depends('order_line.qty_to_invoice')
    def _calculate_amount_to_invoice(self):
        for line in self.order_line:
            self.amount_to_invoice += line.price_reduce_taxinc * line.qty_to_invoice
            if line.product_uom_qty < line.qty_to_invoice:
                self.amount_to_invoice -= line.price_unit
#            if line.product_uom_qty < line.qty_to_invoice:
#                if self.partner_id.is_company = True:
#                    self.amount_to_invoice -= (line.price_unit + price_tax) * line.qty_to_invoice
#                else:
#                    self.amount_to_invoice -= line.price_unit * line.qty_to_invoice
