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

    def get_mrp_prods_ids_from_prod_unit(self,prod_unit_main,filters):
        mrp_prods_ids = []
        mrp_prods_ids = mrp_prods_ids + self.env['mrp.production'].search([("prod_unit_id","=",prod_unit_main.id)]).ids
        for child in prod_unit_main.child_ids:
            if len(child.child_ids) > 0:
                mrp_prods_ids = mrp_prods_ids + self.get_mrp_prods_ids_from_prod_unit(child, filters)
            else:
                mrp_prods_ids = mrp_prods_ids + self.env['mrp.production'].search([("prod_unit_id","=",child.id)]).ids
        return mrp_prods_ids

    def get_array_unit_mrp_prod_from_prod_unit(self, prod_unit_main, filters):
        array_unit = []
        aux={}
        aux["prod_unit_id"]=prod_unit_main.id
        aux["mrp_prod"]=self.get_mrp_prods_ids_from_prod_unit(prod_unit_main, filters)
        array_unit.append(aux)
        for child in prod_unit_main.child_ids:
            if len(child.child_ids) > 0:
                array_unit = array_unit + self.get_array_unit_mrp_prod_from_prod_unit(child, filters)
            else:
                array_unit.append({"prod_unit_id": child.id,"mrp_prod": self.get_mrp_prods_ids_from_prod_unit(child, filters)})
        return array_unit

    def get_info_prod_unit(self,mrp_produccion_unit_prod):
        # obtener las operaciones de todas las unidades
        result= []
        for punit in mrp_produccion_unit_prod:
            result.append(self.get_info_per_prod_unit(punit))
        return result

    def get_info_per_prod_unit(self,unit_data):
        result = []
        # obtener las operaciones de cada unidad
        prod_unit_main = self.env['production.unit'].search([('id', '=', unit_data["prod_unit_id"])])
        mrp_prods = self.env['mrp.production'].search([('id', 'in', unit_data["mrp_prod"])])
        # organizar por productos
        # 1 - cuantos productos diferentes tiene este grupo de produciones
        productos_ids = self.get_productos_from_mrp_prod(mrp_prods)
        produccion_kg = 0
        for d in productos_ids :
            # 2 - agrupar producciones por productos
            aux_mrp_prods = self.env['mrp.production'].search([('id', 'in', unit_data["mrp_prod"]),('product_id', '=', d.id)])
            # 2.1 - obtener todos los ingredientes de esas producciones agrupadas por productos
            move_raw_ids = []
            for x1 in aux_mrp_prods:
                move_raw_ids += x1.move_raw_ids
            # 3 - agrupar ingredientes
            # 3.1 - obtener todos los ingredientes que se encuentran en el grupo de ingredientes
            ingredientes_ids = self.get_ingredientes_in_move_raw_ids(move_raw_ids)
            # 3.2 - agrupar move_raw_ids por ingredientes
            raw_ingredient = []
            for x2 in ingredientes_ids:
                raw_ing = self.env['stock.move'].search([('id', 'in', move_raw_ids.ids), ('product_id', '=', x2.id)])
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

                    count +=1
                # 3 - calcular los datos por ingredientes
                ic = sum(indice_consumo)/len(indice_consumo)
                icp = sum(indice_consumo_plan)/len(indice_consumo_plan)
                co = sum(consumo)
                cop = sum(consumo_plan)
                exc = sum(consumo) - sum(consumo_plan)
                cum = sum(consumo) / sum(consumo_plan) *100
                raw_ingredient.append({"ing":x2,"indice_consumo":ic,"indice_consumo_plan":icp,"consumo":co,"consumo_plan":cop,"exceso":exc,"cumplido":cum})
            produccion_kg += d.product_qty
            result.append({"unit":prod_unit_main,"produccion":produccion_kg,"raw":raw_ingredient})
        return result

    def get_ingredientes_in_move_raw_ids(self,move_raw_ids):
        ingredientes_id = []
        for x2 in move_raw_ids:
            if not x2.product_id in ingredientes_id:
                ingredientes_id.append(x2.product_id)
        return ingredientes_id

    def get_productos_from_mrp_prod(self,prod):
        productos_id = []
        for p1 in prod:
            if not p1.product_id in productos_id:
                productos_id.append(p1.product_id)
        return  productos_id
        # return  self.env['product.product'].search([('id', 'in', productos_id)])

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        filters = {}
        date = datetime.strptime(data['form']['date'], DATE_FORMAT).date()
        start = datetime.strptime(data['form']['start'], DATE_FORMAT).date()
        end = datetime.strptime(data['form']['end'], DATE_FORMAT).date()
        f1 = datetime(year=start.year, month=start.month, day=start.day, tzinfo=None)
        f2 = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999,
                      tzinfo=None)
        filters["start"] = f1
        filters["end"] = f2
        company_id = self.env['res.company'].search([('id', '=', data['form']['company_id'])])
        filters["company_id"] = company_id
        is_product = str(data['form']['is_product'])
        product_id = self.env['product.template'].search([])
        if is_product == 'uno':
            product_id = self.env['product.template'].search([('id', '=', data['form']['product_tmpl_id'])])
        filters["product_id"] = product_id
        is_ingredient = str(data['form']['is_ingredient'])
        ingredient_tmpl_id = self.env['product.category'].search([])
        if is_ingredient == 'uno':
            ingredient_tmpl_id = self.env['product.category'].search([('id', '=', data['form']['ingredient_tmpl_id'])])
        filters["ingredient_tmpl_id"] = ingredient_tmpl_id
        is_todos_prod_unit = str(data['form']['is_todos_prod_unit'])
        prod_unit_id = self.env['production.unit'].search([])
        if is_todos_prod_unit == 'uno':
            prod_unit_id = self.env['production.unit'].search([('id', '=', data['form']['prod_unit_id'])])
        filters["prod_unit_id"] = prod_unit_id
        commercialization_id = self.env['l10n_cu_mrp.commercialization'].search(
            [('id', '=', data['form']['commercialization_id'])])
        filters["commercialization_id"] = commercialization_id
        departament_id = self.env['mrp.department'].search([('id', '=', data['form']['departament_id'])])
        filters["departament_id"] = departament_id
        aux_unit = self.env['production.unit'].search([("id","in",prod_unit_id.ids)], order="level asc", limit=1)
        mrp_produccion_unit_prod = self.get_array_unit_mrp_prod_from_prod_unit(aux_unit,filters)
        docs = self.get_info_prod_unit(mrp_produccion_unit_prod)
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
