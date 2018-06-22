# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

class ProductTemplateMarginWizard(models.TransientModel):
    _name = 'product.template.margin.wizard'
    _description = 'Displays the margins for the product.'

    def discount_mode_selection(self):
        return [
            ('price', 'Price'),
            ('relative', 'Relative (%)'),
            ('absolute', 'Absolute (Euro)'),
            ]

    margin_line_ids = fields.One2many('product.template.margin.line.wizard', 'wizard_id')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company',required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    margin_target = fields.Float(string='Target Margin', help="Computes the price for each line to have the entered margin.")
    price_target = fields.Float(string='Target Price', help='Discounts all lines in relation to their price.')
    discount_target = fields.Float(string='Target Discount', help='Set a target discounts which will be applied to the lines according to discount mode')
    discount_mode = fields.Selection(string='Discount Mode', selection='discount_mode_selection')

    price_regular = fields.Float(string='Regular Price')
    price_special = fields.Float(string='Special Price')
    price_regular_net = fields.Float(string='Regular Net Price')
    cost_unit = fields.Float(string='Cost')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_discounted = fields.Float(string='Amount Total', compute="compute_total", digits=dp.get_precision('Product Price'))
    margin_total = fields.Float(string='Margin Total', compute="compute_total", digits=dp.get_precision('Product Price'))
    margin_percent_total = fields.Float(string='Margin Total (%)', compute="compute_total", digits=dp.get_precision('Discount'))
    discount_total = fields.Float(string='Discount Total', compute='compute_total', digits=dp.get_precision('Product Price'))
    discount_percent_total = fields.Float(string='Discount Total (%)', compute='compute_total', digits=dp.get_precision('Discount'))

    # View Option fields
    show_unit_cost = fields.Boolean(string="Show Unit Cost", default=False)
    show_absolute_margin = fields.Boolean(string="Show Absolute Margin", default=True)
    show_amount_tax = fields.Boolean(string="Show Amount Tax", default=False)

    number_margin_lines = fields.Float(string="# Margin Lines", default=6, help="Number of margin lines computed aside from the selling price.")


    def compute_factors(self):
        return True

    @api.onchange('number_margin_lines')
    def create_margin_lines(self, product):
        price_dif = (self.price_regular - self.cost_unit) / self.number_margin_lines
        finished = False
        special = False
        counter = 0
        while not finished:
            price_unit = self.cost_unit + price_dif * counter
            if price_unit > self.price_special and special == False and self.price_special != 0:
                discount = 100 - self.price_special / self.price_regular * 100
                discount_absolute = self.price_regular - self.price_special
                margin_line = self.env['product.template.margin.line.wizard'].create({
                    'wizard_id': self.id,
                    'price_unit': self.price_special,
                    'cost_unit': self.cost_unit,
                    'discount': discount,
                    'discount_absolute': discount_absolute,
                })
                self.margin_line_ids += margin_line
                special = True
            discount = 100 - price_unit / self.price_regular * 100
            discount_absolute = self.price_regular - price_unit
            margin_line = self.env['product.template.margin.line.wizard'].create({
                'wizard_id': self.id,
                'price_unit': price_unit,
                'cost_unit': self.cost_unit,
                'discount': discount,
                'discount_absolute': discount_absolute,
            })
            self.margin_line_ids += margin_line
            counter += 1
            if counter > self.number_margin_lines:
                finished = True


    def compute_total(self):
        return True

    @api.onchange('price_target')
    def compute_target_fields(self):
        for line in self.margin_line_ids:
            if line.price_unit > self.price_target:
                line.price_unit = self.price_target
                line.discount = 100 - self.price_target / self.price_regular * 100
                line.discount_absolute = self.price_regular - self.price_target
                break

    @api.onchange('discount_target')
    def compute_target_fields(self):
        for line in self.margin_line_ids:
            if line.discount > self.discount_target:
                line.price_unit = self.price_target - self.price_target * self.discount_target * 100
                line.discount = self.discount_target
                line.discount_absolute = self.price_regular - line.price_unit
                break


class ProductTemplateMarginLineWizard(models.TransientModel):
    _name = 'product.template.margin.line.wizard'
    _description = 'Product Margins'

    wizard_id = fields.Many2one('product.template.margin.wizard', string='Product Template', index=True, required=True, ondelete='cascade')
    #product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    cost_unit = fields.Float(string='Unit Cost', digits=dp.get_precision('Product Price'))
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'))
    discount_absolute = fields.Float(string='Discount (€)')
    currency_id = fields.Many2one('res.currency', related="wizard_id.currency_id", string="Currency")
    amount_tax = fields.Float(string='Tax Amount')

    margin = fields.Float(string='Margin', compute="compute_margin", digits=dp.get_precision('Product Price'))
    margin_percent = fields.Float(string='Margin (%)', compute="compute_margin", digits=dp.get_precision('Discount'))


    @api.one
    @api.depends('price_unit', 'cost_unit', 'discount', 'discount_absolute')
    def compute_margin(self):
        self.margin = self.price_unit - self.cost_unit
        if self.price_unit:
            self.margin_percent = self.margin / self.price_unit * 100
        self.discount = 100 - self.price_unit / self.wizard_id.price_regular * 100
