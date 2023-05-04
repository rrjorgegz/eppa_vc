from odoo import fields, models, api


class ProductionUnit(models.Model):
    _name = 'production.unit'
    _description = 'Production Unit'

    name = fields.Char('Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    warehouse_id = fields.Many2many('stock.warehouse', string='Warehouse')
    parent_id = fields.Many2one('production.unit', string='Parent Production Unit')
    child_ids = fields.One2many('production.unit', 'parent_id', string='Child Production Unit')
    level = fields.Integer('Level', store=True, compute='get_level',default=0)

    @api.depends('parent_id.level')
    def get_level(self):
        self.level= False
        for unit in self:
            unit.level = unit.parent_id.level + 1

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of Production Unit must be unique!')
    ]
