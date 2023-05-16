# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from pytz import timezone
import io, base64


class ConsumptionIndexProductsReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consumption_index_products"
    _description = "Consumption Index for Products"

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
            aux1 = "('0')"
        return aux1

    @api.model
    def _get_report_values(self, docids, data=None):
        date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
        start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
        end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()
        f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
        f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
                      tzinfo=None)
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
        departament_id = self.env['mrp.department'].search([('id', '=', data['form']['departament_id'])])
        max_level_prod_unit = """ SELECT MAX(level) FROM  production_unit"""
        self.flush()
        self.env.cr.execute(max_level_prod_unit)
        max_level = self.env.cr.fetchall()
        prod_unit = """SELECT pu.name,pu.level FROM  production_unit pu"""
        self.flush()
        self.env.cr.execute(prod_unit)
        x_prod_unit = self.env.cr.fetchall()
        padre_prod_unit = """SELECT pu.name,pu.level, pu1.name AS parent FROM  production_unit pu
                            INNER JOIN production_unit pu1 ON pu.parent_id = pu1.id"""
        self.flush()
        self.env.cr.execute(padre_prod_unit)
        x_padre_prod_unit = self.env.cr.fetchall()

        query_init = """SELECT t0.nombre_comp,t0.nombre_prod_unit,t0.prod_categ,t0.nombre_ingrediente, AVG(t0.indice_consumo) AS indice_consumo,AVG(t0.indice_consumo_plan) AS indice_consumo_plan,SUM(t0.product_uom_qty) AS consumo_real, SUM(t0.consumo_plan)AS consumo_plan, (SUM(t0.product_uom_qty) - SUM(t0.consumo_plan)) AS exceso,(SUM(t0.product_uom_qty) /nullif(SUM(t0.consumo_plan),0)*100) AS cumplimiento,SUM(t0.produccion) FROM
                    (SELECT mp.produccion,rcmp.name AS nombre_comp, pcmp.name AS prod_categ, pump.id AS prod_unit_id,pump.name AS nombre_prod_unit, mdmp.name AS nombre_mrp_dep ,ptmp.name AS nombre_production,pcmp.name AS categoria_production,rcmp.name company_production,ptmb.name AS nombre_lista_material,ptsm.id AS ingrediente_id,ptsm.name AS nombre_ingrediente,sm.indice_consumo,bl.indice_consumo AS indice_consumo_plan,sm.product_uom_qty/uu.factor AS product_uom_qty, bl.product_qty/uo.factor*(mp.product_qty/mb.product_qty) AS consumo_plan
                    FROM mrp_production mp 
                    INNER JOIN stock_move sm ON  mp.id = sm.raw_material_production_id
                    INNER JOIN mrp_bom mb ON mp.bom_id = mb.id
                    INNER JOIN product_template ptmb ON mb.product_tmpl_id = ptmb.id
                    INNER JOIN product_product ppsm ON sm.product_id = ppsm.id
                    INNER JOIN product_template ptsm ON ppsm.product_tmpl_id = ptsm.id AND ptsm.id IN """ + f"{self.convert_models_to_ids(ingredient_id)}" + """
                    INNER JOIN product_product ppmp ON mp.product_id = ppmp.id
                    INNER JOIN product_template ptmp ON ppmp.product_tmpl_id = ptmp.id
                    INNER JOIN product_category pcmp ON ptmp.categ_id = pcmp.id AND pcmp.id IN """ + f"{self.convert_models_to_ids(category_id)}" + """
                    INNER JOIN res_company rcmp ON ptmp.company_id = rcmp.id AND rcmp.id = """ + f"{company_id.id}" + """
                    INNER JOIN mrp_department mdmp ON ppmp.mrp_dep_id = mdmp.id AND mdmp.id = """ + f"{departament_id.id}" + """
                    INNER JOIN production_unit pump ON mp.prod_unit_id = pump.id 
                    INNER JOIN l10n_cu_mrp_commercialization  AS  lc ON mb.forma_c =lc.id AND lc.id = """ + f"{commercialization_id.id}" + """
                    INNER JOIN mrp_bom_line bl ON mb.id = bl.bom_id
                    INNER JOIN product_product ppbl ON bl.product_id = ppbl.id AND ppbl.id=ppsm.id
                    INNER JOIN product_template ptbl ON ppbl.product_tmpl_id = ptbl.id
                    INNER JOIN uom_uom  AS  uu ON sm.product_uom =uu.id
                    INNER JOIN uom_uom  AS  uo ON bl.product_uom_id =uo.id
                    WHERE mp.state='done' OR mp.state='confirmed'
                    AND mp.date_planned_start <='""" + str(f2) + """'
                    AND mp.date_planned_start >= '""" + str(f1) + """' ) AS t0
                    GROUP BY t0.nombre_comp,t0.nombre_prod_unit,t0.prod_categ,t0.nombre_ingrediente

                    """
        print(query_init)
        self.flush()
        self.env.cr.execute(query_init)
        matrix_data = self.env.cr.fetchall()

        s = max_level[0][0]
        for i in range(max_level[0][0]):  # recorrer por level
            for j in range(len(x_prod_unit)):  # recorrer unidad (lvl)
                if x_prod_unit[j][1] == s:
                    datos_padre = []
                    for m in range(len(matrix_data)):  # recorrer datos para la unidad
                        if x_prod_unit[j][0] == matrix_data[m][1]:
                            datos_padre.append(matrix_data[m])  # datos para la unidad
                    datos_hijo = []
                    for k in range(len(x_padre_prod_unit)):  # recorrer hijos de cada unidad (lvl)
                        if x_prod_unit[j][0] == x_padre_prod_unit[k][2]:
                            for m in range(len(matrix_data)):  # recorrer datos para el hijo unidad
                                if x_padre_prod_unit[k][0] == matrix_data[m][1]:
                                    x1_hijo = (
                                        matrix_data[m][0], x_padre_prod_unit[k][2], matrix_data[m][2],
                                        matrix_data[m][3],
                                        matrix_data[m][4], matrix_data[m][5], matrix_data[m][6], matrix_data[m][7],
                                        matrix_data[m][8], matrix_data[m][9], matrix_data[m][10])
                                    # print("x1_hijo :",x1_hijo)
                                    datos_hijo.append(x1_hijo)  # recorrer datos para el hijo unidad
                    matrix_data += datos_hijo
            s -= 1
        matrix_sql = ""
        count = 0
        for mat in matrix_data:
            matrix_sql += f"{mat}"
            count += 1
            if count < len(matrix_data):
                matrix_sql += f","
        sql = ""
        t1 = ""
        if len(matrix_sql) > 0:
            sql = """SELECT t0.dato0 AS nombre_comp,t0.dato1 AS nombre_prod_unit,t0.dato2 AS prod_categ,t0.dato3 AS nombre_ingrediente, AVG(t0.dato4) AS indice_consumo,AVG(t0.dato5) AS indice_consumo_plan,SUM(t0.dato6) AS consumo_real, SUM(t0.dato7)AS consumo_plan, (SUM(t0.dato6) - SUM(t0.dato7)) AS exceso,(SUM(t0.dato6) /nullif(SUM(t0.dato7),0)*100) AS cumplimiento ,SUM(t0.dato10) AS produccion FROM
                    (SELECT t1.dato0,t1.dato1,t1.dato2,t1.dato3,t1.dato4,t1.dato5,t1.dato6,t1.dato7,t1.dato8,t1.dato9,t1.dato10 
                    FROM (VALUES """ + matrix_sql + """)
                    t1(dato0,dato1,dato2,dato3,dato4,dato5,dato6,dato7,dato8,dato9,dato10)) AS t0
                    GROUP BY nombre_comp,nombre_prod_unit,prod_categ,nombre_ingrediente
                    ORDER BY nombre_prod_unit
                    """
            t1 = """SELECT t5.prod_categ,t5.nombre_prod_unit, SUM(t5.produccion) FROM
                    (SELECT t1.prod_categ,t1.nombre_prod_unit,t1.produccion FROM
                    (""" + sql + """) AS t1
                    GROUP BY t1.prod_categ,t1.nombre_prod_unit,t1.produccion) AS t5
                    GROUP BY t5.prod_categ,t5.nombre_prod_unit
                    """
            t2 = """SELECT t5.nombre_prod_unit, SUM(t5.produccion) FROM
                                (SELECT t1.nombre_prod_unit,t1.produccion FROM
                                (""" + sql + """) AS t1
                                GROUP BY t1.nombre_prod_unit,t1.produccion) AS t5
                                GROUP BY t5.nombre_prod_unit
                                """
        matrix_docs = []
        docs_categ = []
        docs_prod = []
        if len(sql) > 0:
            self.flush()
            self.env.cr.execute(sql)
            matrix_docs = self.env.cr.fetchall()

            self.flush()
            self.env.cr.execute(t1)
            docs_categ = self.env.cr.fetchall()

            self.flush()
            self.env.cr.execute(t2)
            docs_prod = self.env.cr.fetchall()

        docs = []
        docs_unit = []
        conj_unit = []
        for unit in prod_unit_id:
            for prd in docs_prod:
                if prd[0] == unit.name:
                    conj_unit.append(prd)
            docs_unit.append(unit.name)
        for j in range(len(matrix_docs)):
            if matrix_docs[j][1] in docs_unit:
                docs.append(matrix_docs[j])
        comp = self.env.ref('base.main_company')
        return {
            'description': self._description,
            'company_id': comp,
            'icon': comp.logo,
            'docids': docids,
            'docmodel': data['model'],
            'commercialization_id': commercialization_id,
            'data': docs,
            'docs_unit': conj_unit,
            'docs_categ': docs_categ,
            'date': date,
            'start': start,
            'end': end,
        }
