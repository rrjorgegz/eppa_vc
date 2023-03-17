from odoo import fields, models, api


class Commercialization (models.Model):
    _name = 'l10n_cu_mrp.commercialization'
    _description = 'Form of Commercialization'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, size=3)
    currency_id = fields.Many2one('res.currency', 'Currency',default=70, groups="base.group_multi_currency",
                                  required=True)
    _sql_constraints = [
        ('currency_id_uniq', 'unique (currency_id)', 'The Form of Commercialization must be unique!')
    ]


