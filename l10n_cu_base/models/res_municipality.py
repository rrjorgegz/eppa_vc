# -*- coding: utf-8 -*-
from odoo import models, api, fields


class ResCountryMunicipality(models.Model):
    _name = 'l10n_cu_base.res_municipality'
    _description = "Municipality"
    _order = 'code'
    _rec_name = 'name'

    state_id = fields.Many2one('res.country.state', 'State', required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=3,
                       help='The code of the municipality have three characters', required=True)
    country_id = fields.Many2one(
        'res.country', related='state_id.country_id', string='Country', required=True)
    dpa_code = fields.Char('DPA code', compute='_compute_dpa_code', store=True)

    @api.depends('state_id', 'code')
    def _compute_dpa_code(self):
        for municipality in self:
            if municipality.state_id and municipality.code:
                municipality.dpa_code = '%s%s' % (
                    municipality.state_id.code, municipality.code)

    _sql_constraints = [
        ('name_code_uniq', 'unique(state_id, code)',
         'The code of the municipality should be only!')
    ]
