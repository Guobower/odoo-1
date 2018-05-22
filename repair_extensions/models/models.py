# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RepairOrder(models.Model):
    _inherit = 'mrp.repair'
    _order = 'state'

    name = fields.Char(readonly=True)
    partner_id = fields.Many2one(required=True)
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
    stage_id = fields.Many2one(comodel_name='mrp.repair.stage', group_expand='_read_group_stage_ids',
        string='Stage', track_visibility='onchange')
    repair_type = fields.Many2one(comodel_name='mrp.repair.type', string="Repair Type", track_visibility='onchange')
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
        default=lambda self: self.env.user.company_id.currency_id)

    # Advance Payment fields
    pos_order_ids = fields.One2many('pos.order.line', 'order_id')
    pos_advance_pay_count = fields.Integer(string="# of Advance Payments", compute='_compute_advance_payments')

    # Timesheet fields
    task_id = fields.Many2one(related='helpdesk_ticket_id.task_id', string="Task")
    project_id = fields.Many2one(related='helpdesk_ticket_id.project_id', string="Project")
    is_closed = fields.Boolean(related='helpdesk_ticket_id.is_closed', string="Is Closed")
    is_task_active = fields.Boolean(related='helpdesk_ticket_id.is_task_active', string="Task Active")
    timesheet_ids = fields.One2many(related='helpdesk_ticket_id.task_id.timesheet_ids', string="Timesheets")

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

    @api.multi
    def action_view_pos_orders(self):
        action = self.env.ref('point_of_sale.action_pos_order_line')
        result = action.read()[0]
        pos_ids = []
        pos_order_ids = self.env['pos.order'].search([('partner_id', '=', self.partner_id.id)])
        for order in pos_order_ids:
            for line in order.lines:
                if line.is_repair_advance == True and not line.repair_order_id:
                    pos_ids.append(order.id)
        pos_orders = list(set(pos_ids))
        result['domain'] = [('id', 'in', pos_orders)]
        return result

    def _compute_advance_payments(self):
        pos_order_ids = self.env['pos.order'].search([('partner_id', '=', self.partner_id.id)])
        pos_ids = []
        for order in pos_order_ids:
            for line in order.lines:
                if line.is_repair_advance == True and not line.repair_order_id:
                    pos_ids.append(order.id)
        self.pos_advance_pay_count = len(pos_ids)

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

    # Overwrite build-in function to deactivcate insufficent stock popup on confirmation
    def action_validate(self):
        return self.action_repair_confirm()


    def reconcile_advance_payments(self):
        view = self.env.ref('repair_extensions.mrp_repair_reconcile_wizard_form')
        vals = {
            'partner_id': self.partner_id.id,
            'repair_order_id': self.id,
        }
        wizard = self.env['mrp.repair.reconcile.wizard'].create(vals)
        wizard.get_reconcile_payments(self)
        return {
            'name': ('Create wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.repair.reconcile.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
            'context': vals,
        }

    @api.one
    @api.depends('fees_lines.product_id', 'fees_lines.product_uom_qty', 'fees_lines.price_unit', 'operations.product_uom_qty')
    def _planned_repair_time(self):
        self.quotation_notes = "HelloWorld"
        time = 0
        if self.task_id:
            for line in self.fees_lines:
                #TODO Only Count time related products, change if clause to be more flexible
                if line.product_uom.category_id.name == "Working Time":
                    time += line.product_uom_qty
            task = self.env['project.task'].search([('id', '=', self.task_id.id)])

            task.write({'planned_hours': time})
            task.planned_hours = time

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
