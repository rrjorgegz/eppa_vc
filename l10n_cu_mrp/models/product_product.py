from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mrp_dep_id = fields.Many2one('mrp.department', string='Mrp Department',default=lambda self: self.env.user.mrp_dep_id)

