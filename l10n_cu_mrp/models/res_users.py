from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    prod_unit_id = fields.Many2one("production.unit", string="Production Unit")
    prod_unit_ids = fields.Many2many("production.unit", string="Production Units")
    mrp_dep_id = fields.Many2one("mrp.department", string="Mrp Department")
    mrp_dep_ids = fields.Many2many("mrp.department", string="Mrp Departments")
