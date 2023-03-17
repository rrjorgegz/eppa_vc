from odoo import fields, models, api


class MrpDepartment(models.Model):
    _name = 'mrp.department'
    _description = 'Mrp Despartment'

    name = fields.Char('Name', required=True)

    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', 'The name of Mrp Despartment must be unique!')
    # ]

