from odoo import api, fields, models


class Helpdesk(models.Model):
    _inherit = "helpdesk.ticket"

    status_update = fields.Boolean(string="Status Update", default=True,
                                    help="If the Box is deactivated, the customer is removed from the Followers list.")
    is_repair = fields.Boolean('Is a Repair Order?', default=False, compute="_create_task_for_repair_order", store=True)

    repair_count = fields.Integer('Number of repairs for this ticket', compute="_compute_repair_count", store=True)
    repair_orders = fields.One2many(comodel_name="mrp.repair", inverse_name="helpdesk_ticket_id")
    repair_status = fields.Char(compute="_compute_repair_status", string='Repair Status',
                                help="This field will display the status of the lowest state found in attached repair orders.")
    repair_stage = fields.Char(compute="_compute_repair_stage", string='Repair Stage',
                                help="This field will display the status of the lowest stage found in attached repair orders.")

    rma_count = fields.Integer('Number of RMAs for this ticket', compute="_compute_rma_count")
    rma_orders = fields.One2many(comodel_name="rma.order.line", inverse_name="helpdesk_ticket_id")
    rma_status = fields.Char(compute="_compute_rma_status", string='RMA Status', store=True,
                                help="This field will display the status of the lowest state found in attached RMA orders.")

    @api.multi
    @api.onchange('status_update')
    def _remove_customer_from_follower(self):
        if self.status_update == False:
            self.env.cr.execute("""
                delete from mail_followers where partner_id not in (select partner_id from res_users);
                """)
        # TODO: if = true, add customer to follwer list
        #if self.status_update == True:
            #self.write({'message_follower_ids':[(4, self.partner_id.id)]})
            #self.message_follower_ids = [(4, self.partner_id.id)]


### REPAIR
    @api.one
    @api.depends('repair_orders.state')
    def _compute_repair_count(self):
        cond = [('helpdesk_ticket_id', '=', self.id)]
        self.repair_count = len(self.env['mrp.repair'].search(cond))


    # opening repair tree view from ticket
    @api.multi
    def ticket_repair_orders(self):
        # Necessary to open form view from tree view
        tree_view = self.env.ref('mrp_repair.view_repair_order_tree').id
        form_view = self.env.ref('mrp_repair.view_repair_order_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ticket Repair Orders',
            'res_model': 'mrp.repair',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'views': [(tree_view, 'tree'), (form_view, 'form')],
            'context': {'search_default_helpdesk_ticket_id': self.id}
        }
    ### Preparation if repair state should be different to displayed state in helpdesk, Slection for field
    """
    @api.multi
    def get_repair_state(self):
        return [
            ('draft', 'Quotation'),
            ('cancel', 'Cancelled'),
            ('confirmed', 'Confirmed'),
            ('under_repair', 'In Repair'),
            ('ready', 'Ready to Repair'),
            ('2binvoiced', 'To invoice'),
            ('invoice_except', 'Invoice exception'),
            ('done', 'Repaired'),
            ]
            """

    @api.multi
    @api.depends('repair_orders.state')
    def _compute_repair_status(self):
        for ticket in self:
            if ticket.repair_orders:
                repairs_state = set([repair.state for repair in ticket.repair_orders])
                if 'draft' in repairs_state:
                    ticket.repair_status = 'Draft'
                elif 'confirmed' in repairs_state:
                    ticket.repair_status = 'Confirmed'
                elif ('under_repair' or 'ready') in repairs_state:
                    ticket.repair_status = 'Under Repair'
                elif '2binvoiced' in repairs_state:
                    ticket.repair_status = 'To be invoiced'
                elif 'done' in repairs_state:
                    ticket.repair_status = 'Done'
                elif 'cancelled' in repairs_state:
                    ticket.repair_status = 'Cancelled'
                else:
                    ticket.repair_status = 'Status Error'
            else:
                ticket.repair_status = 'None'

    @api.depends('repair_orders.stage_id')
    def _compute_repair_stage(self):
        records = self.env['mrp.repair'].search([('helpdesk_ticket_id', '=', self.id)])
        if records:
            records_sorted = records.sorted(key=lambda r: r.stage_id.sequence)
            stage = records_sorted[0].stage_id.name
            self.repair_stage = stage

    @api.one
    @api.depends('repair_orders')
    def _create_task_for_repair_order(self):
        order_count = self.repair_orders.search_count([('helpdesk_ticket_id', '=', self.id)])
        if order_count == 1 and self.is_repair == False:
            task = self.env['project.task'].create({
                'name': self.display_name,
                'project_id': self.project_id.id,
                'partner_id': self.partner_id.id,
                'helpdesk_ticket_id': self.id,
            })
            self.write({'task_id': task.id, 'is_repair': True})

### RMA

    @api.one
    def _compute_rma_count(self):
        pass
        cond = [('helpdesk_ticket_id', '=', self.id)]
        self.rma_count = len(self.env['rma.order.line'].search(cond))

    # opening RMA tree view from ticket
    @api.multi
    def ticket_rma_orders(self):
        tree_view = self.env.ref('rma.view_rma_line_tree').id
        form_view = self.env.ref('rma.view_rma_line_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ticket RMA Orders',
            'res_model': 'rma.order.line',
            'view_mode': 'tree',
            'views': [(tree_view, 'tree'), (form_view, 'form')],
            'context': {'search_default_helpdesk_ticket_id': self.id}
        }

    @api.multi
    @api.depends('rma_orders.state')
    def _compute_rma_status(self):
        for ticket in self:
            if ticket.rma_orders:
                rmas_state = set([rma.state for rma in ticket.rma_orders])
                if 'draft' in rmas_state:
                    ticket.rma_status = 'Draft'
                elif 'to_approve' in rmas_state:
                    ticket.rma_status = 'To Approve'
                elif 'approved' in rmas_state:
                    ticket.rma_status = 'Approved'
                elif 'done' in rmas_state:
                    ticket.rma_status = 'Done'
                else:
                    ticket.rma_status = 'Status Error'
            else:
                ticket.rma_status = 'None'
