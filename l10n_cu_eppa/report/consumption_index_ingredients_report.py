# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from builtins import print
from datetime import datetime, time, timedelta
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from pytz import timezone
import io, base64


class ConsumptionIndexIngredientsReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consumption_index_ingredients"
    _description = "Consumption Index for Ingredients"

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

    @api.model
    def _get_report_values(self, docids, data=None):
        date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
        start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
        end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()

        fi = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
        fe = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
                      tzinfo=None)

        # utiles para las condiciones de limitar
        company_id = self.env.user.company_ids
        is_todos_company = str(data['form']['is_todos_company'])
        if is_todos_company == 'uno':
            company_id = self.env['res.company'].search([('id', '=', data['form']['company_id'])])
        is_ingredient = str(data['form']['is_ingredient'])
        ingredient_id = self.env['product.template'].search([])
        if is_ingredient == 'uno':
            ingredient_id = self.env['product.template'].search([('id', '=', data['form']['ingredient_tmpl_id'])])

        is_product = str(data['form']['is_product'])
        product_id = self.env['product.template'].search([])
        if is_product == 'uno':
            product_id = self.env['product.template'].search([('id', '=', data['form']['product_tmpl_id'])])
        commercialization_id = self.env['l10n_cu_mrp.commercialization'].search(
            [('id', '=', data['form']['commercialization_id'])])
        company = self.convert_models_to_array_ids(company_id)
        commercialization = self.convert_models_to_ids(commercialization_id)
        ingredient = self.convert_models_to_name(ingredient_id)
        product = self.convert_models_to_name(product_id)

        # Tabla de producción de cada empresa
        query = """SELECT  pd.code,AVG(pd.indice_consumo) AS indice_consumo,AVG(pd.indice_consumo_plan) AS indice_consumo_plan,SUM(pd.consumo_plan)AS consumo_plan,SUM(pd.product_uom_qty)AS consumo_real,(SUM(pd.product_uom_qty) - SUM(pd.consumo_plan)) AS exceso,(SUM(pd.product_uom_qty) /nullif(SUM(pd.consumo_plan),0)*100) AS cumplimiento,pd.ingrediente,pd.ingrediente_id,pd.commercialization,pd.commercialization_id,pd.company,pd.company_id,pd.company_parent_id,pd.product_id,pd.product,pd.produccion,pd.partner,pd.partner_parent_id,pd.partner_name
                                  FROM  (SELECT  pt.default_code AS code, sm.indice_consumo,sm.indice_consumo_plan,sm.consumo_plan,(sm.product_uom_qty / nullif(ui.factor,0)) AS product_uom_qty,ing.name AS ingrediente,ing.id AS ingrediente_id,co.name AS commercialization,co.id AS commercialization_id,rc.name AS company,rc.id AS company_id,rc.parent_id AS company_parent_id,cat.id AS category_id,cat.name AS category,pt.id AS product_id,pt.name AS product,mp.produccion, rt.id AS partner, rt.patner_matriz_id AS partner_parent_id, rt.name AS partner_name
                                  FROM mrp_production mp  INNER JOIN mrp_bom mb  ON mp.bom_id = mb.id INNER JOIN res_company rc ON mp.company_id = rc.id
                                  INNER JOIN product_product pp ON mp.product_id = pp.id INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id AND pt.name IN """ + product + """
                                  INNER JOIN stock_picking_type st ON mp.picking_type_id = st.id
                                  INNER JOIN stock_warehouse sw ON st.warehouse_id = sw.id
                                  INNER JOIN res_partner rt ON sw.partner_id = rt.id
                                  INNER JOIN stock_move sm ON  mp.id = sm.raw_material_production_id INNER JOIN l10n_cu_mrp_commercialization co ON  mb.forma_c = co.id
                                  INNER JOIN uom_uom  AS  ui ON sm.product_uom =ui.id INNER JOIN product_product ppt ON sm.product_id = ppt.id INNER JOIN product_template AS  ing ON  ppt.product_tmpl_id = ing.id 
                                  AND ing.purchase_ok=True AND ing.active=True  AND ing.name IN """ + ingredient + """
                                  INNER JOIN product_category  AS  cat ON ing.categ_id = cat.id
    							  WHERE mp.date_planned_start >= '""" + str(fi) + """'
                                  AND mp.date_planned_start <='""" + str(fe) + """' AND mp.state='done' OR mp.state='confirmed' 
                                  AND co.id IN """ + commercialization + """)AS pd  
                                  GROUP BY code,ingrediente,ingrediente_id,commercialization,commercialization_id,company,company_id,company_parent_id,product_id,product,produccion,partner,partner_parent_id,partner_name
                                  ORDER BY pd.company_id
                            """
        print(query)
        self.flush()
        self.env.cr.execute(query)
        x = self.env.cr.fetchall()

        # Total de ingredientes q se utilizan
        query1 = """SELECT  ingrediente FROM (""" + query + """) AS tabla1 GROUP BY ingrediente"""
        self.flush()
        self.env.cr.execute(query1)
        x1 = self.env.cr.fetchall()

        # Formas de comercialización q se utilizan
        query1 = """SELECT  commercialization_id,commercialization FROM (""" + query + """) AS tabla1 GROUP BY commercialization_id,commercialization"""
        self.flush()
        self.env.cr.execute(query1)
        x2 = self.env.cr.fetchall()
        #
        # # category q se utilizan
        # query3 = """SELECT  category_id,category FROM (""" + query + """) AS tabla1 GROUP BY category_id,category"""
        # self.flush()
        # self.env.cr.execute(query3)
        # x3 = self.env.cr.fetchall()

        # product q se utilizan
        query4 = """SELECT  product FROM (""" + query + """) AS tabla1 GROUP BY product"""
        self.flush()
        self.env.cr.execute(query4)
        x4 = self.env.cr.fetchall()

        query5 = """SELECT partner,partner_parent_id, partner_name,SUM(produccion),company FROM (""" + query + """) AS tabla1 GROUP BY partner,partner_parent_id,partner_name,company ORDER BY partner DESC"""
        self.flush()
        self.env.cr.execute(query5)
        aux_5 = self.env.cr.fetchall()

        # ordenar las compañías descendentemente para q se sume gradual y no tener un bucle interminable
        aux_query = """SELECT id,name,parent_id FROM res_company ORDER BY id DESC"""
        self.flush()
        self.env.cr.execute(aux_query)
        aux_x = self.env.cr.fetchall()

        # crear  una matrix en blanco  o 0 de columana i= cantidad de compañías y j= cantidad de datos
        i = []
        for i_company in aux_x:
            for i_partner in aux_5:
                for i_product in x4:
                    for j_ingredientes in x1:
                        j = {}
                        j['code'] = None
                        j['indice_consumo'] = 0
                        j['indice_consumo_plan'] = 0
                        j['consumo_plan'] = 0
                        j['consumo_real'] = 0
                        j['exceso'] = 0
                        j['cumplimiento'] = 0
                        j['ingrediente'] = j_ingredientes[0] or None
                        j['commercialization'] = commercialization_id.name or None
                        j['commercialization_id'] = commercialization_id.id or None
                        j['company'] = i_company[1] or None
                        j['company_id'] = i_company[0] or None
                        j['company_parent_id'] = i_company[2] or None
                        j['product'] = i_product[0] or None
                        j['produccion'] = 0
                        j['partner'] = i_partner[0] or None
                        j['partner_parent_id'] = i_partner[1] or None
                        j['partner_name'] = i_partner[2] or None
                        i.append(j)

        #     # llenando la matrix con datos obtnidos
        for i_matriz in i:
            for dato in x:
                if dato[7] == i_matriz['ingrediente'] and dato[9] == i_matriz['commercialization'] and dato[11] == \
                        i_matriz['company'] and dato[15] == i_matriz['product']:
                    i_matriz['code'] = dato[0]
                    if dato[0] == '':
                        i_matriz['code'] = dato[9]
                    i_matriz['indice_consumo'] = dato[1] or 0
                    i_matriz['indice_consumo_plan'] = dato[2] or 0
                    i_matriz['consumo_plan'] = dato[3] or 0
                    i_matriz['consumo_real'] = dato[4] or 0
                    i_matriz['exceso'] = dato[5] or 0
                    i_matriz['cumplimiento'] = dato[6] or 0
                    i_matriz['produccion'] = dato[16] or 0

        # sumar de hijos a padres
        for i_dato in i:
            cont = 0
            for buscando_dato in i:
                if i_dato['partner'] == buscando_dato['partner_parent_id'] \
                        and i_dato['commercialization_id'] == buscando_dato['commercialization_id'] \
                        and i_dato['ingrediente'] == buscando_dato['ingrediente'] \
                        and i_dato['company'] == buscando_dato['company'] \
                        and i_dato['product'] == buscando_dato['product']:
                    i_dato['indice_consumo'] = i_dato['indice_consumo'] + buscando_dato['indice_consumo']
                    i_dato['indice_consumo_plan'] = i_dato['indice_consumo_plan'] + buscando_dato['indice_consumo_plan']

                    i_dato['consumo_real'] = i_dato['consumo_real'] + buscando_dato['consumo_real']

                    i_dato['consumo_plan'] = i_dato['consumo_plan'] + buscando_dato['consumo_plan']
                    i_dato['exceso'] = i_dato['consumo_real'] - i_dato['consumo_plan']
                    i_dato['cumplimiento'] = 0
                    aux = 0
                    if i_dato['consumo_plan'] > 0:
                        aux = i_dato['consumo_real'] / i_dato['consumo_plan']
                    i_dato['cumplimiento'] = aux * 100
                    if buscando_dato['consumo_real'] > 0:
                        cont = cont + 1
                    i_dato['produccion'] = i_dato['produccion'] + buscando_dato['produccion']
            if cont > 1:
                i_dato['indice_consumo'] = i_dato['indice_consumo'] / cont
                i_dato['indice_consumo_plan'] = i_dato['indice_consumo_plan'] / cont

        for i_dato in i:
            cont = 0
            for buscando_dato in i:
                if i_dato['company_id'] == buscando_dato['company_parent_id'] \
                        and i_dato['commercialization_id'] == buscando_dato['commercialization_id'] \
                        and i_dato['ingrediente'] == buscando_dato['ingrediente'] \
                        and i_dato['partner'] == buscando_dato['partner'] \
                        and i_dato['product'] == buscando_dato['product']:
                    i_dato['indice_consumo'] = i_dato['indice_consumo'] + buscando_dato['indice_consumo']
                    i_dato['indice_consumo_plan'] = i_dato['indice_consumo_plan'] + buscando_dato['indice_consumo_plan']

                    i_dato['consumo_real'] = i_dato['consumo_real'] + buscando_dato['consumo_real']

                    i_dato['consumo_plan'] = i_dato['consumo_plan'] + buscando_dato['consumo_plan']
                    i_dato['exceso'] = i_dato['consumo_real'] - i_dato['consumo_plan']
                    i_dato['cumplimiento'] = 0
                    aux = 0
                    if i_dato['consumo_plan'] > 0:
                        aux = i_dato['consumo_real'] / i_dato['consumo_plan']
                    i_dato['cumplimiento'] = aux * 100
                    if buscando_dato['consumo_real'] > 0:
                        cont = cont + 1
                    i_dato['produccion'] = i_dato['produccion'] + buscando_dato['produccion']
            if cont > 1:
                i_dato['indice_consumo'] = i_dato['indice_consumo'] / cont
                i_dato['indice_consumo_plan'] = i_dato['indice_consumo_plan'] / cont

        # estructurando para mostrar a la vista

        d = []
        for aux_a in aux_x:
            if aux_a[0] in company:
                a = {}
                a['company'] = aux_a[1]
                a['company_id'] = aux_a[0]
                a['company_parent_id'] = aux_a[2]
                a['datos'] = []
                for aux_c in aux_5:
                    c = {}
                    c['partner'] = aux_c[2]
                    c['produccion'] = aux_c[3]
                    c['datos'] = []
                    for aux_b in x1:
                        b = {}
                        b['ingrediente'] = aux_b[0]
                        b['datos'] = []
                        for aux_d in i:
                            if aux_d['partner'] == aux_c[0] and aux_a[1] == aux_d['company'] and aux_b[0] == aux_d['ingrediente'] and aux_d[
                                'produccion'] != 0 and float(aux_d['consumo_real']) > 0:
                                j = {}
                                j['code'] = aux_d['code']
                                j['indice_consumo'] = aux_d['indice_consumo']
                                j['indice_consumo_plan'] = aux_d['indice_consumo_plan']
                                j['consumo_plan'] = aux_d['consumo_plan']
                                j['consumo_real'] = aux_d['consumo_real']
                                j['exceso'] = aux_d['exceso']
                                j['cumplimiento'] = aux_d['cumplimiento']
                                j['ingrediente'] = aux_d['ingrediente']
                                j['commercialization'] = aux_d['commercialization']
                                j['commercialization_id'] = aux_d['commercialization_id']
                                j['product'] = aux_d['product']
                                j['produccion'] = aux_d['produccion']
                                b['datos'].append(j)
                        if b['datos'] != []:
                            c['datos'].append(b)
                    if c['datos'] != []:
                        a['datos'].append(c)
                if a['datos'] != []:
                    d.append(a)

        comp = self.env.ref('base.main_company')
        return {
            'description': self._description,
            'company_id': comp,
            'icon': comp.logo,
            'docids': docids,
            'docmodel': data['model'],
            'commercialization_id': commercialization_id,
            'docs': d,
            'date': date,
            'start': start,
            'end': end,
        }
