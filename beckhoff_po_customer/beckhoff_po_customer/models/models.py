# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomerToPo(models.Model):
    _inherit = 'purchase.order'

    customer = fields.Many2one('res.partner', 'Customer', track_visibility='OnChange')
    salesperson = fields.Many2one('res.users','Salesperson', track_visibility='OnChange')
    opportunity = fields.Many2one('crm.lead', 'Opportunity', track_visibility='OnChange')

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

class CustomerPoCounter(models.Model):
    _inherit = 'res.partner'

    customer_purchase_order = fields.Integer(compute='_purchase_invoice_count', string='# of Purchase Orders')

    @api.one
    def _purchase_invoice_count(self):
        cond = [('customer', '=', self.id)]
        self.customer_purchase_order = len(self.env['purchase.order'].search(cond))

class OpportunityPoCounter(models.Model):
    _inherit = 'crm.lead'

    opportunity_purchase_order = fields.Integer(compute='_opportunity_purchase_order_count', string='# of Purchase Orders')

    @api.one
    def _opportunity_purchase_order_count(self):
        cond = [('opportunity', '=', self.id)]
        self.opportunity_purchase_order = len(self.env['purchase.order'].search(cond))
