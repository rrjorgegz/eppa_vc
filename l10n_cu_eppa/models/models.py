# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class l10n_cu_eppa_report(models.Model):
#     _name = 'l10n_cu_eppa_report.l10n_cu_eppa_report'
#     _description = 'l10n_cu_eppa_report.l10n_cu_eppa_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
