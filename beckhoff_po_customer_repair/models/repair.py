# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Repair(models.Model):
    _inherit = "mrp.repair"

    purchased_orders = fields.Integer(compute="_compute_purchased_orders_number",
                                      string="Quantity of Purchase Orders, based on that Repair Order")

    def _compute_purchased_orders_number(self):
        self.purchased_orders = len(self.env['purchase.order'].search([('repair_order_id', '=', self.id)]).ids)

    def create_purchase_order_repair(self):
        view = self.env.ref('beckhoff_po_customer_repair.purchase_order_repair_wizard_form')
        vals = {
            'partner_id': self.partner_id.id,
            'salesperson_id': self.technician.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'repair_order_id': self.id,
        }
        wizard = self.env['purchase.order.repair.wizard'].create(vals)
        wizard.create_po_lines_from_so(self)
        return {
            'name': ('Create wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.repair.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
            'context': vals,
        }

class RepairOrderLinePOfromRepair(models.Model):
    _inherit = 'mrp.repair.line'

    forecasted_qty = fields.Float(related='product_id.virtual_available', string='Forecast Quantity',
                                     help="Forecast quantity (computed as Quantity On Hand "
                                          "- Outgoing + Incoming)\n"
                                          "In a context with a single Stock Location, this includes "
                                          "goods stored in this location, or any of its children.\n"
                                          "In a context with a single Warehouse, this includes "
                                          "goods stored in the Stock Location of this Warehouse, or any "
                                          "of its children.\n"
                                          "Otherwise, this includes goods stored in any Stock Location "
                                          "with 'internal' type.")

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        self.forecasted_qty = self.product_id.virtual_available - self.product_uom_qty
