# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderAmountToInvoice(models.Model):
    _inherit = 'sale.order'

    amount_to_invoice = fields.Monetary(compute="_calculate_amount_to_invoice")

    @api.one
    @api.depends('order_line.qty_to_invoice')
    def _calculate_amount_to_invoice(self):
        amount_to_invoice = 0
        for line in self.order_line:
            self.amount_to_invoice += line.price_reduce_taxexcl * line.qty_to_invoice
