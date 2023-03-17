# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from pytz import timezone
import io, base64


class ConsumptionIndexCategoriesReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consumption_index_categories"
    _description = "Consumption Index for Categories"

    @api.model
    def _get_report_values(self, docids, data=None):
        date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
        start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
        end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()

        f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
        f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
                      tzinfo=None)

        # utiles para las condiciones de limitar
        company_id = self.env.user.company_ids
        is_todos_company = str(data['form']['is_todos_company'])
        if is_todos_company == 'uno':
            company_id = self.env['res.company'].search([('id', '=', data['form']['company_id'])])

        is_ingredient = str(data['form']['is_todos'])
        ingredient_id = self.env['product.template'].search([])
        if is_ingredient == 'uno':
            ingredient_id = self.env['product.template'].search([('id', '=', data['form']['product_tmpl_id'])])

        is_category = str(data['form']['is_category'])
        category_id = self.env['product.category'].search([])
        if is_category == 'uno':
            category_id = self.env['product.category'].search([('id', '=', data['form']['category_id'])])

        is_todos_prod_unit = str(data['form']['is_todos_prod_unit'])
        prod_unit_id = self.env['production.unit'].search([])
        if is_todos_prod_unit == 'uno':
            prod_unit_id = self.env['production.unit'].search([('id', '=', data['form']['prod_unit_id'])])

        commercialization_id = self.env['l10n_cu_mrp.commercialization'].search(
            [('id', '=', data['form']['commercialization_id'])])

        query = """ SELECT MAX(level) FROM  production_unit"""
        self.flush()
        self.env.cr.execute(query)
        x = self.env.cr.fetchall()
        print(company_id)
        print(x[0][0])
        for company in company_id:
            z = self.env['mrp.production'].search([('date_planned_start','>=',start),('date_planned_start','<=',end)])
            print(self.get_childs(company))
        for prod_unit in prod_unit_id:
            print(self.get_childs(prod_unit))

        docs = []
        comp = self.env.ref('base.main_company')
        return {
            'description': self._description,
            'company_id': comp,
            'icon': comp.logo,
            'docids': docids,
            'docmodel': data['model'],
            'commercialization_id': commercialization_id,
            'docs': docs,
            'date': date,
            'start': start,
            'end': end,
        }

    def get_childs(self,production_unit):
        ids=[]
        if production_unit.child_ids :
            print(production_unit.child_ids)
    #         return self.env['mrp.production'].search([('id', 'in', ids)])
    #     ids.append()
    #     return self.get_companys_child(self.env['mrp.production'].search([('id', 'in', ids)]))


    def convert_models_to_ids(self, models):
        aux1 = '('
        aux2 = ''
        count = 0
        for x1 in models:
            count = count + 1
            aux2 = aux2 + str(x1.id)
            if count != len(models):
                aux2 = aux2 + ','
        aux1 = aux1 + aux2 + ')'
        if 0 == len(models):
            aux1 = "('')"
        return aux1

    def convert_models_to_name(self, models):
        aux1 = '('
        aux2 = ''
        count = 0

        for x1 in models:
            count = count + 1
            aux2 = aux2 + "'" + str(x1.name) + "'"
            if count != len(models):
                aux2 = aux2 + ','
        aux1 = aux1 + aux2 + ')'
        if 0 == len(models):
            aux1 = "('')"
        return aux1

    def convert_models_to_array_ids(self, models):
        x = []
        for x1 in models:
            x.append(x1.id)
        return x