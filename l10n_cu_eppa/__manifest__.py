# -*- coding: utf-8 -*-
{
    'name': "SisCostX",

    'summary': """
        Sistema de Costos para la EPPA en Villa Clara.
        """,

    'description': """
        Sistema de Costos para la Empresa Provincial
        Productora de Alimentos in Villa Clara.
    """,

    'author': "Desoft VC",
    'website': "https://odoo.desoft.cu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/System of Costs',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_cu_mrp'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/report_templates.xml',
        'views/product_template_views.xml',
        'report/mrp_bom_report_views.xml',
        'report/wage_worker_report_views.xml',
        'report/concept_expenses_report_views.xml',
        'report/consolidated_report_views.xml',
        'report/consumption_index_categories_report_views.xml',
        'report/consumption_index_companies_report_views.xml',
        'report/consumption_index_ingredients_report_views.xml',
        'report/consumption_index_products_report_views.xml',
        'wizards/consolidated_wizards_views.xml',
        'wizards/consumption_index_categories_wizards_views.xml',
        'wizards/consumption_index_companies_wizards_views.xml',
        'wizards/consumption_index_ingredients_wizards_views.xml',
        'wizards/consumption_index_products_wizards_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
