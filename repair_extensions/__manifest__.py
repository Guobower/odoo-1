# -*- coding: utf-8 -*-
{
    'name': "repair_extensions",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        - Search for product from customer purchasing history (account.invoice.line)
        - Display category and Brand of product (based on OCA/product_brand)
        - Add a field to store amount of money the customer is willing to pay without sending a quote
        - Add a field for the responsible technician / team
        - Replace the built-in Kanban view
        - Repair reference = readonly
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp_repair'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/kanban_view.xml',
    ]
}
