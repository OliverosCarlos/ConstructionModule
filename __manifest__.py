# -*- coding: utf-8 -*-
{
    'name': "construction",
    'summary': 'Modulo para calculo de precios unitarios',
    'sequence':'-100',
    'description': """
    PRECIOS UNITARIOS
    ------------------------------------------------------------------
        - etc
        - etc
    -------------------------------------------------------------------
        - etc
        - etc
    """,

    'author': "Sohersa",
    'website': "http://www.sohersabim.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    
    'category': 'Services/construction',
    'version': '0.2',
    # any module necessary for this one to work correctly
    'depends': [
        'web',
        'website',
        'base'
        ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/projects_views.xml',
        'views/views.xml',
        'views/workforce_views.xml',
        'views/catalogs_views.xml',
        'views/clients_views.xml',
        'views/materials_views.xml',
        'views/machinery_views.xml',
        'views/suppliers_views.xml',
        'views/bim_views.xml',
        'views/assets.xml',
        #reports
        'report/insumos_report.xml',
        'report/basics_report.xml',
        'report/concepts_report.xml',
        'report/machinery_report.xml',
        'report/materials_report.xml',
        'report/workforce_report.xml',
        # 'report/tst_report.xml',
        #wizard
        'wizard/budgets.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}