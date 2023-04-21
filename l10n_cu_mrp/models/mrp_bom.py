from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    weight = fields.Float('Weight', related='product_tmpl_id.weight', digits='Product Unit of Measure')
    produccion = fields.Float('Production', default=0, digits='Product Unit of Measure')
    forma_c = fields.Many2one('l10n_cu_mrp.commercialization', string='Commercialization',
                              help='Form of Commercialization', index=1, required=True)
    total = fields.Float(string='Cost', default=0, digits='Product Unit of Measure', required=True)
    metodo = fields.Selection([('directo', 'Direct'), ('none', 'None')], 'Method', default="directo", required=True)
    descripcion = fields.Text('Description')
    salario_count = fields.Integer('# Labor Wage', compute='_compute_salario_obrero_count', compute_sudo=False)
    concepto_count = fields.Integer('# Concept of Expenses', compute='_compute_concepto_gastos_count',
                                    compute_sudo=False)
    confeccionado_por = fields.Many2one('hr.employee', string='Made for')
    aprobado_por = fields.Many2one('hr.employee', string='Approved for')
    mrp_dep_id = fields.Many2one('mrp.department', string='Mrp Department',default=lambda self: self.env.user.mrp_dep_id)

    def _compute_salario_obrero_count(self):
        for salario in self:
            salario.salario_count = 0
            if salario.id:
                salario.salario_count = self.env[
                    'l10n_cu_mrp.wage_worker'].search_count(
                    [('mrp_bom_id', '=', salario.id)])

    def _compute_concepto_gastos_count(self):
        for concepto in self:
            concepto.concepto_count = 0
            if concepto.id:
                concepto.concepto_count = self.env[
                    'l10n_cu_mrp.concept_expenses'].search_count(
                    [('mrp_bom_id', '=', concepto.id)])

    @api.onchange('product_qty', 'product_uom_id', 'product_tmpl_id', 'weight')
    def get_production(self):
        self.produccion = self.product_uom_id._compute_quantity(qty=self.product_qty,
                                                                to_unit=self.product_uom_id,
                                                                raise_if_failure=False) * self.weight
        return

    @api.onchange('weight', 'produccion')
    def get_product_qty(self):
        self.product_qty = 0
        if self.weight > 0:
            self.product_qty = self.produccion / self.weight
        return

    @api.constrains('bom_line_ids')
    def get_total(self):
        for t in self:
            aux = 0
            for rec in t.bom_line_ids:
                aux = aux + rec.total_importe
            t.total = aux
        return

    # @api.onchange('bom_line_ids', 'produccion')
    # def bom_line_(self):
    #     for rec in self.bom_line_ids:
    #         rec.indice_consumo = 0
    #         if self.produccion > 0:
    #             rec.indice_consumo = rec.product_uom_id._compute_quantity(qty=rec.product_qty,
    #                                                                       to_unit=rec.product_uom_id,
    #                                                                       raise_if_failure=False) / self.produccion
    #     return
