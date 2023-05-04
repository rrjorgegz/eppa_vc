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
    prod_unit_id = fields.Many2one('production.unit', string='Production Unit',
                                   default=lambda self: self.env.user.prod_unit_id, required=True)

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

    @api.constrains('move_raw_ids', 'produccion', 'bom_id')
    def move_raw_ids_consumo_plan(self):
        self.ensure_one()
        for raw in self.move_raw_ids:
                raw.indice_consumo = (raw.product_uom_qty / self.produccion) or 0
                raw.indice_consumo_plan = (self.bom_id.bom_line_ids.search(
                    [('bom_id','=',self.bom_id.id),('product_tmpl_id', '=', raw.product_id.product_tmpl_id.id)], limit=1).indice_consumo) or 0
                raw.consumo_plan = (self.produccion / self.bom_id.produccion) * ((self.bom_id.bom_line_ids.search(
                    [('bom_id','=',self.bom_id.id),('product_tmpl_id', '=', raw.product_id.product_tmpl_id.id)], limit=1).product_qty) or 0)
                raw.porciento = (raw.product_uom_qty / raw.consumo_plan) * 100
                self.total = self.total + raw.total_cost
