# -*- coding: utf-8 -*-
from odoo import http

# class BeckhoffFleetExtensions(http.Controller):
#     @http.route('/beckhoff_fleet_extensions/beckhoff_fleet_extensions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beckhoff_fleet_extensions/beckhoff_fleet_extensions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beckhoff_fleet_extensions.listing', {
#             'root': '/beckhoff_fleet_extensions/beckhoff_fleet_extensions',
#             'objects': http.request.env['beckhoff_fleet_extensions.beckhoff_fleet_extensions'].search([]),
#         })

#     @http.route('/beckhoff_fleet_extensions/beckhoff_fleet_extensions/objects/<model("beckhoff_fleet_extensions.beckhoff_fleet_extensions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beckhoff_fleet_extensions.object', {
#             'object': obj
#         })