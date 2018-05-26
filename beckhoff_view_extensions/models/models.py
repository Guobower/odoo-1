# -*- coding: utf-8 -*-

from odoo import models, fields, api

class beckhoff_view_extensions(models.Model):
    _inherit = 'product.product'

    list_price = fields.Float(track_visibility='OnChange')
    name = fields.Char(track_visibility='OnChange')
    barcode = fields.Char(track_visibility='OnChange')
    active = fields.Boolean(track_visibility='OnChange')

class ProductTemplateChangeTrack(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(track_visibility='OnChange')
    name = fields.Char(track_visibility='OnChange')
    barcode = fields.Char(track_visibility='OnChange')
    active = fields.Boolean(track_visibility='OnChange')

    description_sale = fields.Text(copy=False)
    description_purchase = fields.Text(copy=False)
    description_picking = fields.Text(copy=False)
    description_pickingin = fields.Text(copy=False)
    description_pickingout = fields.Text(copy=False)

class PartnerChangeData(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(track_visibility='OnChange')
    email = fields.Char(track_visibility='OnChange')
    city = fields.Char(track_visibility='OnChange')
    street = fields.Char(track_visibility='OnChange')
    active = fields.Boolean(track_visibility='OnChange')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'
    invoice_line_brand = fields.Many2one(string="Brand", related="product_id.product_brand_id", readonly=True)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    order_line_brand = fields.Many2one(string="Brand", related="product_id.product_brand_id", readonly=True)

class MoveLine(models.Model):
    _inherit = 'stock.move.line'

    partner_id = fields.Many2one(related="move_id.picking_partner_id", string="Partner")
