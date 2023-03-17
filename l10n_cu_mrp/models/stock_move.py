# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    indice_consumo = fields.Float(string='IC', help='Index of Consumption Real',
                                  digits='Index of Consumption', default=0, required=True)
    indice_consumo_plan = fields.Float(string='IC PLAN', help='Index of Consumption Plan',
                                       digits='Index of Consumption', default=0, required=True)
    consumo_plan = fields.Float(string='Consumption PLAN', help='Consumption Plan',
                                digits='Product Unit of Measure', default=0, required=True)
    cost = fields.Float('Cost per unit', help='Cost per unit of the Product',
                        default=lambda self: self.product_id.standard_price,
                        digits='Product Unit of Measure', required=True)
    total_cost = fields.Float('Total Cost per unit', help='Total cost of the weight of the Product', default=0,
                              store=True, compute='get_total_cost', digits='Product Unit of Measure')
    porciento = fields.Float(string='%', help='Percent', digits='Product Unit of Measure', default=0)

    @api.depends('product_id', 'product_uom', 'product_qty')
    def get_total_cost(self):
        for t in self:
            t.total_cost = t.product_id.uom_id._compute_quantity(qty=t.product_uom_qty, to_unit=t.product_uom,
                                                                       raise_if_failure=False) * t.cost
        return
