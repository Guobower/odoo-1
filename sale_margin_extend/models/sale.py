from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

# prepare to pass cost of SO to Invoice in case cost field is editable
"""
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        vals['purchase_price'] = self.purchase_price
        return vals
"""

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_percent = fields.Float(string="Margin (%)", compute="_compute_margin_percent")

    @api.multi
    @api.depends('order_line.margin')
    def _compute_margin_percent(self):
        if self.amount_untaxed:
            self.margin_percent = self.margin / self.amount_untaxed * 100
