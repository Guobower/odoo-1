from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class PurchaseOrderLineDiscounts(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string="Discount (%)", default=0.0)
    discount_absolute = fields.Float(string="Discount (Euro)", default=0.0, help="Only one discount mode can be active for a purchase order line.")

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'discount_absolute')
    def _compute_amount(self):
        for line in self:
            # Compute price to be passed to taxes depending on discount mode
            if line.discount_absolute > 0:
                if line.price_unit < line.absolute_discount:
                    raise ValidationError("Discount cannot be greater than Unit price.")
                price = line.price_unit - line.discount_absolute
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # end price computation
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
})

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        # Adding discount fields to be passed to invoice
        vals = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        vals['discount'] = line.discount
        vals['discount_absolute'] = line.discount_absolute
        return vals
