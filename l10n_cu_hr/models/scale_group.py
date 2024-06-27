from odoo import fields, models


class ScaleGroup(models.Model):
    _name = "l10n_cu_hr.scale_group"
    _description = "Scale Group"

    name = fields.Char("Name", required=1)
    hour = fields.Integer(string="Hour", required=1, default=8)
    salary = fields.Float(string="Salary", required=1, digits="Hr/Salario")
    hourly_rate = fields.Float(string="Hourly Rate", required=1, digits="Hr/Salario")
    currency = fields.Many2one("res.currency", "Currency", required=1, groups="base.group_multi_currency", readonly=False, default=70)

    _sql_constraints = [("name_uniq", "unique (name)", "The name of the Scale Group must be unique!")]
