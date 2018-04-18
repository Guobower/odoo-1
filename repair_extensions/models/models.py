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

    reference_move_id = fields.Many2one(
        comodel_name='stock.move', string='Originating Stock Move',
        copy=False,
        readonly=True, states={'draft': [('readonly', False)]},)
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
    stage_id = fields.Many2one(comodel_name='mrp.repair.stage', group_expand='_read_group_stage_ids', string='Stage', track_visibility='onchange')
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                    default=lambda self: self.env.user.company_id.currency_id)


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.invoice_line_id = False

    @api.onchange('invoice_line_id')
    def _onchange_invoice_line_id(self):
        self.product_id = self.invoice_line_id.product_id.id

    @api.onchange('reference_move_id')
    def _onchange_reference_move_id(self):
        self.product_id = self.reference_move_id.product_id.id

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree')
        result = action.read()[0]
        invoice_ids = picking_ids = []
        for line in self.reference_move_id.sale_line_id.order_id.invoice_ids:
            invoice_ids.append(line.id)
        invoices = list(set(invoice_ids))
        if invoices:
            if len(invoices) > 1:
                result['domain'] = [('id', 'in', invoices)]
            else:
                res = self.env.ref('account.invoice_form', False)
                result['views'] = [(res and res.id or False, 'form')]
                result['res_id'] = invoices[0]
        return result

    # Required to maintain empty stages in Kanban view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['mrp.repair.stage'].search([])
        return stage_ids

    class RepairStage(models.Model):
        _name = 'mrp.repair.stage'
        _description = 'Stage'
        _order = 'sequence, id'

        name = fields.Char(required=True, translate=True)
        sequence = fields.Integer('Sequence', default=10)
        is_close = fields.Boolean('Closing Kanban Stage', help='Tickets in this stage are considered done.')
        fold = fields.Boolean('Folded', help="Folded in Kanban view")


    class Tag(models.Model):
        _name = 'mrp.repair.tag'
        _description = 'Category of Repair Order'

        name = fields.Char('Name', required=True)
        color = fields.Integer('Color Index')

        _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !"),]
