from odoo import fields, models, api


class ResOrganism (models.Model):
    _name = 'res.organism'
    _description = 'Organism'
    _order = 'code'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', help='', required=True)
    short_name = fields.Char('Short Name')
    active = fields.Boolean('Active', default=True)
    


