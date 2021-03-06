# -*- coding: utf-8 -*-
{
    'name': "beckhoff_fleet_extensions",

    'summary': """
        Small extensions for the fleet module""",

    'description': """
        Adds fields for:
        - Fuel PIN
        - Field for link to invoice document in DMS
    """,

    'author': "Jan Beckhoff",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.1',

    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'views/views.xml'
    ]
}
