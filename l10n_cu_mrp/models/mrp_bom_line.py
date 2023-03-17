from odoo import fields, models, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    promedio = fields.Float(string='%', help='Percent',
                            digits='Product Unit of Measure',
                            default=0, required=True)
    indice_consumo = fields.Float(string='IC', help='Index of Consumption',
                                  digits='Index of Consumption', default=0,
                                  required=True)
    standard_price = fields.Float('Standard Price',store=True, related='product_id.standard_price',
                                  digits='Product Unit of Measure', default=0)
    total_importe = fields.Float('Care Total', digits='Product Unit of Measure',
                                 compute='get_total_importe',
                                 default=0)

    @api.depends('product_id', 'product_qty', 'product_uom_id')
    def get_total_importe(self):
        for t in self:
            quantity = 0
            if t.product_uom_id:
                print("calculo  "+str(t.product_uom_id.name)+"  "+str(t.product_qty)+"   "+str(t.product_id.product_tmpl_id.uom_id.name))
                quantity = t.product_uom_id._compute_quantity(qty=t.product_qty,
                                                              to_unit=t.product_id.product_tmpl_id.uom_id,
                                                              raise_if_failure=False)
                print("calculo  cantidad :" +str(quantity)+"   precio :"+str(t.standard_price))
            t.total_importe = t.standard_price * quantity
        return
