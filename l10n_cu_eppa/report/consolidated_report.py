# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from pytz import timezone
import io, base64, xlwt
from urllib.request import urlopen
from PIL import Image


class ConsolidatedReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consolidated"
    _description = "Model AC-03"

    @api.model
    def _get_report_values(self, docids, data=None):
        date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
        start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
        end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()

        f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
                      tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')

        currency = str(data['form']['currency_id'])

        is_todos_company = str(data['form']['is_todos_company'])
        docs = {}
        docs['indice_consumo'] = []
        company_id = self.env.user.company_ids
        if is_todos_company == 'uno':
            company_id = self.env['res.company'].search([('id', '=', data['form']['company_id'])])

        query = """SELECT t2.company_id,t2.company ,t2.category_id,t2.category,t2.currency_id ,t2.currency,t2.product_template,t2.produccion_uf,
        t2.materias_p_real,t2.materias_p_fcosto, (t2.materias_p_real-t2.materias_p_fcosto) AS materias_p_variacion,
        t2.sal_ft_real, t2.sal_ft_fcosto, (t2.sal_ft_real-t2.sal_ft_fcosto) AS sal_ft_variacion,
        t2.gastos_ip_real, t2.gastos_ip_fcosto, (t2.gastos_ip_real-t2.gastos_ip_fcosto) AS gastos_ip_variacion,
        t2.gastos_tc_real, t2.gastos_tc_fcosto, (t2.gastos_tc_real-t2.gastos_tc_fcosto) AS gastos_tc_variacion
        FROM (SELECT t1.company_id,t1.company ,t1.category_id,t1.category,t1.currency_id ,t1.currency,t1.product_template,t1.produccion_uf,
          (t1.materias_p_real/t1.produccion_uf) AS materias_p_real, (t1.materias_p_fcosto/t1.produccion_uf) AS materias_p_fcosto, (t1.materias_p_real-t1.materias_p_fcosto) AS materias_p_variacion,
        (t1.sal_ft_real/t1.produccion_uf) AS sal_ft_real, (t1.sal_ft_fcosto/t1.produccion_uf) AS sal_ft_fcosto, (t1.sal_ft_real-t1.sal_ft_fcosto) AS sal_ft_variacion,
        (t1.gastos_ip_real/t1.produccion_uf) AS gastos_ip_real, (t1.gastos_ip_fcosto/t1.produccion_uf) AS gastos_ip_fcosto, (t1.gastos_ip_real-t1.gastos_ip_fcosto) AS gastos_ip_variacion,
        (t1.gastos_tc_real/t1.produccion_uf) AS gastos_tc_real, (t1.gastos_tc_fcosto/t1.produccion_uf) AS gastos_tc_fcosto, (t1.gastos_tc_real-t1.gastos_tc_fcosto) AS gastos_tc_variacion
        FROM (SELECT rc.id AS company_id,rc.name AS company ,pc.id AS category_id,pc.name AS category,ru.id AS currency_id ,ru.name AS currency, pt.name AS product_template,
        SUM(mp.product_qty) AS produccion_uf, SUM(lc.materias_p) AS materias_p_fcosto, SUM(lc.sal_ft) AS sal_ft_fcosto,
        SUM(lc.gastos_ip) AS gastos_ip_fcosto, SUM(lc.gastos_tc) AS gastos_tc_fcosto, SUM(cep.materias_p) AS materias_p_real,
        SUM(cep.sal_ft) AS sal_ft_real, SUM(cep.gastos_ip) AS gastos_ip_real , SUM(cep.gastos_tc) AS gastos_tc_real 
        FROM l10n_cu_mrp_concept_expenses_production as cep INNER JOIN res_company AS rc ON rc.id = cep.company_id  
        INNER JOIN mrp_bom AS mb ON mb.id = cep.mrp_bom_id INNER JOIN product_template AS pt ON pt.id = cep.product_tmpl_id
        INNER JOIN l10n_cu_mrp_wage_worker AS lw ON lw.id = cep.salario
        INNER JOIN l10n_cu_mrp_concept_expenses AS lc ON lc.id = cep.concept_expenses_id
        INNER JOIN mrp_production AS mp ON mp.id = cep.mrp_production_id
        INNER JOIN res_currency AS ru ON ru.id = cep.currency_id AND ru.id =  """ + currency + """
        INNER JOIN product_category AS pc ON pc.id = pt.categ_id
        WHERE  cep.date >= '""" + str(f1) + """' AND cep.date <= '""" + str(f2) + """' AND  cep.state = 'done'
          GROUP BY rc.id,pc.id,ru.id,pt.name 	) AS t1 ) AS t2          
        """
        print(query)
        self.flush()
        self.env.cr.execute(query)
        x = self.env.cr.fetchall()

        query1 = """SELECT  category FROM (""" + query + """) AS t3  GROUP BY category
         """

        self.flush()
        self.env.cr.execute(query1)
        x1 = self.env.cr.fetchall()
        query2 = """SELECT  product_template FROM (""" + query + """) AS t3  GROUP BY product_template
         """
        self.flush()
        self.env.cr.execute(query2)
        x2 = self.env.cr.fetchall()

        # ordenar las compañías descendentemente para q se sume gradual y no tener un bucle interminable
        aux_query = """SELECT c1.id,c1.name,c1.parent_id  FROM res_company as c1 ORDER BY id DESC"""
        self.flush()
        self.env.cr.execute(aux_query)
        aux_x = self.env.cr.fetchall()
        # crear  una matrix en blanco  o 0 de columana i= cantidad de compañías y j= cantidad de datos
        i1 = []
        for i_company in aux_x:
            for j_category in x1:
                for j_product in x2:
                    j = {}
                    j['bom'] = j_product[0] or None
                    j['produccion_uf'] = 0
                    j['materias_p_real'] = 0
                    j['materias_p_fcosto'] = 0
                    j['materias_p_variacion'] = 0
                    j['sal_ft_real'] = 0
                    j['sal_ft_fcosto'] = 0
                    j['sal_ft_variacion'] = 0
                    j['gastos_ip_real'] = 0
                    j['gastos_ip_fcosto'] = 0
                    j['gastos_ip_variacion'] = 0
                    j['gastos_tc_real'] = 0
                    j['gastos_tc_fcosto'] = 0
                    j['gastos_tc_variacion'] = 0
                    j['company'] = i_company[1] or None
                    j['company_id'] = i_company[0] or None
                    j['company_parent_id'] = i_company[2] or None
                    j['category'] = j_category[0] or None
                    j['count'] = 0
                    i1.append(j)

        # llenando datos
        for i_matriz in i1:
            for dato in x:
                if dato[3] == i_matriz['category'] and dato[6] == i_matriz['bom'] and dato[1] == \
                        i_matriz['company']:
                    i_matriz['produccion_uf'] = dato[7]
                    i_matriz['materias_p_real'] = dato[8]
                    i_matriz['materias_p_fcosto'] = dato[9]
                    i_matriz['materias_p_variacion'] = dato[10]
                    i_matriz['sal_ft_real'] = dato[11]
                    i_matriz['sal_ft_fcosto'] = dato[12]
                    i_matriz['sal_ft_variacion'] = dato[13]
                    i_matriz['gastos_ip_real'] = dato[14]
                    i_matriz['gastos_ip_fcosto'] = dato[15]
                    i_matriz['gastos_ip_variacion'] = dato[16]
                    i_matriz['gastos_tc_real'] = dato[17]
                    i_matriz['gastos_tc_fcosto'] = dato[18]
                    i_matriz['gastos_tc_variacion'] = dato[19]

        # sumar de hijos a padres
        # Primedio
        # Suma

        for i_dato in i1:
            count = 0
            for buscando_dato in i1:
                if i_dato['company_id'] == buscando_dato['company_parent_id'] \
                        and i_dato['category'] == buscando_dato['category'] \
                        and i_dato['bom'] == buscando_dato['bom']:
                    if float(i_dato['produccion_uf'])>0 and float(buscando_dato['produccion_uf'])>0:
                        i_dato['count'] = i_dato['count']+1
                    i_dato['produccion_uf'] = i_dato['produccion_uf'] + buscando_dato['produccion_uf']
                    i_dato['materias_p_real'] = i_dato['materias_p_real'] + buscando_dato['materias_p_real']
                    i_dato['materias_p_fcosto'] = i_dato['materias_p_fcosto'] + buscando_dato['materias_p_fcosto']
                    i_dato['sal_ft_real'] = i_dato['sal_ft_real'] + buscando_dato['sal_ft_real']
                    i_dato['sal_ft_fcosto'] = i_dato['sal_ft_fcosto'] + buscando_dato['sal_ft_fcosto']
                    i_dato['gastos_ip_real'] = i_dato['gastos_ip_real'] + buscando_dato['gastos_ip_real']
                    i_dato['gastos_ip_fcosto'] = i_dato['gastos_ip_fcosto'] + buscando_dato['gastos_ip_fcosto']
                    i_dato['gastos_tc_real'] = i_dato['gastos_tc_real'] + buscando_dato['gastos_tc_real']
                    i_dato['gastos_tc_fcosto'] = i_dato['gastos_tc_fcosto'] + buscando_dato['gastos_tc_fcosto']

        # # sumar de hijos a padres
        # # Division
        for i_dato in i1:
            if i_dato['produccion_uf'] > 0 and i_dato['count'] > 0 :
                i_dato['materias_p_real'] = (i_dato['materias_p_real']) / i_dato['produccion_uf']
                i_dato['materias_p_fcosto'] = (i_dato['materias_p_fcosto']) / i_dato['produccion_uf']
                i_dato['sal_ft_real'] = (i_dato['sal_ft_real']) / i_dato['produccion_uf']
                i_dato['sal_ft_fcosto'] = (i_dato['sal_ft_fcosto']) / i_dato['produccion_uf']
                i_dato['gastos_ip_real'] = (i_dato['gastos_ip_real']) / i_dato['produccion_uf']
                i_dato['gastos_ip_fcosto'] = (i_dato['gastos_ip_fcosto']) / i_dato['produccion_uf']
                i_dato['gastos_tc_real'] = (i_dato['gastos_tc_real']) / i_dato['produccion_uf']
                i_dato['gastos_tc_fcosto'] = (i_dato['gastos_tc_fcosto']) / i_dato['produccion_uf']
            i_dato['gastos_tc_variacion'] = i_dato['gastos_tc_real'] - i_dato['gastos_tc_fcosto']
            i_dato['materias_p_variacion'] = i_dato['materias_p_real'] - i_dato['materias_p_fcosto']
            i_dato['sal_ft_variacion'] = i_dato['sal_ft_real'] - i_dato['sal_ft_fcosto']
            i_dato['gastos_ip_variacion'] = i_dato['gastos_ip_real'] - i_dato['gastos_ip_fcosto']

        d = []
        for c in company_id:
            company = {}
            company['company'] = c.name
            company['datos'] = []
            for a in x1:
                category = {}
                category['category'] = a[0]
                category['datos'] = []
                for i in i1:
                    if i['company_id'] == c.id and i['category'] == a[0]:
                        bom = {}
                        bom['bom'] = i['bom']
                        bom['produccion_uf'] = i['produccion_uf']
                        bom['materias_p_real'] = i['materias_p_real']
                        bom['materias_p_fcosto'] = i['materias_p_fcosto']
                        bom['materias_p_variacion'] = i['materias_p_variacion']
                        bom['sal_ft_real'] = i['sal_ft_real']
                        bom['sal_ft_fcosto'] = i['sal_ft_fcosto']
                        bom['sal_ft_variacion'] = i['sal_ft_variacion']
                        bom['gastos_ip_real'] = i['gastos_ip_real']
                        bom['gastos_ip_fcosto'] = i['gastos_ip_fcosto']
                        bom['gastos_ip_variacion'] = i['gastos_ip_variacion']
                        bom['gastos_tc_real'] = i['gastos_tc_real']
                        bom['gastos_tc_fcosto'] = i['gastos_tc_fcosto']
                        bom['gastos_tc_variacion'] = i['gastos_tc_variacion']
                        if float(bom['produccion_uf']) > 0.00000:
                            category['datos'].append(bom)
                if category['datos'] != []:
                    company['datos'].append(category)
            d.append(company)
        moneda = self.env['l10n_cu_mrp.commercialization'].search(
            [('currency_id', '=', data['form']['currency_id'])])
        comp = self.env.ref('base.main_company')
        return {
            'description': self._description,
            'company_id': comp,
            'icon': comp.logo,
            'doc_ids': docids,
            'moneda': moneda.code,
            'doc_model': data['model'],
            'docs': d,
            'date': date,
            'start': start,
            'end': end,
        }
