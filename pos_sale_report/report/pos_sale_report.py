# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, tools, api

class PurchaseOrderLineTaxStore(models.Model):
    _inherit = 'pos.order.line'

    price_subtotal_incl = fields.Float(store=True)

class PosSaleReport(models.Model):
    _name = 'pos.sale.report'
    _description = 'POS orders and Sale orders aggregated report'
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    date = fields.Date(string='Order Date', readonly=True)
    name = fields.Char('Order Reference', readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product Variant', readonly=True)
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)
    origin = fields.Char(string='Origin', readonly=True)
    qty = fields.Float(string='Quantity', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    price_total = fields.Float('Taxed Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    profit_center = fields.Selection([
        ('30', 'Kleingeräte'),
        ('31', 'Licht'),
        ('32', 'Großgeräte'),
        ('34', 'Wohnaccessoires'),
        ('40', 'Unterhaltungselektronik'),
        ('45', 'Werkstatt'),
        ('50', 'Telekom'),
        ('93', 'Gesamt')
        ], string='Profit Center', readonly=True)

    # WARNING : this code doesn't handle uom conversion for the moment
    def _sale_order_select(self):
        select = """SELECT min(sol.id)*-1 AS id,
            so.date_order::date AS date,
            so.name as name,
            sol.product_id AS product_id,
            pp.product_tmpl_id AS product_tmpl_id,
            so.company_id AS company_id,
            so.partner_id AS partner_id,
            so.user_id AS user_id,
            pt.categ_id AS categ_id,
            sum(sol.price_total) AS price_total,
            sum(sol.price_subtotal) AS price_subtotal,
            'Sale Order' AS origin,
            sum(sol.product_uom_qty) AS qty,
            pc.profit_center AS profit_center
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            WHERE so.state NOT IN ('draft', 'sent', 'cancel')
            GROUP BY so.date_order, sol.product_id, pp.product_tmpl_id,
            so.company_id, so.user_id, sol.price_subtotal, sol.price_total,
            so.partner_id, pt.categ_id, pc.profit_center, so.name
        """
        return select

    def _pos_order_select(self):
        select = """SELECT min(pol.id) AS id,
            po.date_order::date AS date,
            po.name as name,
            pol.product_id AS product_id,
            pp.product_tmpl_id AS product_tmpl_id,
            po.company_id AS company_id,
            po.partner_id AS partner_id,
            po.user_id AS user_id,
            pt.categ_id AS categ_id,
            sum(pol.price_subtotal_incl) AS price_total,
            sum(pol.price_unit * pol.qty) AS price_subtotal,
            'Point of Sale' AS origin,
            sum(pol.qty) AS qty,
            pc.profit_center AS profit_center
            FROM pos_order_line pol
            LEFT JOIN pos_order po ON po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            WHERE po.state IN ('paid', 'done', 'invoiced')
            GROUP BY po.date_order, pol.product_id, pp.product_tmpl_id,
            po.company_id, po.user_id, pol.qty, pol.price_unit, po.partner_id,
            pt.categ_id, pc.profit_center, pol.price_subtotal_incl, po.name
        """
        return select

    def _invoice_select(self):
        select = """SELECT min(ail.id) AS id,
            ai.date::date AS date,
            ai.name as name,
            ail.product_id AS product_id,
            pp.product_tmpl_id AS product_tmpl_id,
            ai.company_id AS company_id,
            ai.partner_id AS partner_id,
            ai.user_id AS user_id,
            pt.categ_id AS categ_id,
            ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
            count(*) * invoice_type.sign AS price_total,
            sum(ail.price_subtotal_signed) AS price_subtotal,
            'Invoice' AS origin,
            sum(ail.quantity) AS qty,
            pc.profit_center AS profit_center
            FROM account_invoice_line ail
            JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN product_product pp ON pp.id = ail.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            JOIN (
                -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Refund)
                SELECT id,(CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                        THEN -1
                        ELSE 1
                    END) AS sign
                FROM account_invoice ai
            ) AS invoice_type ON invoice_type.id = ai.id
            WHERE ai.state NOT IN ('draft', 'cancel')
            GROUP BY ai.date, ail.product_id, pp.product_tmpl_id,
            ai.company_id, ai.user_id, ail.quantity, ail.price_subtotal,
            ai.partner_id, pt.categ_id, pc.profit_center, ai.residual_company_signed, ai.id,
            invoice_type.sign, ail.price_subtotal_signed, ai.name
        """
        return select

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("CREATE OR REPLACE VIEW %s AS (%s UNION %s UNION %s)" % (
            self._table, self._sale_order_select(), self._pos_order_select(), self._invoice_select()))
