from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env.user.prod_unit_id)
    prod_unit_id = fields.Many2one('production.unit', string='Production Unit',default=lambda self: self.env.user.prod_unit_id)
    mrp_dep_id = fields.Many2one('mrp.department', string='Mrp Department',default=lambda self: self.env.user.mrp_dep_id)
