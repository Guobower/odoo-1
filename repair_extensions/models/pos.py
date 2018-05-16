from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    repair_order_id = fields.Many2one('mrp.repair', string='Repair Order')
    partner_id = fields.Many2one(related='order_id.partner_id')
    is_repair_advance = fields.Boolean(related='product_id.is_repair_advance')
