from odoo import fields, models, api


class OccupationalCategory (models.Model):
    _name = 'l10n_cu_hr.occupational_category'
    _description = 'Occupational Category'

    name = fields.Char('Name',required=1)
    code = fields.Char('Code',required=1,size=3)
    


