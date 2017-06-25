# -*- coding: utf-8 -*-
from odoo import http

# class BeckhoffViewExtensions(http.Controller):
#     @http.route('/beckhoff_view_extensions/beckhoff_view_extensions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beckhoff_view_extensions/beckhoff_view_extensions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beckhoff_view_extensions.listing', {
#             'root': '/beckhoff_view_extensions/beckhoff_view_extensions',
#             'objects': http.request.env['beckhoff_view_extensions.beckhoff_view_extensions'].search([]),
#         })

#     @http.route('/beckhoff_view_extensions/beckhoff_view_extensions/objects/<model("beckhoff_view_extensions.beckhoff_view_extensions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beckhoff_view_extensions.object', {
#             'object': obj
#         })