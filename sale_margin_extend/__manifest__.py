# -*- coding: utf-8 -*-
{
    'name': "sale_margin_extend",

    'summary': """
        Adds the margin calculation to PoS Orders, Repair Orders and Invoices""",

    'description': """
        Inspired by Margins in Odoo from Odoo SA and Sylvain LE GAL OCA/pos_order_margin (10.0)
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp_repair', 'account', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'views/account_invoice_views.xml',
        'views/pos_order_views.xml',
        'views/repair_views.xml',
        'views/sale_views.xml',
    ],
}
