# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class WageWorker(models.Model):
    _name = 'l10n_cu_mrp.wage_worker'
    _description = "Wage of the Worker"

    name = fields.Char('Reference', store=True, compute='get_name', help='Name of the Worker s Wage')
    date = fields.Date(string='Scheduled Date', default=datetime.today(),
                       required=True)
    company_id = fields.Many2one('res.company', string='Companies', required=True,
                                 default=lambda self: self.env.company)
    mrp_bom_id = fields.Many2one('mrp.bom', string='Bill of Material',
                                 domain="[('company_id', '=', company_id)]",
                                 required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', store=True,
                                      related='mrp_bom_id.product_tmpl_id')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True,
                                  related='mrp_bom_id.forma_c.currency_id', groups="base.group_multi_currency")
    fuerza_ids = fields.One2many('l10n_cu_mrp.forces_work', 'salario_id', 'Forces of Work', copy=True)
    total_salario = fields.Float('Total', default=0, digits='Product Unit of Measure', help='Total',
                                 compute='_compute_total_salario')
    a1 = fields.Float('A1',default=0, digits='Product Unit of Measure', help='Volumen de Producción',required=True)
    a2 = fields.Float('A2', store=True, related='mrp_bom_id.product_qty', digits='Product Unit of Measure', help='A2')
    salario_basico = fields.Float('Basic wage', default=0, digits='Product Unit of Measure',
                                  help='Basic wage = Total / a1 * a2', compute='_compute_salario_basico')
    confeccionado_por = fields.Many2one('hr.employee', string='Made for')
    aprobado_por = fields.Many2one('hr.employee', string='Approved for')

    @api.depends('fuerza_ids')
    def _compute_total_salario(self):
        aux = 0
        for rec in self.fuerza_ids:
            aux = aux + rec.gasto_salario
        self.total_salario = aux
        return

    @api.depends('total_salario', 'a1', 'a2')
    def _compute_salario_basico(self):
        for w in self:
            w.salario_basico = 0
            aux=0
            if w.a1 > 0:
                aux = w.total_salario / w.a1
            w.salario_basico = aux * w.a2
        return

    @api.depends('product_tmpl_id')
    def get_name(self):
        self.name = "SO/"
        if self.ids:
            self.name = "SO/" + str(self.ids)
        return
