# -*- coding: utf-8 -*-
from odoo import http

# class BeckhoffPoCustomer(http.Controller):
#     @http.route('/beckhoff_po_customer/beckhoff_po_customer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beckhoff_po_customer/beckhoff_po_customer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beckhoff_po_customer.listing', {
#             'root': '/beckhoff_po_customer/beckhoff_po_customer',
#             'objects': http.request.env['beckhoff_po_customer.beckhoff_po_customer'].search([]),
#         })

#     @http.route('/beckhoff_po_customer/beckhoff_po_customer/objects/<model("beckhoff_po_customer.beckhoff_po_customer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beckhoff_po_customer.object', {
#             'object': obj
#         })