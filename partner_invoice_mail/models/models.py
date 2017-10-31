# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PartnerInvoiceMail(models.Model):
     _inherit = 'res.partner'

     partner_invoice_mail = fields.Boolean(string="Invoices via Mail", help="If this box is checked, a notification will display on the invoice reminding the user to send the invoice via Mail.")

class PartnerAccountInvoiceMail(models.Model):
    _inherit = 'account.invoice'

    account_invoice_mail = fields.Boolean(string='Receive E-Mail Invoices', related="partner_id.partner_invoice_mail", help="This customer wants to receive Invoices via Mail.")
