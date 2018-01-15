# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Quote_qty_check(models.Model):
    _inherit = 'sale.order.line'

    is_available = fields.Boolean()

    def _overwrite_qty_check(self):
        record = super(Sale_Order_Line,self)._onchange_product_id_check_availability()

        record['warning_mess'] = {
                                'title': _('Test!'),
                                'message' : _('You plan to sell %s %s but you only have %s %s available!\nThe stock on hand is %s %s.') % \
                                    (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
        }
        return record

    #http://github.com/odoo/odoo/blob/10.0/addons/sale_stock/models/sale_order.py

"""
    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    warning_mess = {
                        'title': _('Test'),
                        'message' : _('You plan to sell %s %s but you only have %s %s available!\nThe stock on hand is %s %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                    }
                    return {'warning': warning_mess}
return {}
"""
