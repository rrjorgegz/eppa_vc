# -*- coding: utf-8 -*-
{
    "name": "l10n_cu_mrp",
    "summary": "",
    "description": "",
    "author": "Desoft VC",
    "website": "https://odoo.desoft.cu",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Manufacturing",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["mrp", "l10n_cu_hr"],
    # always loaded
    "data": [
        "views/menu_views.xml",
        "views/commercialization_views.xml",
        "views/mrp_bom_line_views.xml",
        "views/mrp_production_views.xml",
        "views/concept_expenses_views.xml",
        "views/concept_expenses_production_views.xml",
        "views/forces_work_views.xml",
        "views/wage_worker_views.xml",
        "views/mrp_bom_views.xml",
        "views/production_unit_views.xml",
        "views/res_users_views.xml",
        "views/mrp_department_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/commercialization_data.xml",
        "data/uom_data.xml",
        "data/stock_data.xml",
        "data/product_categories_data.xml",
        "data/decimal_precision_data.xml",
        "data/mrp_department_data.xml",
        "data/production_unit_data.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
}
