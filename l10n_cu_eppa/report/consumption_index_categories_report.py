# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ConsumptionIndexCategoriesReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consumption_index_categories"
    _description = "Consumption Index for Categories"

    def get_mrp_prods_ids_from_prod_unit(self, prod_unit_main, filters):
        mrp_prods_ids = []
        mrp_prods_ids = (
            mrp_prods_ids
            + self.env["mrp.production"]
            .search(
                [
                    ("prod_unit_id", "=", prod_unit_main.id),
                    ("date_planned_start", ">=", filters["start"]),
                    ("date_planned_start", "<=", filters["end"]),
                    ("company_id", "in", filters["company_id"].ids),
                ]
            )
            .ids
        )
        for child in prod_unit_main.child_ids:
            if len(child.child_ids) > 0:
                mrp_prods_ids = mrp_prods_ids + self.get_mrp_prods_ids_from_prod_unit(child, filters)
            else:
                mrp_prods_ids = (
                    mrp_prods_ids
                    + self.env["mrp.production"]
                    .search(
                        [("prod_unit_id", "=", child.id), ("date_planned_start", ">=", filters["start"]), ("date_planned_start", "<=", filters["end"]), ("company_id", "in", filters["company_id"].ids)]
                    )
                    .ids
                )
        return mrp_prods_ids

    def get_array_unit_mrp_prod_from_prod_unit(self, prod_unit_main, filters):
        array_unit = []
        aux = {}
        aux["prod_unit_id"] = prod_unit_main.id
        aux["mrp_prod"] = self.get_mrp_prods_ids_from_prod_unit(prod_unit_main, filters)
        array_unit.append(aux)
        for child in prod_unit_main.child_ids:
            if len(child.child_ids) > 0:
                array_unit = array_unit + self.get_array_unit_mrp_prod_from_prod_unit(child, filters)
            else:
                array_unit.append({"prod_unit_id": child.id, "mrp_prod": self.get_mrp_prods_ids_from_prod_unit(child, filters)})
        return array_unit

    def get_info_prod_unit(self, mrp_produccion_unit_prod, filters):
        # obtener las operaciones de todas las unidades
        result = []
        for punit in mrp_produccion_unit_prod:
            # obtener resultado po cada unidad de produccion
            aux = self.get_info_per_prod_unit(punit, filters)
            if not aux == {}:
                result.append(aux)
        return result

    def get_info_per_prod_unit(self, unit_data, filters):
        result = {}
        # obtener las operaciones de cada unidad
        prod_unit_main = self.env["production.unit"].search([("id", "=", unit_data["prod_unit_id"])])
        mrp_prods = self.env["mrp.production"].search([("id", "in", unit_data["mrp_prod"])])
        # organizar por categoria
        # 1 - cuantos categoria diferentes tiene este grupo de produciones
        aux_pdr = self.get_categorias_from_mrp_prod(mrp_prods)
        categorys_ids = []
        for pdr in aux_pdr:
            # filtrar por categoria
            if pdr in filters["category_id"]:
                categorys_ids.append(pdr)
        categs = []
        for d in categorys_ids:
            # 2 - agrupar producciones por categorys_ids
            p2 = self.env["product.template"].search([("categ_id", "=", d.id)])
            p1 = self.env["product.product"].search([("product_tmpl_id", "in", p2.ids)])
            aux_mrp_prods = self.env["mrp.production"].search([("id", "in", unit_data["mrp_prod"]), ("product_id", "in", p1.ids), ("product_id", "in", filters["ingredient"].ids)])
            # 2.1 - obtener todos los ingredientes de esas producciones agrupadas por productos
            move_raw_ids = []
            produccion_kg = 0
            for x1 in aux_mrp_prods:
                move_raw_ids += x1.move_raw_ids
                produccion_kg += x1.product_qty
            # 3 - agrupar ingredientes
            # 3.1 - obtener todos los ingredientes que se encuentran en el grupo de ingredientes
            ingredientes_ids = self.get_ingredientes_in_move_raw_ids(move_raw_ids)
            # 3.2 - agrupar move_raw_ids por ingredientes
            produ = []

            for ingrediente_group in ingredientes_ids:
                raw_ingredient = {}
                moves_ids = []
                for ingredientes in move_raw_ids:
                    if ingrediente_group == ingredientes.product_id:
                        moves_ids += ingredientes.ids
                raw_ing = self.env["stock.move"].search([("id", "in", moves_ids), ("product_id", "=", ingrediente_group.id)])
                indice_consumo = []
                indice_consumo_plan = []
                consumo = []
                consumo_plan = []
                count = 0
                unit = 0

                for x3 in raw_ing:
                    if count == 0:
                        unit = x3.product_uom
                    aux_qty = x3.product_uom._compute_quantity(x3.product_uom_qty, unit, raise_if_failure=False)
                    indice_consumo.append(x3.indice_consumo)
                    indice_consumo_plan.append(x3.indice_consumo_plan)
                    consumo.append(aux_qty)
                    consumo_plan.append(x3.consumo_plan)
                    count += 1

                # 3 - calcular los datos por ingredientes
                ic = 0
                if len(indice_consumo) > 0:
                    ic = sum(indice_consumo) / len(indice_consumo)
                icp = 0
                if len(indice_consumo_plan) > 0:
                    icp = sum(indice_consumo_plan) / len(indice_consumo_plan)
                co = sum(consumo)
                cop = sum(consumo_plan)
                exc = sum(consumo) - sum(consumo_plan)
                cum = 0
                if len(consumo_plan) > 0:
                    cum = sum(consumo) / sum(consumo_plan) * 100

                # pp = self.env['product.product'].search([('id', '=', ingrediente_group.id)])
                # pt = self.env['product.template'].search([('product_tmpl_id', '=', pp.id)])
                if ingrediente_group in filters["ingredient"]:
                    raw_ingredient = {
                        "ing": ingrediente_group.product_tmpl_id.name,
                        "indice_consumo": ic,
                        "indice_consumo_plan": icp,
                        "consumo": co,
                        "consumo_plan": cop,
                        "exceso": exc,
                        "cumplido": cum,
                    }
                if len(raw_ingredient) > 0:
                    produ.append(raw_ingredient)
            if len(produ) > 0:
                categs.append({"category": d, "produccion": produccion_kg, "produ": produ})
        if len(categs) > 0:
            result = {"unit": prod_unit_main, "raw": categs}
        return result

    def get_ingredientes_in_move_raw_ids(self, move_raw_ids):
        ingredientes_ids = []
        for x2 in move_raw_ids:
            if x2.product_id not in ingredientes_ids:
                ingredientes_ids.append(x2.product_id)
        return ingredientes_ids

    def get_categorias_from_mrp_prod(self, prod):
        categorias_id = []
        for p1 in prod:
            if p1.product_id.product_tmpl_id.categ_id not in categorias_id:
                categorias_id.append(p1.product_id.product_tmpl_id.categ_id)
        return categorias_id

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        # 1 - filtros inicializar y guardar datos
        filters = {}
        date = datetime.strptime(data["form"]["date"], DATE_FORMAT).date()
        start = datetime.strptime(data["form"]["start"], DATE_FORMAT).date()
        end = datetime.strptime(data["form"]["end"], DATE_FORMAT).date()
        f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
        f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999, tzinfo=None)
        filters["start"] = f1
        filters["end"] = f2
        company_id = self.env["res.company"].search([("id", "=", data["form"]["company_id"])])
        filters["company_id"] = company_id
        is_ingredient = str(data["form"]["is_todos"])
        ingredient_id = self.env["product.template"].search([])
        if is_ingredient == "uno":
            ingredient_id = self.env["product.template"].search([("id", "=", data["form"]["product_tmpl_id"])])
        filters["ingredient"] = self.env["product.product"].search([("product_tmpl_id", "in", ingredient_id.ids)])
        is_category = str(data["form"]["is_category"])
        category_id = self.env["product.category"].search([])
        if is_category == "uno":
            category_id = self.env["product.category"].search([("id", "=", data["form"]["category_id"])])
        filters["category_id"] = category_id
        is_todos_prod_unit = str(data["form"]["is_todos_prod_unit"])
        prod_unit_id = self.env["production.unit"].search([])
        if is_todos_prod_unit == "uno":
            prod_unit_id = self.env["production.unit"].search([("id", "=", data["form"]["prod_unit_id"])])
        filters["prod_unit_id"] = prod_unit_id
        commercialization_id = self.env["l10n_cu_mrp.commercialization"].search([("id", "=", data["form"]["commercialization_id"])])
        filters["commercialization_id"] = commercialization_id
        departament_id = self.env["mrp.department"].search([("id", "=", data["form"]["departament_id"])])
        filters["departament_id"] = departament_id
        # 2- Organizar las unidades de Produccion e forma acendente por level
        aux_unit = self.env["production.unit"].search([("id", "in", prod_unit_id.ids)], order="level asc", limit=1)
        # 3- Mrp Production por unidad de Production
        mrp_produccion_unit_prod = self.get_array_unit_mrp_prod_from_prod_unit(aux_unit, filters)
        # 4 - Aplicar filtros
        result = []
        for unit1 in mrp_produccion_unit_prod:
            # Aplicar filtro por unidad de produccion
            if unit1["prod_unit_id"] in filters["prod_unit_id"].ids:
                aux_mrp_p1 = self.env["mrp.production"].search([("id", "in", unit1["mrp_prod"])])
                unit1["mrp_prod"] = []
                for mrp_p1 in aux_mrp_p1:
                    # Aplicar filtro por commercialization o moneda por departament_id
                    if mrp_p1.bom_id.forma_c == filters["commercialization_id"] and mrp_p1.bom_id.mrp_dep_id == filters["departament_id"]:
                        unit1["mrp_prod"].append(mrp_p1.id)
                result.append(unit1)
        # 5- Obtener resultados por unidad de Produccion
        docs = self.get_info_prod_unit(result, filters)
        comp = self.env.ref("base.main_company")
        return {
            "description": self._description,
            "company_id": comp,
            "icon": comp.logo,
            "docids": docids,
            "docmodel": data["model"],
            "commercialization_id": commercialization_id,
            "docs": docs,
            "date": date,
            "start": start,
            "end": end,
        }


#
#
# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.
# from datetime import datetime
# from odoo import fields, models, tools, api
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
# from pytz import timezone
# import io, base64
#
#
# class ConsumptionIndexCategoriesReport(models.AbstractModel):
#     _name = "report.l10n_cu_eppa.consumption_index_categories"
#     _description = "Consumption Index for Categories"
#
#     def convert_models_to_ids(self, models):
#         aux1 = '('
#         aux2 = ''
#         count = 0
#         for x1 in models:
#             count = count + 1
#             aux2 = aux2 + str(x1.id)
#             if count != len(models):
#                 aux2 = aux2 + ','
#         aux1 = aux1 + aux2 + ')'
#         if 0 == len(models):
#             aux1 = "('')"
#         return aux1
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
#         start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
#         end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()
#         f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
#         f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
#                       tzinfo=None)
#         company_id = self.env['res.company'].search([('id', '=', data['form']['company_id'])])
#         is_ingredient = str(data['form']['is_todos'])
#         ingredient_id = self.env['product.template'].search([])
#         if is_ingredient == 'uno':
#             ingredient_id = self.env['product.template'].search([('id', '=', data['form']['product_tmpl_id'])])
#         is_category = str(data['form']['is_category'])
#         category_id = self.env['product.category'].search([])
#         if is_category == 'uno':
#             category_id = self.env['product.category'].search([('id', '=', data['form']['category_id'])])
#         is_todos_prod_unit = str(data['form']['is_todos_prod_unit'])
#         prod_unit_id = self.env['production.unit'].search([])
#         if is_todos_prod_unit == 'uno':
#             prod_unit_id = self.env['production.unit'].search([('id', '=', data['form']['prod_unit_id'])])
#         commercialization_id = self.env['l10n_cu_mrp.commercialization'].search(
#             [('id', '=', data['form']['commercialization_id'])])
#         departament_id = self.env['mrp.department'].search([('id', '=', data['form']['departament_id'])])
#         max_level_prod_unit = """ SELECT MAX(level) FROM  production_unit"""
#         self.flush()
#         self.env.cr.execute(max_level_prod_unit)
#         max_level = self.env.cr.fetchall()
#         padre_prod_unit = """SELECT pu.name,pu1.name AS parent FROM  production_unit pu
#                             INNER JOIN production_unit pu1 ON pu.parent_id = pu1.id"""
#         self.flush()
#         self.env.cr.execute(padre_prod_unit)
#         x_padre_prod_unit = self.env.cr.fetchall()
#
#         all_prod_units = """ SELECT name,level FROM  production_unit"""
#         self.flush()
#         self.env.cr.execute(all_prod_units)
#         x_prod_unit = self.env.cr.fetchall()
#
#         query_init = """SELECT mp.produccion,rcmp.name AS nombre_comp, pcmp.name AS prod_categ, pump.id AS prod_unit_id,pump.name AS nombre_prod_unit, mdmp.name AS nombre_mrp_dep ,ptmp.name AS nombre_production,pcmp.name AS categoria_production,rcmp.name company_production,ptmb.name AS nombre_lista_material,ptsm.id AS ingrediente_id,ptsm.name AS nombre_ingrediente,sm.indice_consumo,bl.indice_consumo AS indice_consumo_plan,sm.product_uom_qty/uu.factor AS product_uom_qty,sm.consumo_plan/uu.factor AS consumo_plan
#                     FROM mrp_production mp
#                     INNER JOIN stock_move sm ON  mp.id = sm.raw_material_production_id
#                     INNER JOIN mrp_bom mb ON mp.bom_id = mb.id
#                     INNER JOIN product_template ptmb ON mb.product_tmpl_id = ptmb.id
#                     INNER JOIN product_product ppsm ON sm.product_id = ppsm.id
#                     INNER JOIN product_template ptsm ON ppsm.product_tmpl_id = ptsm.id AND ptsm.id IN """ + f"{self.convert_models_to_ids(ingredient_id)}" + """
#                     INNER JOIN product_product ppmp ON mp.product_id = ppmp.id
#                     INNER JOIN product_template ptmp ON ppmp.product_tmpl_id = ptmp.id
#                     INNER JOIN product_category pcmp ON ptmp.categ_id = pcmp.id AND pcmp.id IN """ + f"{self.convert_models_to_ids(category_id)}" + """
#                     INNER JOIN res_company rcmp ON ptmp.company_id = rcmp.id AND rcmp.id = """ + f"{company_id.id}" + """
#                     INNER JOIN mrp_department mdmp ON ppmp.mrp_dep_id = mdmp.id AND mdmp.id = """ + f"{departament_id.id}" + """
#                     INNER JOIN production_unit pump ON mp.prod_unit_id = pump.id
#                     INNER JOIN l10n_cu_mrp_commercialization  AS  lc ON mb.forma_c =lc.id AND lc.id = """ + f"{commercialization_id.id}" + """
#                     INNER JOIN mrp_bom_line bl ON mb.id = bl.bom_id
#                     INNER JOIN product_product ppbl ON bl.product_id = ppbl.id AND ppbl.id=ppsm.id
#                     INNER JOIN product_template ptbl ON ppbl.product_tmpl_id = ptbl.id
#                     INNER JOIN uom_uom  AS  uu ON sm.product_uom =uu.id
#                     WHERE mp.state='done' OR mp.state='confirmed'
#                     AND mp.date_planned_start <='""" + str(f2) + """'
#                     AND mp.date_planned_start >= '""" + str(f1) + """'
#                     """
#         t0 = """
#             SELECT t0.nombre_comp,t0.nombre_prod_unit,t0.prod_categ,t0.nombre_ingrediente, AVG(t0.indice_consumo) AS indice_consumo,AVG(t0.indice_consumo_plan) AS indice_consumo_plan,SUM(t0.product_uom_qty) AS consumo_real, SUM(t0.consumo_plan)AS consumo_plan, (SUM(t0.product_uom_qty) - SUM(t0.consumo_plan)) AS exceso,(SUM(t0.product_uom_qty) /nullif(SUM(t0.consumo_plan),0)*100) AS cumplimiento FROM
#             (""" + query_init + """) AS t0
#             GROUP BY t0.nombre_comp,t0.nombre_prod_unit,t0.prod_categ,t0.nombre_ingrediente
#             """
#         print(t0)
#         self.flush()
#         self.env.cr.execute(t0)
#         matrix_data = self.env.cr.fetchall()
#         t1 = """SELECT t5.prod_categ,t5.nombre_prod_unit, SUM(t5.produccion) FROM
#                 (SELECT t1.prod_categ,t1.nombre_prod_unit,t1.produccion FROM
#             (""" + query_init + """) AS t1
#             GROUP BY t1.prod_categ,t1.nombre_prod_unit,t1.produccion) AS t5
# 			GROUP BY t5.prod_categ,t5.nombre_prod_unit
#             """
#         t2 = """SELECT t2.ingrediente_id,t2.nombre_ingrediente FROM
#             (""" + query_init + """) AS t2
#             GROUP BY t2.ingrediente_id,t2.nombre_ingrediente
#             """
#         t3 = """SELECT t3.nombre_prod_unit FROM
#             (""" + query_init + """) AS t3
#             GROUP BY t3.nombre_prod_unit
#             """
#         self.flush()
#         self.env.cr.execute(t3)
#         prod_unit = self.env.cr.fetchall()
#
#         self.flush()
#         self.env.cr.execute(t1)
#         prod_categ = self.env.cr.fetchall()
#
#         t4 = """SELECT t4.nombre_ingrediente FROM
#                    (""" + query_init + """) AS t4
#                    GROUP BY t4.nombre_ingrediente
#                    """
#         self.flush()
#         self.env.cr.execute(t4)
#         x_ingred = self.env.cr.fetchall()
#
#         h, w = len(x_ingred) * len(x_prod_unit) * len(prod_categ), 10
#         matrix = [[f"" for x in range(w)] for y in range(h)]
#         pos = 0
#         for un in x_prod_unit:
#             for ct in prod_categ:
#                 for ig in x_ingred:
#                     indice_consumo = 0
#                     indice_consumo_plan = 0
#                     consumo_real = 0
#                     consumo_plan = 0
#                     exceso = 0
#                     cumplimiento = 0
#                     for matrix_x in matrix_data:
#                         if matrix_x[1] == un[0] and matrix_x[2] == ct[0] and matrix_x[3] == ig[0]:
#                             indice_consumo = matrix_x[4]
#                             indice_consumo_plan = matrix_x[5]
#                             consumo_real = matrix_x[6]
#                             consumo_plan = matrix_x[7]
#                             exceso = matrix_x[8]
#                             cumplimiento = matrix_x[9]
#                     matrix[pos][0] = un[0]
#                     matrix[pos][1] = un[1]
#                     matrix[pos][2] = ct[0]
#                     matrix[pos][3] = ig[0]
#                     matrix[pos][4] = indice_consumo
#                     matrix[pos][5] = indice_consumo_plan
#                     matrix[pos][6] = consumo_real
#                     matrix[pos][7] = consumo_plan
#                     matrix[pos][8] = exceso
#                     matrix[pos][9] = cumplimiento
#                     pos += 1
#         x_level = max_level[0][0]
#         s = x_level
#         orden_matrix = []
#         for j in range(x_level):
#             for i in range(len(matrix)):
#                 if s == matrix[i][1]:
#                     orden_matrix.append(matrix[i])
#             s -= 1
#
#         for j in range(len(orden_matrix)):
#             sum = 0
#             for i in range(len(orden_matrix)):
#                 x1_data = orden_matrix[j][0]
#                 x2_data = self.env['production.unit'].search([('name', '=', orden_matrix[i][0])]).parent_id.name
#                 if x2_data == x1_data and orden_matrix[i][2] == orden_matrix[j][2] and orden_matrix[i][3] == \
#                         orden_matrix[j][3] and orden_matrix[i][4] > 0 and orden_matrix[i][5] > 0 and orden_matrix[i][
#                     6] > 0:
#                     sum += 1
#                     orden_matrix[j][4] += orden_matrix[i][4] / sum
#                     orden_matrix[j][5] = orden_matrix[i][5]
#                     orden_matrix[j][6] += orden_matrix[i][6]
#                     orden_matrix[j][7] += orden_matrix[i][6]
#                     orden_matrix[j][8] = orden_matrix[i][6] - orden_matrix[i][7]
#                     orden_matrix[j][9] = orden_matrix[i][6] / (orden_matrix[i][7] * 100)
#         docs = []
#         docs_unit = []
#         for unit in prod_unit_id:
#             docs_unit.append(unit.name)
#             for j in range(len(orden_matrix)):
#                 if unit.name == orden_matrix[j][0] and orden_matrix[j][6] > 0:
#                     docs.append(orden_matrix[j])
#         docs_categ = []
#         for j in prod_categ:
#             x1 = []
#             x1.append(j[0])
#             x1.append(j[1])
#             docs_categ.append(x1)
#         comp = self.env.ref('base.main_company')
#         return {
#             'description': self._description,
#             'company_id': comp,
#             'icon': comp.logo,
#             'docids': docids,
#             'docmodel': data['model'],
#             'commercialization_id': commercialization_id,
#             'docs': docs,
#             'docs_unit': docs_unit,
#             'docs_categ': docs_categ,
#             'date': date,
#             'start': start,
#             'end': end,
#         }
