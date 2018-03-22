# -*- coding: utf-8 -*-
{
    'name': "sale_order_amount_to_invoice",

    'summary': """
        Add amount to invoice to sale order list and form view""",

    'description': """

    """,

    'author': "Jan Beckhoff",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
