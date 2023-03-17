# -*- coding: utf-8 -*-
{
    'name': "l10n_cu_hr",
    'summary': "",
    'description': "",
    'author': "Desoft VC",
    'website': "https://odoo.desoft.cu",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr', 'l10n_cu_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/occupational_category_views.xml',
        'views/scale_group_views.xml',
        'views/hr_job_views.xml',
        'views/menu_views.xml',
        'data/occupational_category_data.xml',
        # 'data/scale_group_data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
