from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_repair_advance = fields.Boolean(string='Repair Advance Payment', default=False)
