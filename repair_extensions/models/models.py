# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RepairOrder(models.Model):
    _inherit = 'mrp.repair'
    _order = 'state'

    name = fields.Char(readonly=True)
    internal_notes = fields.Text('Internal Notes',
        placeholder="Add internal notes and accessories or damages...")
    quotation_notes = fields.Text('Error Description', required=True,
        placeholder="Add error description and other notes here...")

    invoice_line_id = fields.Many2one(comodel_name="account.invoice.line",
        string="Products from Invoices", ondelete="restrict", index=True,
        readonly=True, states={'draft': [('readonly', False)]},)
    product_brand = fields.Many2one(related='product_id.product_brand_id',
        readonly=True)
    product_category = fields.Many2one(related='product_id.categ_id',
        readonly=True)
    amount_repair_until = fields.Float(string="Repair without quote until",
        placeholder="0", track_visibility="onchange",
        help="Repairable without asking if total is below. 0 indicates that the customer required a quote.")
    technician = fields.Many2one(comodel_name="res.users", String="Technician", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('mrp.repair.tag', string="Tags")
    helpdesk_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Helpdesk Ticket")

    color = fields.Integer('Color Index', default=0)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                    default=lambda self: self.env.user.company_id.currency_id)


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.invoice_line_id = False

    @api.onchange('invoice_line_id')
    def _onchange_invoice_line_id(self):
        self.product_id = self.invoice_line_id.product_id.id

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree')
        result = action.read()[0]
        res = self.env.ref('account.invoice_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['view_id'] = res and res.id or False
        result['res_id'] = self.invoice_line_id.invoice_id.id
        return result

    class Tag(models.Model):
        _name = 'mrp.repair.tag'
        _description = 'Category of Repair Order'

        name = fields.Char('Name', required=True)
        color = fields.Integer('Color Index')

        _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !"),]
