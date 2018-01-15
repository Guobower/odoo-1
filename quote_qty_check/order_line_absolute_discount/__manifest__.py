# -*- coding: utf-8 -*-
{
    'name': "order_line_absolute_discount",

    'summary': """
        Adds the possibility to choose an absolute discount in sale order lines.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ]
}
