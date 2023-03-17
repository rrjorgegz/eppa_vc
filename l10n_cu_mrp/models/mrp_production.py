# -*- coding: utf-8 -*-
from builtins import print

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    produccion = fields.Float(string='Production',
                              digits='Product Unit of Measure', default=0)
    weight = fields.Float(string='Weight', related='product_tmpl_id.weight', digits='Product Unit of Measure',
                          default=0)
    total = fields.Float(string='Cost of Production', default=0, digits='Product Unit of Measure', required=True)


    @api.onchange('produccion')
    def get_product_qty(self):
        if self.weight > 0:
            self.product_qty = self.produccion / self.weight
        return

    @api.onchange('product_qty', 'product_uom_id')
    def get_produccion(self):
        self.produccion = self.weight * self.product_uom_id._compute_quantity(qty=self.product_qty,
                                                                              to_unit=self.product_uom_id,
                                                                              raise_if_failure=False)
        return

    @api.constrains('bom_id', 'product_uom_id', 'produccion', 'product_uom_qty', 'move_raw_ids')
    @api.constrains('bom_id', 'product_uom_id', 'produccion', 'product_uom_qty', 'move_raw_ids')
    def move_raw_ids_calculate(self):
        if self.state == 'draft':
            self.total = 0
            for bol in self.move_raw_ids:
                line_bom = self.bom_id
                if self.bom_id.mrp_bom_id:
                    line_bom = self.bom_id.mrp_bom_id
                for rec in line_bom.bom_line_ids:
                    if (rec.product_tmpl_id.name == bol.product_id.name):
                        bol.consumo_plan = 0
                        aux = 0
                        if self.bom_id.produccion > 0:
                            aux = rec.product_qty / self.bom_id.produccion
                        bol.consumo_plan = self.produccion * aux
                        bol.indice_consumo_plan = rec.indice_consumo
                    bol.indice_consumo = 0
                    if self.produccion > 0:
                        bol.indice_consumo = bol.product_uom_qty / self.produccion
                    aux2 = 0
                    if bol.consumo_plan > 0:
                        aux2 = bol.product_uom_qty / bol.consumo_plan
                    bol.porciento = aux2 * 100
                    self.total = self.total + bol.total_cost
