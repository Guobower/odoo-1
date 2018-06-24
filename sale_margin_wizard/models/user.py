# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api

class ResUser(models.Model):
    _inherit = 'res.users'

    margin_lines = fields.Float(string="Margin Lines", default=6, help="Number of margin lines displayed in product margin wizard")
    price_mode = fields.Selection([('net', 'Net'),('gross', 'Gross')], string="Price mode", default='gross', help="Default price mode for margin wizards")
