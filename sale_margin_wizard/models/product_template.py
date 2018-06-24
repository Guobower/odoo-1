# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'product.template'

    def create_margin_wizard(self):
        view = self.env.ref('sale_margin_wizard.product_template_margin_wizard_form')
        tax_factor = 0
        for tax in self.taxes_id:
            tax_factor += tax.amount
        if self.special_offer > 0:
            has_special_price = True
        else:
            has_special_price = False
        vals = {
            'product_tmpl_id': self.id,
            'price_regular': self.lst_price,
            'price_regular_net': self.gross_net,
            'price_special': self.special_offer,
            'cost_unit': self.standard_price,
            'taxes_id': [(6, 0, self.taxes_id.ids)] or False,
            'tax_factor': tax_factor,
            'has_special_price': has_special_price,
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
