# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrderMarginWizard(models.TransientModel):
    _name = 'sale.order.margin.wizard'
    _description = 'View and manipulate prices and margins per sale order line.'

    def discount_mode_selection(self):
        return [
            ('price', 'Price'),
            ('relative', 'Relative (%)'),
            ('absolute', 'Absolute (Euro)'),
            ]

    order_line_ids = fields.One2many('sale.order.margin.line.wizard', 'order_id')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Partner')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    margin_target = fields.Float(string='Target Margin', help="Computes the price for each line to have the entered margin.")
    price_target = fields.Float(string='Target Price', help='Discounts all lines in relation to their price.')
    discount_target = fields.Float(string='Target Discount', help='Set a target discounts which will be applied to the lines according to discount mode')
    discount_mode = fields.Selection(string='Discount Mode', selection='discount_mode_selection')

    amount_total = fields.Float(string='Amount Total', compute="compute_total", digits=dp.get_precision('Product Price'))
    margin_total = fields.Float(string='Margin Total', compute="compute_total", digits=dp.get_precision('Product Price'))
    margin_percent_total = fields.Float(string='Margin Total (%)', compute="compute_total", digits=dp.get_precision('Discount'))
    discount_total = fields.Float(string='Discount Total', compute='compute_total', digits=dp.get_precision('Product Price'))
    discount_percent_total = fields.Float(string='Discount Total (%)', compute='compute_total', digits=dp.get_precision('Discount'))

    # View Option fields
    show_sections = fields.Boolean(string="Show Sections", default=False)
    show_quantity = fields.Boolean(string="Show Unit Quantities", default=False)
    show_unit_cost = fields.Boolean(string="Show Unit Cost", default=True)
    show_absolute_margin = fields.Boolean(string="Show Absolute Margin", default=True)
    show_amount_tax = fields.Boolean(string="Show Amount Tax", default=False)
    show_total_discounts = fields.Boolean(string="Show Total Discounts", default=False)



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
                'sale_order_line_id': line.id,
            })
            self.order_line_ids += so_line


    def reset_so_lines(self):
        for line in self.order_line_ids:
            line.price_unit = line.sale_order_line_id.price_unit
            line.cost_unit = line.sale_order_line_id.purchase_price
            line.discount = line.sale_order_line_id.discount
            line.discount_absolute = line.sale_order_line_id.discount_absolute
        return {"type": "ir.actions.do_nothing"}


    def restore_so_lines_prices(self):
        for line in self.order_line_ids:
            line.write({
                'discount': 0,
                'discount_absolute': 0,
                'price_unit': line.product_id.lst_price,
                'cost_unit':line.product_id.standard_price,
            })
        return {"type": "ir.actions.do_nothing"}


    @api.depends('order_line_ids.discount', 'order_line_ids.discount_absolute', 'order_line_ids.price_unit', 'order_line_ids.cost_unit')
    def compute_total(self):
        for line in self.order_line_ids:
            self.amount_total += line.price_discounted * line.product_uom_qty
            self.margin_total += line.margin * line.product_uom_qty
            self.discount_total += (line.product_id.lst_price - line.price_discounted) * line.product_uom_qty
        self.margin_percent_total = self.margin_total / self.amount_total * 100
        self.discount_percent_total = self.discount_total / self.amount_total * 100


    def manipulate_prices(self):
        for line in self.order_line_ids:
            line.sale_order_line_id.discount =  line.discount
            line.sale_order_line_id.discount_absolute = line.discount_absolute
            line.sale_order_line_id.price_unit = line.price_unit
            line.sale_order_line_id.purchase_price = line.cost_unit


    # TODO: should work with gross/net unit prices
    @api.onchange('discount_mode')
    def compute_target_margin(self):
        if self.margin_target < 0 or self.margin_target > 100:
            raise ValidationError("Margin must be between 0 and 100")
        if self.margin_target > 0:
            self.reset_so_lines()
            for line in self.order_line_ids:
                line.discount = 0
                line.discount_absolute = 0
                selling_price = line.cost_unit / ((100 - self.margin_target) / 100)
                if self.discount_mode == 'relative':
                    line.discount = (line.price_unit - selling_price) / line.price_unit * 100
                if self.discount_mode == 'absolute':
                    line.discount_absolute = line.price_unit - selling_price
                if self.discount_mode == 'price':
                    line.price_unit = selling_price

    @api.onchange('discount_mode')
    def compute_target_price(self):
        if self.price_target > 0:
            self.reset_so_lines()
            for line in self.order_line_ids:
                line.discount = 0
                line.discount_absolute = 0
            price_target_rel = (1 - self.price_target / self.amount_total)
            for line in self.order_line_ids:
                if self.discount_mode == 'relative':
                    line.discount = price_target_rel * 100
                if self.discount_mode == 'absolute':
                    line.discount_absolute = line.price_unit * price_target_rel
                if self.discount_mode == 'price':
                    line.price_unit = line.price_unit - line.price_unit * price_target_rel


    @api.onchange('discount_mode')
    def compute_target_discount(self):
        if self.discount_target > 0:
            if self.discount_mode == 'relative':
                if self.discount_target < 0 or self.discount_target > 100:
                    raise ValidationError("If you want to set a relative discount, the discount amount must be between 0 and 100.")
                for line in self.order_line_ids:
                    line.discount = self.discount_target
            if self.discount_mode == 'absolute':
                for line in self.order_line_ids:
                    line.discount_absolute = self.discount_target
            if self.discount_mode == 'price':
                raise ValidationError("This Discount/Discount Mode configuration is not supported. Please use an absolute or relative discount.")


    @api.onchange('discount_mode')
    def compute_discount_mode(self):
        # re-compute the discount into another discount model
        if self.margin_target == 0 and self.price_target == 0:
            for line in self.order_line_ids:
                if self.discount_mode == 'relative' and line.discount == 0:
                    line.discount = line.discount_absolute / line.price_unit * 100
                    line.discount_absolute = 0
                if self.discount_mode == 'absolute' and line.discount_absolute == 0:
                    line.discount_absolute = line.discount * line.price_unit / 100
                    line.discount = 0
                if self.discount_mode == 'price':
                    line.price_unit = line.price_discounted
                    line.discount = 0
                    line.discount_absolute = 0


    @api.onchange('discount_mode')
    def reset_target_fields(self):
        if not self.discount_mode:
            self.margin_target = 0
            self.price_target = 0


class SaleOrderMarginLineWizard(models.TransientModel):
    _name = 'sale.order.margin.line.wizard'
    _description = 'Margins for Sale Order Lines'

    product_id = fields.Many2one('product.product', string='Product')
    section = fields.Many2one('sale.layout_category', string='Section')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    cost_unit = fields.Float(string='Unit Cost', digits=dp.get_precision('Product Price'))
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'))
    discount_absolute = fields.Float(string='Discount (€)')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    order_id = fields.Many2one('sale.order.margin.wizard', string='Order Reference', index=True, required=True, ondelete='cascade')
    amount_tax = fields.Float(string='Tax Amount')
    sale_order_line_id = fields.Many2one('sale.order.line', string="Sale Order Line ID")

    margin = fields.Float(string='Margin', compute="compute_margin", digits=dp.get_precision('Product Price'))
    margin_percent = fields.Float(string='Margin (%)', compute="compute_margin", digits=dp.get_precision('Discount'))
    price_discounted = fields.Float(string='Discounted Price', compute="compute_margin", digits=dp.get_precision('Product Price'))

    @api.one
    @api.depends('price_unit', 'cost_unit', 'discount', 'discount_absolute')
    def compute_margin(self):
        #TODO: FIX Tax computation
        if self.discount_absolute:
            selling_price = self.price_unit - self.discount_absolute
        else:
            selling_price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.taxes_id.compute_all(selling_price, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.sale_order_id.partner_shipping_id)
        self.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []) if t.price_include == True)
        # If no fiscal position, the unit price is in gross and the amount_tax needs to be considered for margin computation
        if not self.order_id.sale_order_id.fiscal_position_id:
            self.margin = selling_price  - self.cost_unit - self.amount_tax
            if selling_price:
                self.margin_percent = self.margin / selling_price * 100
        else:
            self.margin = selling_price - self.cost_unit
            if selling_price:
                self.margin_percent = self.margin / selling_price * 100
        self.price_discounted = selling_price


    def create_product_margin_wizard(self):
        view = self.env.ref('sale_margin_wizard.product_template_margin_wizard_form')
        taxes = [(6, 0, self.taxes_id.ids)] or False
        vals = {
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'price_regular': self.product_id.product_tmpl_id.lst_price,
            'price_special': self.product_id.product_tmpl_id.special_offer,
            'cost_unit': self.product_id.product_tmpl_id.standard_price,
            #'taxes_id': taxes,
        }
        wizard = self.env['product.template.margin.wizard'].create(vals)
        wizard.create_margin_lines(self)
        return {
            'name': ('Product Margin Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template.margin.wizard',
            'src_model': 'sale.order.margin.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
            'context': vals,
        }