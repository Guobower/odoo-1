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
    repair_type = fields.Many2one(comodel_name='mrp.repair.type', string="Repair Type", track_visibility='onchange')
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
        for move in self.reference_move_id:
            lot_ids = [x.lot_id.id for x in move.move_line_ids if x.lot_id]
            return {'domain': {'lot_id': [('id', 'in', lot_ids)]}}

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

    @api.onchange('repair_type')
    def _onchange_repair_type(self):
        if self.repair_type:
            self.invoice_method = self.repair_type.invoice_method
            self.partner_invoice_id = self.repair_type.invoice_address.id
            self.tag_ids = [(6,0,self.repair_type.tag_ids.ids)]
            color = self.repair_type.kanban_color
            self.color = color
            self.technician = self.repair_type.technician.id

    # Required to maintain empty stages in Kanban view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['mrp.repair.stage'].search([])
        return stage_ids

    # This is the original function from mrp.repair, overwritten to prevent stock intake through repair order
    @api.multi
    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products
        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        Move = self.env['stock.move']
        for repair in self:
            moves = self.env['stock.move']
            for operation in repair.operations:
                move = Move.create({
                    'name': repair.name,
                    'product_id': operation.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'move_line_ids': [(0, 0, {'product_id': operation.product_id.id,
                                           'lot_id': operation.lot_id.id,
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': operation.product_uom.id,
                                           'qty_done': operation.product_uom_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'location_id': operation.location_id.id, #TODO: owner stuff
                                           'location_dest_id': operation.location_dest_id.id,})],
                    'repair_id': repair.id,
                    'origin': repair.name,
                })
                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            """
            move = Move.create({
                'name': repair.name,
                'product_id': repair.product_id.id,
                'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                'product_uom_qty': repair.product_qty,
                'partner_id': repair.address_id.id,
                'location_id': repair.location_id.id,
                'location_dest_id': repair.location_dest_id.id,
                'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                                           'lot_id': repair.lot_id.id,
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                                           'qty_done': repair.product_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'location_id': repair.location_id.id, #TODO: owner stuff
                                           'location_dest_id': repair.location_dest_id.id,})],
                'repair_id': repair.id,
                'origin': repair.name,
            })
            consumed_lines = moves.mapped('move_line_ids')
            produced_lines = move.move_line_ids
            moves |= move
            moves._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[repair.id] = move.id
            """
        return res

    class RepairStage(models.Model):
        _name = 'mrp.repair.stage'
        _description = 'Stage'
        _order = 'sequence, id'

        name = fields.Char(required=True, translate=True)
        sequence = fields.Integer('Sequence', default=10)
        is_close = fields.Boolean('Closing Kanban Stage', help='Tickets in this stage are considered done.')
        fold = fields.Boolean('Folded', help="Folded in Kanban view")

    class RepairType(models.Model):
        _name = 'mrp.repair.type'
        _description = 'Repair Type'
        _order = 'sequence, id'

        active = fields.Boolean('Active', default=True)
        name = fields.Char(required=True, translate=True)
        sequence = fields.Integer('Sequence', default=10)
        invoice_method = fields.Selection(string='Invoice Method', selection='repair_type_sel')
        invoice_address = fields.Many2one('res.partner', string='Invoice Address')
        tag_ids = fields.Many2many('mrp.repair.tag', string='Tags')
        kanban_color = fields.Integer('Color Index')
        technician = fields.Many2one('res.users', string='Technician', help="Sets a default Technician for every Repair Order of this type.")

        @api.model
        def repair_type_sel(self):
            return [
                ('none', 'No Invoice'),
                ('b4repair', 'Before Repair'),
                ('after_repair', 'After Repair'),
                ]



    class Tag(models.Model):
        _name = 'mrp.repair.tag'
        _description = 'Category of Repair Order'

        name = fields.Char('Name', required=True)
        color = fields.Integer('Color Index')

        _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !"),]
