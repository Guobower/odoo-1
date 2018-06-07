# -*- coding: utf-8 -*-
{
    'name': "beckhoff_po_customer_repair",

    'summary': """
        Allows the user to create a purchase order from a repair order""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.1',

    # any module necessary for this one to work correctly
    'depends': ['beckhoff_po_customer'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/purchase_order_wizard_form.xml',
    ],
}
