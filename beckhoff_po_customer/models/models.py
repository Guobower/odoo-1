# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api

class CustomerToPo(models.Model):
    _inherit = 'purchase.order'

    customer = fields.Many2one('res.partner', 'Customer', track_visibility='OnChange')
    salesperson = fields.Many2one('res.users','Salesperson', track_visibility='OnChange')
    salesteam_id = fields.Many2one('crm.team', string='Salesteam', default=lambda self:self.env.user.sale_team_id.id)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order",
                                    help="Not empty if an origin for purchase order was sale order")

    # Remove the total amount from the purchase order path
    @api.multi
    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = []
        for po in self:
            name = po.name
            if po.partner_ref:
                name += ' ('+po.partner_ref+')'
            if po.amount_total:
                name += ' ' #+ formatLang(self.env,  po.amount_total, currency_obj=po.currency_id)
            result.append((po.id, name))
        return result

    @api.onchange('salesperson')
    def _onchange_salesperson(self):
        self.salesteam_id = self.salesperson.sale_team_id.id

class CustomerPoCounter(models.Model):
    _inherit = 'res.partner'

    customer_purchase_order = fields.Integer(compute='_purchase_invoice_count', string='# of Purchase Orders')

    @api.one
    def _purchase_invoice_count(self):
        cond = [('customer', '=', self.id)]
        self.customer_purchase_order = len(self.env['purchase.order'].search(cond))
