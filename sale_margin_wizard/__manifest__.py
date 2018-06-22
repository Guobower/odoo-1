# -*- coding: utf-8 -*-
{
    'name': "sale_margin_wizard",

    'summary': """
        This module provides a wizard to view margins and change prices""",

    'description': """

    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_margin_extend','order_line_absolute_discount', 'beckhoff_price_gross', 'sale_margin'],

    # always loaded
    'data': [
        'wizard/product_template_wizard_form.xml',
        'wizard/sale_order_wizard_form.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
}
