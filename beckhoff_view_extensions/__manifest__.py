# -*- coding: utf-8 -*-
{
    'name': "beckhoff_view_extensions",

    'summary': """
        This module provides simple view adjustments.""",

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
    'depends': ['base','product_brand','point_of_sale', 'purchase', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/product_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/stock_views.xml',
        'views/views.xml'
    ],
}
