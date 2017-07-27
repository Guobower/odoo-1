# -*- coding: utf-8 -*-
from odoo import http

# class PartnerInvoiceMail(http.Controller):
#     @http.route('/partner_invoice_mail/partner_invoice_mail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_invoice_mail/partner_invoice_mail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_invoice_mail.listing', {
#             'root': '/partner_invoice_mail/partner_invoice_mail',
#             'objects': http.request.env['partner_invoice_mail.partner_invoice_mail'].search([]),
#         })

#     @http.route('/partner_invoice_mail/partner_invoice_mail/objects/<model("partner_invoice_mail.partner_invoice_mail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_invoice_mail.object', {
#             'object': obj
#         })