# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_margin_wizard(self):
        view = self.env.ref('sale_margin_wizard.sale_order_margin_wizard_form')
        vals = {
            'partner_id': self.partner_id.id,
            'salesperson_id': self.user_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'sale_order_id': self.id,
            'pricelist_id': self.pricelist_id.id,
            #'fiscal_pos': self.fiscal_position_id.id,
        }
        wizard = self.env['sale.order.margin.wizard'].create(vals)
        wizard.create_so_lines(self)
        return {
            'name': ('Sale Margin Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.margin.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': wizard.id,
            'context': vals,
            'flags': {'form': {'action_buttons': True, 'options':{'mode': 'edit'}}}
        }
