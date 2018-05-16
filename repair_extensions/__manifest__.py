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

        Helpdesk:
        - Create Repair order from helpdesk ticket
        - add smart button on ticket for repairs linked to that ticket
        - add Status fields for repair and rma in helpdesk ticket
    """,

    'author': "Jan Beckhoff",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp_repair', 'helpdesk_timesheet', 'rma', 'product_brand'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/repair_order_report.xml',
        'views/helpdesk_views.xml',
        'views/kanban_view.xml',
        'views/rma_views.xml',
        'views/views.xml',
    ]
}
