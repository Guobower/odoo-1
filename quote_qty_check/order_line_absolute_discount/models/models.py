# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class SaleOrderLineAbsoluteDiscount(models.Model):
    _inherit = 'sale.order.line'

    discount_absolute = fields.Float(string="Discount (Euro)", default=0.0, help="Only one discount mode can be active for a sale order line.")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_absolute')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            """ Addition to odoo core"""
            if line.discount_absolute > 0:
                if line.discount_absolute > line.price_unit:
                    raise ValidationError("Discount cannot be greater than Unit price.")
                else:
                    price = line.price_unit - line.discount_absolute
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            """ End Addition """
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
})


    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'discount_absolute': self.discount_absolute,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res

class AccountInvoiceLineAbsoluteDiscount(models.Model):
    _inherit = 'account.invoice.line'

    discount_absolute = fields.Float(string="Discount (Euro)", default=0.0, help="Only one discount mode can be active for an invoice line.")

    @api.one
    @api.depends('price_unit', 'discount', 'discount_absolute', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        """ Addition to odoo core """
        if self.discount_absolute > 0:
            if self.discount_absolute > self.price_unit:
                raise ValidationError("Absolute Discount cannot be greater than Unit Price.")
            else:
                price = self.price_unit - self.discount_absolute
        else:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        """ End Addition"""
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
