from odoo import api, fields, models

class RmaOrderLine(models.Model):
    _inherit = "rma.order.line"
    
    helpdesk_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Helpdesk Ticket")
