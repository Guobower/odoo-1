# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class AdvancePayReconcileWizard(models.TransientModel):
    _name = 'mrp.repair.reconcile.wizard'
    _description = 'Allows to reconcile advance payments from Point of Sale with Repair Order'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    pos_order_line_ids = fields.One2many('mrp.repair.reconcile.line.wizard', 'order_line_id')
    repair_order_id = fields.Many2one('mrp.repair', string="Repair Order", required=True)


    def get_reconcile_payments(self, repair_order):
        pos_order_ids = self.env['pos.order'].search([('partner_id', '=', self.partner_id.id)])
        for order in pos_order_ids:
            for line in order.lines:
                if line.is_repair_advance == True and not line.repair_order_id:
                    wizard_line = self.env['mrp.repair.reconcile.line.wizard'].create({
                        'name': line.order_id.name,
                        'date_order': line.create_date,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty,
                        'price': line.price_unit,
                        'order_line_id': self.id,
                        'discount': line.discount,
                        'price_subtotal_incl': line.price_subtotal_incl,
                        'taxes_id': [(6, 0, line.tax_ids.ids)],
                        'pos_order_line_id': line.id,
                    })
                    self.pos_order_line_ids += wizard_line

    @api.onchange('partner_id')
    def update_reconcile_payments(self):
        self.pos_order_line_ids = [(5,0,0)]
        pos_order_ids = self.env['pos.order'].search([('partner_id', '=', self.partner_id.id)])
        for order in pos_order_ids:
            for line in order.lines:
                if line.is_repair_advance == True and not line.repair_order_id:
                    wizard_line = self.env['mrp.repair.reconcile.line.wizard'].create({
                        'name': line.order_id.name,
                        'date_order': line.create_date,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty,
                        'price': line.price_unit,
                        'order_line_id': self.id,
                        'discount': line.discount,
                        'price_subtotal_incl': line.price_subtotal_incl,
                        'taxes_id': [(6, 0, line.tax_ids.ids)],
                        'pos_order_line_id': line.id,
                    })
                    self.pos_order_line_ids += wizard_line

    def reconcile_payments(self):
        warning = self.check_lines()
        if warning:
            raise ValidationError(warning)
        #TODO compute margin for this line
        fee_env = self.env['mrp.repair.fee']
        for line in self.pos_order_line_ids:
            if line.line_to_reconcile == True:
                inverted_price = line.price * -1
                fee_line = fee_env.create({
                    'name': line.product_id.name,
                    'price_unit': inverted_price,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'repair_id': self.repair_order_id.id,
                    'tax_id': [(6, 0, line.taxes_id.ids)],
                    'product_id': line.product_id.id,
                })
                # Mark PoS order line as reconciled
                pos_order_line = self.env['pos.order.line'].search([('id', '=', line.pos_order_line_id.id)])
                pos_order_line.write({'repair_order_id': self.repair_order_id.id})

    def check_lines(self):
        message = ''
        line_with_box_checked = False
        for line in self.pos_order_line_ids:
            if line.line_to_reconcile == False:
                message = message + 'No box checked in Advance Payment lines. Please select a line to reconcile.'
            if line.line_to_reconcile == True:
                line_with_box_checked = True
        if line_with_box_checked == False:
            message = 'No Line selected \n' + message
        return message


class AdvancePayReconcileLineWizard(models.TransientModel):
    _name = 'mrp.repair.reconcile.line.wizard'
    _description = 'PoS Lines to reconcile'

    order_line_id = fields.Many2one('mrp.reconcile.wizard', string='Order Line', index=True)
    pos_order_line_id = fields.Many2one('pos.order.line', string="PoS Order Line")
    name = fields.Char('Order Reference', required=True, readonly=True)
    date_order = fields.Datetime('Order Date', index=True, readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', readonly=True)
    price = fields.Float(string='Price', readonly=True)
    discount = fields.Float(string='Discount', readonly=True)
    price_subtotal_incl = fields.Float(string='Price Total', readonly=True)
    line_to_reconcile = fields.Boolean(string='Reconcile', default=False, help='Check this Box to reconcile this line')
    taxes_id = fields.Many2many('account.tax', string="Taxes", domain=['|', ('active', '=', False), ('active', '=', True)])
