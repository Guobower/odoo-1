# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'product.template'

    def create_margin_wizard(self):
        view = self.env.ref('sale_margin_wizard.product_template_margin_wizard_form')
        taxes = [(6, 0, self.taxes_id.ids)] or False
        vals = {
            'product_tmpl_id': self.id,
            'price_regular': self.lst_price,
            'price_special': self.special_offer,
            'cost_unit': self.standard_price,
            #'taxes_id': taxes,
        }
        wizard = self.env['product.template.margin.wizard'].create(vals)
        wizard.create_margin_lines(self)
        return {
            'name': ('Product Margin Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template.margin.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
            'context': vals,
        }
