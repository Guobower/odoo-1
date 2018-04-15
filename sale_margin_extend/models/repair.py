# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import openerp.addons.decimal_precision as dp


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    margin = fields.Float(
        'Margin', compute='_compute_margin', store=True,
        digits=dp.get_precision('Product Price'))

    purchase_price = fields.Float(
        'Cost Price', compute='_compute_margin', store=True,
        digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('product_id', 'product_uom_qty', 'price_subtotal')
    def _compute_margin(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0
                line.margin = 0
            else:
                line.purchase_price = line.product_id.standard_price
                line.margin = line.price_subtotal - (
                line.product_id.standard_price * line.product_uom_qty)

class MrpRepairFee(models.Model):
    _inherit = 'mrp.repair.fee'

    margin = fields.Float(
        'Margin', compute='_compute_margin', store=True,
        digits=dp.get_precision('Product Price'))

    purchase_price = fields.Float('Cost Price', compute='_compute_margin', store=True,
        digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('product_id', 'product_uom_qty', 'price_subtotal')
    def _compute_margin(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0
                line.margin = 0
            else:
                line.purchase_price = line.product_id.standard_price
                line.margin = line.price_subtotal - (
                line.product_id.standard_price * line.product_uom_qty)

class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    margin = fields.Float(
        'Margin', compute='_compute_margin', store=True, digits=dp.get_precision('Product Price'),
        help="It gives profitability by calculating the difference between"
        " the Unit Price and the cost price.")
    margin_percent = fields.Float(string="Margin (%)", compute="_compute_margin")

    @api.one
    @api.depends('fees_lines.margin', 'operations.margin')
    def _compute_margin(self):
        for order in self:
            order.margin = sum(order.mapped('fees_lines.margin')) + sum(order.mapped('operations.margin'))
        self.margin_percent = self.margin / self.amount_untaxed * 100
