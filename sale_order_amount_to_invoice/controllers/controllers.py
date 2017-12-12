# -*- coding: utf-8 -*-
from odoo import http

# class SaleOrderAmountToInvoice(http.Controller):
#     @http.route('/sale_order_amount_to_invoice/sale_order_amount_to_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_amount_to_invoice/sale_order_amount_to_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_amount_to_invoice.listing', {
#             'root': '/sale_order_amount_to_invoice/sale_order_amount_to_invoice',
#             'objects': http.request.env['sale_order_amount_to_invoice.sale_order_amount_to_invoice'].search([]),
#         })

#     @http.route('/sale_order_amount_to_invoice/sale_order_amount_to_invoice/objects/<model("sale_order_amount_to_invoice.sale_order_amount_to_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_amount_to_invoice.object', {
#             'object': obj
#         })