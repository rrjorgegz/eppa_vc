from odoo import api, fields, models


class Job(models.Model):
    _inherit = 'hr.job'

    category_id = fields.Many2one('l10n_cu_hr.occupational_category', string='Occupational Category',required=True,)
    scale_group_id = fields.Many2one('l10n_cu_hr.scale_group', string='Scale Group',required=True,)