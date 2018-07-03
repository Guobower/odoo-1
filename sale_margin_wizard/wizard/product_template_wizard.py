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
    tax_mode = fields.Selection([('net', 'Net'),('gross', 'Gross')], string="Tax mode", default='gross')
    price_regular = fields.Float(string='Regular Price')
    price_special = fields.Float(string='Special Price')
    price_regular_net = fields.Float(string='Regular Net Price')
    has_special_price = fields.Boolean(string='Has Special Price')
    cost_unit = fields.Float(string='Cost')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    tax_factor = fields.Float(string='Tax Factor')
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
    created_from_so = fields.Boolean(string='Wizard created from SO?', default=False)

    def compute_factors(self):
        return True

    @api.onchange('number_margin_lines')
    def create_margin_lines(self, product):
        # compute the cost price plus tax
        amount_tax = 0
        for tax in self.taxes_id:
            amount_tax += tax.amount * self.cost_unit / 100
        gross_base_price = self.cost_unit + amount_tax
        # compute the price difference between two one2many margin lines
        price_dif = (self.price_regular - gross_base_price) / self.number_margin_lines
        finished = False
        special = False
        counter = 0
        while not finished:
            price_unit = gross_base_price + price_dif * counter
            amount_tax = 0
            for tax in self.taxes_id:
                amount_tax += tax.amount * price_unit / 100
            # Insert a margin line for the special price if one is given
            if price_unit > self.price_special and special == False and self.price_special != 0:
                discount = 100 - self.price_special / self.price_regular * 100
                discount_absolute = self.price_regular - self.price_special
                margin_line = self.env['product.template.margin.line.wizard'].create({
                    'wizard_id': self.id,
                    'price_unit': self.price_special,
                    'cost_unit': self.cost_unit,
                    'discount': discount,
                    'discount_absolute': discount_absolute,
                    'amount_tax': amount_tax,
                    'tax_mode_line': True,
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
                'amount_tax': amount_tax,
                'tax_mode_line': True,
            })
            self.margin_line_ids += margin_line
            counter += 1
            if counter > self.number_margin_lines:
                finished = True


    def compute_total(self):
        return True

    @api.onchange('price_target')
    def compute_price_target(self):
        if self.price_target == 0:
            for line in self.margin_line_ids:
                if line.is_target_line == True:
                    line.is_target_line = False
        else:
            for line in self.margin_line_ids:
                if line.price_unit > self.price_target:
                    line.price_unit = self.price_target
                    line.is_target_line = True
                    break

    @api.onchange('discount_target')
    def compute_discount_target(self):
        if self.discount_target == 0:
            for line in self.margin_line_ids:
                if line.is_target_line == True:
                    line.is_target_line = False
        else:
            target_price = self.price_regular - self.price_regular * self.discount_target / 100
            for line in self.margin_line_ids:
                if line.price_unit > target_price:
                    line.price_unit = target_price
                    line.is_target_line = True
                    break

    @api.onchange('margin_target')
    def compute_margin_target(self):
        if self.margin_target == 0:
            for line in self.margin_line_ids:
                if line.is_target_line == True:
                    line.is_target_line = False
        else:
            target_price = self.cost_unit / ((100 - self.margin_target) / 100)
            if self.tax_mode == 'gross':
                target_price = target_price * ((100 + self.tax_factor) / 100)

            for line in self.margin_line_ids:
                if line.price_unit > target_price:
                    line.price_unit = target_price
                    line.is_target_line = True
                    break

    @api.onchange('cost_unit')
    def set_cost_price(self):
        for line in self.margin_line_ids:
            line.cost_unit = self.cost_unit


    @api.onchange('tax_mode')
    def compute_tax_mode(self):
        for line in self.margin_line_ids:
            if self.tax_mode == 'gross':
                line.price_unit = line.price_unit * ((100 + self.tax_factor) / 100)
                line.tax_mode_line = True
            if self.tax_mode == 'net':
                line.price_unit = line.price_unit / ((100 + self.tax_factor) / 100)
                line.tax_mode_line = False

    def manipulate_prices(self):
        for line in self.order_line_ids:
            line.sale_order_line_id.discount =  line.discount
            line.sale_order_line_id.discount_absolute = line.discount_absolute
            line.sale_order_line_id.price_unit = line.price_unit
            line.sale_order_line_id.purchase_price = line.cost_unit
            

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

    margin = fields.Float(string='Margin (€)', compute="compute_margin", digits=dp.get_precision('Product Price'))
    margin_percent = fields.Float(string='Margin (%)', compute="compute_margin", digits=dp.get_precision('Discount'))
    is_target_line = fields.Boolean(string="Target Line", default=False)
    tax_mode_line = fields.Boolean(string="Net/Gross", default=True)


    @api.one
    @api.depends('price_unit', 'cost_unit', 'discount', 'discount_absolute')
    def compute_margin(self):
        if self.wizard_id.tax_mode == 'gross':
            net_price = self.price_unit / ((100 + self.wizard_id.tax_factor) / 100)
            self.amount_tax  = self.price_unit - net_price
            self.margin = self.price_unit - self.amount_tax - self.cost_unit
            if self.price_unit:
                self.margin_percent = self.margin / (self.price_unit - self.amount_tax) * 100
            if self.wizard_id.price_regular:
                self.discount = 100 - self.price_unit / self.wizard_id.price_regular * 100
            self.discount_absolute = self.wizard_id.price_regular - self.price_unit

        if self.wizard_id.tax_mode == 'net':
            self.amount_tax = self.price_unit * (self.wizard_id.tax_factor / 100)
            self.margin = self.price_unit - self.cost_unit
            if self.price_unit:
                self.margin_percent = self.margin / self.price_unit * 100
            if self.wizard_id.price_regular_net:
                self.discount = 100 - self.price_unit / self.wizard_id.price_regular_net * 100
            self.discount_absolute = self.wizard_id.price_regular_net - self.price_unit
