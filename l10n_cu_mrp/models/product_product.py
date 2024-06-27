from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    mrp_dep_id = fields.Many2one("mrp.department", string="Mrp Department", domain=lambda self: [("id", "=", self.env.user.mrp_dep_id.id)], default=lambda self: self.env.user.mrp_dep_id)
