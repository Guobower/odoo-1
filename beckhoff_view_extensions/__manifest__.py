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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product_brand','point_of_sale', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/product_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
