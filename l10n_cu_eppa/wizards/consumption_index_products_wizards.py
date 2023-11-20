# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
import calendar


class ConsumptionIndexProductsWizards(models.TransientModel):
    _name = 'l10n_cu_eppa.consumption_index_products_wizards'
    _description = 'Consumption Index for Products Wizards'

    date = fields.Date('Date', default=datetime.today(),
                       required=True)
    start = fields.Date('Start', default=datetime.today().replace(day=1),
                        required=True)
    end = fields.Date('End',
                      default=datetime.today().replace(
                          day=calendar.monthrange(year=datetime.today().year, month=datetime.today().month)[1]),
                      required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 required=True)
    is_product = fields.Selection([('uno', 'An Product'), ('todos', 'All the Products')],
                                'Select Products',
                                help='To select Product', default="todos",
                                required=True)
    domain = "{}"
    product_tmpl_id = fields.Many2one('product.template', string='Product',
                                      domain=[('sale_ok', '=', 1), ('active', '=', True), ('type', '=', 'product')],
                                      help='Product', index=True)
    is_todos_prod_unit = fields.Selection([('uno', 'A Production Unit'), ('todos', 'All the Production Units')],
                                          'Select Production Unit',
                                          help='To select Production Unit', default="todos",
                                          required=True)
    prod_unit_id = fields.Many2one('production.unit', string='Production Unit', required=True,
                                   default=lambda self: self.env.user.prod_unit_id)

    departament_id = fields.Many2one('mrp.department', help='MRP Departament', required=True,
                                     default=lambda self: self.env.ref('l10n_cu_mrp.mrp_department_produccion').id)


    is_ingredient = fields.Selection([('uno', 'An Ingredient'), ('todos', 'All the Ingredients')],
                                'Select Ingredients',
                                help='To select ingredients', default="todos",
                                required=True)
    ingredient_tmpl_id = fields.Many2one('product.template', string='Ingredient',
                                      domain=[('purchase_ok', '=', 1), ('active', '=', True), ('type', '=', 'product')],
                                      help='Product', index=True)
    commercialization_id = fields.Many2one('l10n_cu_mrp.commercialization', help='Form of Commercialization',
                                           required=True, default=lambda self: self.env.ref('l10n_cu_mrp.MN').id)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': 'report.l10n_cu_eppa.consumption_index_products',
            'form': {
                'date': self.date,
                'start': self.start,
                'end': self.end,
                'company_id': self.company_id.id,
                'is_product': self.is_product,
                'product_tmpl_id': self.product_tmpl_id.id,
                'is_ingredient': self.is_ingredient,
                'ingredient_tmpl_id': self.ingredient_tmpl_id.id,
                'commercialization_id': self.commercialization_id.id,
                'is_todos_prod_unit': self.is_todos_prod_unit,
                'prod_unit_id': self.prod_unit_id.id,
                'departament_id': self.departament_id.id,
            },
        }
        return self.env.ref('l10n_cu_eppa.action_report_consumption_index_products').report_action(self, data=data)
