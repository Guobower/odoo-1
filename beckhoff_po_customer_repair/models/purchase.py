# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    repair_order_id = fields.Many2one('mrp.repair', string="Repair Order")
