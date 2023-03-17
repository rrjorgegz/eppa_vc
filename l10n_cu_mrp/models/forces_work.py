# -*- coding: utf-8 -*-
from docutils.nodes import field

from odoo import api, fields, models, _


class ForcesWork(models.Model):
    _name = 'l10n_cu_mrp.forces_work'
    _description = "Forces of Work"

    name = fields.Char('Reference', compute='get_name', store=True)
    company_id = fields.Many2one('res.company', string='Companies', default=lambda self: self.env.user.company_id,
                                 required=True)
    mrp_bom_id = fields.Many2one('mrp.bom', string='Bill of Material', store=True, required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', store=True,
                                      related='mrp_bom_id.product_tmpl_id')
    salario_id = fields.Many2one('l10n_cu_mrp.wage_worker', string='Wage of the Worker', help='Wage of the Worker',
                                 ondelete='cascade')
    job = fields.Many2one('hr.job', string='Job Position', domain="[('company_id', '=', company_id)]", required=True)
    cant_trabajadores = fields.Integer('Quantity of Workers', default=0, required=True,
                                       help='Quantity of Workers for the elaboration of a product')
    category = fields.Many2one('l10n_cu_hr.occupational_category', string='Occupational Category',
                               help='Category of the worker s position', related='job.category_id')
    grupo_escala = fields.Many2one('l10n_cu_hr.scale_group', 'Scale Group', help='Scale Group of the worker',
                                   related='job.scale_group_id',store=True)
    salario_hora = fields.Float('Wage/Hour', digits='Product Unit of Measure', default=0,
                                help='Wage/Hour for the elaboration of a product',
                                related='job.scale_group_id.hourly_rate',store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='mrp_bom_id.forma_c.currency_id',
                                  groups="base.group_multi_currency")
    norma_tiempo = fields.Integer('Norma of Time (h)', default=0,
                                related='job.scale_group_id.hour',store=True,
                                help='Norma of Time (h) for the elaboration of a product')
    gasto_salario = fields.Float('Expense Wage', digits='Product Unit of Measure', compute='_compute_gasto_salario',
                                 help='Expense Wage in the Force of Work')



    @api.depends('salario_hora','norma_tiempo','cant_trabajadores','currency_id')
    def _compute_gasto_salario(self):
        for rec in self:
            rec.gasto_salario = rec.salario_hora * rec.norma_tiempo * rec.cant_trabajadores * rec.currency_id.rounding

    @api.depends('product_tmpl_id')
    def get_name(self):
        self.name = "FT/"
        if self.ids:
            self.name = "FT/" + str(self.ids)
        return
