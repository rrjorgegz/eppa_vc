# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ConsumptionIndexIngredientsReport(models.AbstractModel):
    _name = "report.l10n_cu_eppa.consumption_index_ingredients"
    _description = "Consumption Index for Ingredients"

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
            aux = self.get_info_per_prod_unit(punit, filters)
            if not aux == {}:
                result.append(aux)
        return result

    def get_info_per_prod_unit(self, unit_data, filters):
        result = {}
        # obtener las operaciones de cada unidad
        prod_unit_main = self.env["production.unit"].search([("id", "=", unit_data["prod_unit_id"])])
        mrp_prods = self.env["mrp.production"].search([("id", "in", unit_data["mrp_prod"])])
        # organizar por productos
        # 1 - cuantos productos diferentes tiene este grupo de produciones
        aux_pdr = self.get_productos_from_mrp_prod(mrp_prods)
        productos_ids = []
        for pdr in aux_pdr:
            if pdr in filters["product_id"]:
                productos_ids.append(pdr)

        raw = []
        for d in productos_ids:
            # 2 - agrupar producciones por productos
            aux_mrp_prods = self.env["mrp.production"].search([("id", "in", unit_data["mrp_prod"]), ("product_id", "=", d.id), ("product_id", "in", filters["product_id"].ids)])
            # 2.1 - obtener todos los ingredientes de esas producciones agrupadas por productos
            move_raw_ids = []
            for x1 in aux_mrp_prods:
                move_raw_ids += x1.move_raw_ids
            raw += move_raw_ids
            # 3 - agrupar ingredientes
            # 3.1 - obtener todos los ingredientes que se encuentran en el grupo de ingredientes
        ingredientes_ids = self.get_ingredientes_in_move_raw_ids(raw)
        # 3.2 - agrupar move_raw_ids por ingredientes
        produ = []

        for ingrediente_group in ingredientes_ids:
            raw_ingredient = {}
            moves_ids = []
            for ingredientes in raw:
                if ingrediente_group == ingredientes.product_id:
                    moves_ids += ingredientes.ids
            raw_ing = self.env["stock.move"].search([("id", "in", moves_ids), ("product_id", "=", ingrediente_group.id)])

            indice_consumo = []
            indice_consumo_plan = []
            consumo = []
            consumo_plan = []
            count = 0
            unit = 0
            produccion_kg = 0
            for x3 in raw_ing:
                if count == 0:
                    unit = x3.product_uom
                aux_qty = x3.product_uom._compute_quantity(x3.product_uom_qty, unit, raise_if_failure=False)
                indice_consumo.append(x3.indice_consumo)
                indice_consumo_plan.append(x3.indice_consumo_plan)
                consumo.append(aux_qty)
                consumo_plan.append(x3.consumo_plan)
                count += 1
                produccion_kg += x3.raw_material_production_id.product_qty
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
                    "produccion": produccion_kg,
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
            result = {"unit": prod_unit_main, "ingredients": produ}
        return result

    def get_ingredientes_in_move_raw_ids(self, move_raw_ids):
        ingredientes_ids = []
        for x2 in move_raw_ids:
            if x2.product_id not in ingredientes_ids:
                ingredientes_ids.append(x2.product_id)
        return ingredientes_ids

    def get_productos_from_mrp_prod(self, prod):
        productos_id = []
        for p1 in prod:
            if p1.product_id not in productos_id:
                productos_id.append(p1.product_id)
        return productos_id
        # return  self.env['product.product'].search([('id', 'in', productos_id)])

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
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
        is_ingredient = str(data["form"]["is_ingredient"])
        ingredient_id = self.env["product.template"].search([])
        if is_ingredient == "uno":
            ingredient_id = self.env["product.template"].search([("id", "=", data["form"]["product_tmpl_id"])])
        filters["ingredient"] = self.env["product.product"].search([("product_tmpl_id", "in", ingredient_id.ids)])
        is_product = str(data["form"]["is_product"])
        product_id = self.env["product.template"].search([])
        if is_product == "uno":
            product_id = self.env["product.template"].search([("id", "=", data["form"]["product_tmpl_id"])])
        filters["product_id"] = self.env["product.product"].search([("product_tmpl_id", "=", product_id.ids)])
        is_todos_prod_unit = str(data["form"]["is_todos_prod_unit"])
        prod_unit_id = self.env["production.unit"].search([])
        if is_todos_prod_unit == "uno":
            prod_unit_id = self.env["production.unit"].search([("id", "=", data["form"]["prod_unit_id"])])
        filters["prod_unit_id"] = prod_unit_id
        commercialization_id = self.env["l10n_cu_mrp.commercialization"].search([("id", "=", data["form"]["commercialization_id"])])
        filters["commercialization_id"] = commercialization_id
        departament_id = self.env["mrp.department"].search([("id", "=", data["form"]["departament_id"])])
        filters["departament_id"] = departament_id
        aux_unit = self.env["production.unit"].search([("id", "in", prod_unit_id.ids)], order="level asc", limit=1)
        mrp_produccion_unit_prod = self.get_array_unit_mrp_prod_from_prod_unit(aux_unit, filters)
        result = []
        for unit1 in mrp_produccion_unit_prod:
            if unit1["prod_unit_id"] in filters["prod_unit_id"].ids:
                aux_mrp_p1 = self.env["mrp.production"].search([("id", "in", unit1["mrp_prod"])])
                unit1["mrp_prod"] = []
                for mrp_p1 in aux_mrp_p1:
                    if mrp_p1.bom_id.forma_c == filters["commercialization_id"] and mrp_p1.bom_id.mrp_dep_id == filters["departament_id"]:
                        unit1["mrp_prod"].append(mrp_p1.id)
                result.append(unit1)
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
