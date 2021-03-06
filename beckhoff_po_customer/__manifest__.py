# -*- coding: utf-8 -*-
{
    'name': "beckhoff_po_customer",

    'summary': """
        Creating Purchase Orders from Sale Orders""",

    'description': """
        This App will faciliate a wizard to create purchase order from sale orders and create the fields Salesperson and Customer to be assigned to a Purchase Order. The Purchase Orders will be shown in Partner Form.
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'sale_management', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_sale_views.xml',
        'views/purchase_views.xml',
        'wizard/purchase_order_wizard_form.xml',
    ],
}
