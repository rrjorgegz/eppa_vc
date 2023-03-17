# -*- coding: utf-8 -*-
# from odoo import http


# class L10nCuEppaReport(http.Controller):
#     @http.route('/l10n_cu_eppa_report/l10n_cu_eppa_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cu_eppa_report/l10n_cu_eppa_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cu_eppa_report.listing', {
#             'root': '/l10n_cu_eppa_report/l10n_cu_eppa_report',
#             'objects': http.request.env['l10n_cu_eppa_report.l10n_cu_eppa_report'].search([]),
#         })

#     @http.route('/l10n_cu_eppa_report/l10n_cu_eppa_report/objects/<model("l10n_cu_eppa_report.l10n_cu_eppa_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cu_eppa_report.object', {
#             'object': obj
#         })
