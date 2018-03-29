from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.task"

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', 'Helpdesk Ticket')
