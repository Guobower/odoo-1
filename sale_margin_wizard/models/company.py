
from odoo import models, fields, api

class Company(models.Model):
    _inherit = 'res.company'

    fiscal_pos_gross = fields.Many2one('account.fiscal.position', string='Fiscal Position (gross)')
    fiscal_pos_net = fields.Many2one('account.fiscal.position', string='Fiscal Position (net)')
