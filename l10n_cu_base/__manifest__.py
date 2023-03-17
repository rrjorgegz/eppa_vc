# -*- coding: utf-8 -*-
{
    'name': "l10n_cu_base",
    'summary': "",
    'description': "",
    'author': "Desoft VC",
    'website': "https://odoo.desoft.cu",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['base','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_module_category_data.xml',
        'data/res_state_data.xml',
        'data/res_municipality_data.xml',
        'data/res_lang_data.xml',
        'data/res_currency_data.xml',
        'data/res_company_data.xml',
        'views/res_company_views.xml',
        'views/res_municipality_views.xml',
        'views/res_partner_views.xml',
        'views/res_partner_rating_views.xml',
        'views/res_organism_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
