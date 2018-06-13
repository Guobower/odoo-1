# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _


class SaleOrderMarginWizard(models.TransientModel):
    _name = 'sale.order.margin.wizard'
    _description = 'View and manipulate prices and margins per sale order line.'

    order_line_ids = fields.One2many('sale.order.margin.line.wizard', 'order_id')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Partner')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    amount_total = fields.Float(string='Amount Total', compute="compute_total")
    margin_total = fields.Float(string='Margin Total', compute="compute_total")
    margin_percent_total = fields.Float(string='Margin Total (%)', compute="compute_total")

    def create_so_lines(self, s_order):
        for line in s_order.order_line:
            taxes = [(6, 0, line.tax_id.ids)] or False
            so_line = self.env['sale.order.margin.line.wizard'].create({
                'product_uom_qty': line.product_uom_qty,
                'product_id': line.product_id.id,
                'order_id': self.id,
                'section': line.layout_category_id.id,
                'price_unit': line.price_unit,
                'cost_unit': line.purchase_price,
                'discount': line.discount,
                'discount_absolute': line.discount_absolute,
                'taxes_id': taxes,
            })
            self.order_line_ids += so_line

    @api.depends('order_line_ids.margin')
    def compute_total(self):
        for line in self.order_line_ids:
            self.amount_total += line.price_discounted * line.product_uom_qty
            self.margin_total += line.margin * line.product_uom_qty
        self.margin_percent_total = self.margin_total / self.amount_total * 100

    #TODO: create function for manipulating prices and write them to SO
    def manipulate_prices(self):
        return True

class SaleOrderMarginLineWizard(models.TransientModel):
    _name = 'sale.order.margin.line.wizard'
    _description = 'Margins for Sale Order Lines'

    product_id = fields.Many2one('product.product', string='Product')
    section = fields.Many2one('sale.layout_category', string='Section')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    cost_unit = fields.Float(string='Unit Cost')
    discount = fields.Float(string='Discount (%)')
    discount_absolute = fields.Float(string='Discount (€)')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    order_id = fields.Many2one('sale.order.margin.wizard', string='Order Reference', index=True, required=True, ondelete='cascade')
    amount_tax = fields.Float(string='Tax Amount')

    margin = fields.Float(string='Margin', compute="compute_margin")
    margin_percent = fields.Float(string='Margin (%)', compute="compute_margin")
    price_discounted = fields.Float(string='Discounted Price', compute="compute_margin")

    @api.one
    @api.depends('price_unit', 'cost_unit', 'discount', 'discount_absolute')
    def compute_margin(self):
        #TODO: FIX Tax computation
        selling_price = self.price_unit
        if self.discount:
            selling_price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        if self.discount_absolute:
            selling_price = self.price_unit - self.discount_absolute
        taxes = self.taxes_id.compute_all(selling_price, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.sale_order_id.partner_shipping_id)
        self.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []) if t.price_include == True)
        if not self.order_id.sale_order_id.fiscal_position_id:
            self.margin = selling_price  - self.cost_unit - self.amount_tax
            self.margin_percent = self.margin / selling_price * 100
        else:
            self.margin = selling_price - self.cost_unit
            self.margin_percent = self.margin / selling_price * 100
        self.price_discounted = selling_price
