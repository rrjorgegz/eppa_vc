# -*- coding: utf-8 -*-
# from odoo import http


# class L10nCuMrp(http.Controller):
#     @http.route('/l10n_cu_mrp/l10n_cu_mrp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cu_mrp/l10n_cu_mrp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cu_mrp.listing', {
#             'root': '/l10n_cu_mrp/l10n_cu_mrp',
#             'objects': http.request.env['l10n_cu_mrp.l10n_cu_mrp'].search([]),
#         })

#     @http.route('/l10n_cu_mrp/l10n_cu_mrp/objects/<model("l10n_cu_mrp.l10n_cu_mrp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cu_mrp.object', {
#             'object': obj
#         })
