from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env.user.company_id)
    mrp_dep_id = fields.Many2one('mrp.department', string='Mrp Department',domain=lambda self: [('id', '=', self.env.user.mrp_dep_id.id)],default=lambda self: self.env.user.mrp_dep_id)
