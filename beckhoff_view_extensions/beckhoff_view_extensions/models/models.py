# -*- coding: utf-8 -*-

from odoo import models, fields, api

class beckhoff_view_extensions(models.Model):
    _inherit = 'product.product'
    _inherit = 'purchase.order'

    list_price = fields.Float(track_visibility='OnChange')
    name = fields.Char(track_visibility='OnChange')
    barcode = fields.Char(track_visibility='OnChange')

class ProductTemplateChangeTrack(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(track_visibility='OnChange')
    name = fields.Char(track_visibility='OnChange')
    barcode = fields.Char(track_visibility='OnChange')

class PartnerChangeData(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(track_visibility='OnChange')
    email = fields.Char(track_visibility='OnChange')
    city = fields.Char(track_visibility='OnChange')
    street = fields.Char(track_visibility='OnChange')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'
    invoice_line_brand = fields.Many2one(string="Brand", related="product_id.product_brand_id", readonly=True)


#    Include OnChange Events for product: price, category, name etc.
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
