from odoo import api, fields, models

class Helpdesk(models.Model):
    _inherit = "helpdesk.ticket"

    repair_count = fields.Integer('Number of repairs for this ticket', compute="_compute_repair_count")

    def _compute_repair_count(self):
        cond = [('helpdesk_ticket_id', '=', self.id)]
        self.repair_count = len(self.env['mrp.repair'].search(cond))

    # opening repair tree view from ticket
    @api.multi
    def ticket_repair_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ticket Repair Orders',
            'res_model': 'mrp.repair',
            'view_mode': 'tree',
            'context': {'search_default_helpdesk_ticket_id': self.id}
        }
